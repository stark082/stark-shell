#!/usr/bin/env python3
"""Transactional, user-scoped installer for Stark Shell. Standard library only."""
import argparse
import copy
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
SECTIONS = ('left', 'centerBegin', 'center', 'centerEnd', 'right', 'tray')
MISSING = {'__stark_missing__': True}


class Error(RuntimeError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    if path.is_symlink():
        raise Error(f'Refusing symlink target: {path}')
    return path.read_bytes() if path.exists() else None


def guard_destination(path):
    for ancestor in [path, *path.parents]:
        if ancestor.is_symlink():
            raise Error(f'Refusing symlink in managed destination: {ancestor}')


def atomic(path, data, mode=0o600):
    """Replace a file on the same filesystem; never follow a target symlink."""
    guard_destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def load_json(path, default=None):
    data = read(path)
    return copy.deepcopy(default) if data is None else json.loads(data)


def run(args, check=True, timeout=30):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        raise Error(f'Command failed: {" ".join(map(str, args))}\n{result.stderr or result.stdout}')
    return result


def safe_relative(value):
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise Error(f'Unsafe package path: {value}')
    return path


def tree_hashes(path):
    if path.is_symlink():
        raise Error(f'Refusing symlink plugin: {path}')
    if not path.exists():
        return {}
    result = {}
    for p in sorted(path.rglob('*')):
        if p.is_symlink():
            raise Error(f'Refusing symlink: {p}')
        if p.is_file():
            result[str(p.relative_to(path))] = digest(p.read_bytes())
    return result


def diff(before, after, path=()):
    """Arrays are atomic: an edited/reordered widget list is a conflict, not overwritten."""
    changes = []
    if before == MISSING or after == MISSING:
        if before != after:
            changes.append({'path': list(path), 'before': before, 'after': after})
    elif isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(before.keys() | after.keys()):
            changes.extend(diff(before.get(key, MISSING), after.get(key, MISSING), path + (key,)))
    elif before != after:
        changes.append({'path': list(path), 'before': before, 'after': after})
    return changes


def get_at(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return MISSING
        value = value[key]
    return value


def set_at(value, path, new):
    current = value
    for key in path[:-1]:
        current = current.setdefault(key, {})
    if new == MISSING:
        current.pop(path[-1], None)
    else:
        current[path[-1]] = copy.deepcopy(new)


def reverse_changes(current, changes):
    result = copy.deepcopy(current)
    conflicts = []
    for change in changes:
        present = get_at(result, change['path'])
        if present == change['after']:
            set_at(result, change['path'], change['before'])
        elif present != change['before']:
            conflicts.append('/' + '/'.join(change['path']))
    return result, conflicts


class Transaction:
    """Persistent before-images and expected after hashes; interrupted runs are recoverable."""
    def __init__(self, state_dir, name):
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        self.directory = state_dir / 'transactions' / (stamp + '-' + name)
        self.directory.mkdir(parents=True, mode=0o700)
        self.journal = {'status': 'pending', 'files': {}}
        self.flush()

    def flush(self):
        atomic(self.directory / 'journal.json', json_bytes(self.journal))

    def capture(self, path):
        key = str(path)
        if key not in self.journal['files']:
            data = read(path)
            record = {'before': None, 'expected': digest(data) if data is not None else None,
                      'mode': path.stat().st_mode & 0o777 if data is not None else 0o600}
            if data is not None:
                backup = 'before/' + str(len(self.journal['files']))
                atomic(self.directory / backup, data)
                record['before'] = backup
            self.journal['files'][key] = record
            self.flush()

    def observe(self, path):
        data = read(path)
        self.journal['files'][str(path)]['expected'] = digest(data) if data is not None else None
        self.flush()

    def write(self, path, data, mode=0o600):
        guard_destination(path)
        self.capture(path)
        previous = read(path)
        expected = self.journal['files'][str(path)]['expected']
        if (digest(previous) if previous is not None else None) != expected:
            raise Error(f'Concurrent edit detected: {path}')
        if data is None:
            path.unlink(missing_ok=True)
        else:
            atomic(path, data, mode)
        self.observe(path)

    def finish(self):
        self.journal['status'] = 'complete'
        self.flush()

    def rollback(self):
        conflicts = []
        for name, record in reversed(list(self.journal['files'].items())):
            path = Path(name)
            current = read(path)
            if (digest(current) if current is not None else None) != record['expected']:
                conflicts.append(name)
                continue
            if record['before'] is None:
                path.unlink(missing_ok=True)
            else:
                atomic(path, (self.directory / record['before']).read_bytes(), record['mode'])
        self.journal['status'] = 'rollback-conflict' if conflicts else 'rolled-back'
        self.journal['conflicts'] = conflicts
        self.flush()
        return conflicts


class Manager:
    def __init__(self, repo=REPO):
        self.repo = Path(repo)
        self.lock = load_json(self.repo / 'packaging/upstreams.lock.json')
        self.home = Path.home()
        self.config = Path(os.environ.get('XDG_CONFIG_HOME', str(self.home / '.config')))
        if self.config != self.home / '.config':
            raise Error('Omarchy 4.5 plugin commands use ~/.config. Non-default XDG_CONFIG_HOME is not supported.')
        self.state_dir = Path(os.environ.get('XDG_STATE_HOME', str(self.home / '.local/state'))) / 'stark-shell'
        self.state_path = self.state_dir / 'state.json'
        self.plugins = self.config / 'omarchy/plugins'
        self.shell = self.config / 'omarchy/shell.json'
        self.omarchy = Path(os.environ.get('OMARCHY_PATH', '/usr/share/omarchy'))

    def environment(self):
        if sys.version_info < (3, 10):
            raise Error('Python 3.10 or newer is required.')
        required = ['python3', 'omarchy', 'omarchy-shell', 'quickshell', 'hyprctl', 'jq', 'patch']
        missing = [name for name in required if not shutil.which(name)]
        if missing:
            raise Error('Missing required commands: ' + ', '.join(missing) + '. Install Omarchy Quattro and these dependencies first.')
        versions = {name: run(command).stdout.strip() for name, command in {
            'omarchy': ['omarchy', 'version'], 'quickshell': ['quickshell', '--version'],
            'hyprland': ['hyprctl', 'version']}.items()}
        patterns = {'omarchy': r'^4\.5\.\d+(?:-\d+)?$', 'quickshell': r'Quickshell 0\.3\.2\b',
                    'hyprland': r'Hyprland 0\.56\.\d+\b'}
        for name, pattern in patterns.items():
            if not re.search(pattern, versions[name]):
                raise Error(f'Unsupported {name}: {versions[name].splitlines()[0]}. '
                            'This release supports Omarchy 4.5.x, Quickshell 0.3.2 and Hyprland 0.56.x only. See docs/UPDATING.md.')
        for relative, token in {
            'shell/Ui/BarWidget.qml': 'function setting',
            'shell/Commons/Style.qml': 'function duration',
            'shell/services/PluginRegistry.qml': 'clonedFrom',
        }.items():
            path = self.omarchy / relative
            if not path.is_file() or token not in path.read_text():
                raise Error(f'Missing required Omarchy interface: {path} ({token}). See docs/UPDATING.md.')
        run(['omarchy', 'plugin', 'validate', '--help'])
        optional = {name: bool(shutil.which(name)) for name in ['cava', 'fc-cache', 'node', 'shellcheck']}
        print('Versions:', '; '.join(f'{k}={v.splitlines()[0]}' for k, v in versions.items()))
        if not optional['cava']:
            print('Optional CAVA missing: visualizer will use PipeWire peak fallback. No packages will be installed.')
        return {'versions': versions, 'optional': optional}

    def select(self, names):
        selected = []
        def add(name):
            if name not in self.lock['components']:
                raise Error(f'Unknown component: {name}')
            for dependency in self.lock['components'][name]['dependencies']:
                add(dependency)
            if name not in selected:
                selected.append(name)
        for name in names:
            add(name)
        return selected

    def materialize(self, names, output):
        """Rebuild only in staging, reject changed source files instead of guessing at patches."""
        paths = {}
        for name in names:
            component = self.lock['components'][name]
            target = output / component['id']
            target.mkdir(parents=True)
            for relative, record in component['files'].items():
                destination = target / safe_relative(relative)
                if 'overlay' in record:
                    source = self.repo / safe_relative(record['overlay'])
                    data = read(source)
                else:
                    source = self.omarchy / safe_relative(record['source'])
                    data = read(source)
                    if data is None or digest(data) != record['source_sha256']:
                        raise Error(f'Upstream compatibility conflict: {source}. Expected SHA256 {record["source_sha256"]}. '
                                    'Do not force the patch; port and test it against this Omarchy package.')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                if 'patch' in record:
                    run(['patch', '--batch', '--fuzz=0', str(destination),
                         str(self.repo / safe_relative(record['patch']))])
                if digest(destination.read_bytes()) != record['sha256']:
                    raise Error(f'Package hash mismatch: {destination}')
                destination.chmod(0o755 if record.get('executable') else 0o644)
            run(['omarchy', 'plugin', 'validate', target])
            paths[name] = target
        return paths

    def state(self):
        state = load_json(self.state_path, {})
        if state and state.get('schema') != 1:
            raise Error('Unsupported installation-state schema; retain the old installer for recovery.')
        return state

    def verify_owned(self, state):
        for name, record in state.get('components', {}).items():
            path = self.plugins / record['id']
            if tree_hashes(path) != record['files']:
                raise Error(f'User-modified or missing plugin: {path}. Preserve your edits and resolve this conflict before updating/removing.')
        for filename, record in state.get('resources', {}).items():
            data = read(Path(filename))
            if data is None or digest(data) != record['sha256']:
                raise Error(f'User-modified or missing Stark-owned file: {filename}. Retaining your changes.')

    def replace_plugin(self, txn, target, source):
        """Publish a complete staged tree; never expose a mixture of old/new QML files."""
        guard_destination(target)
        before = tree_hashes(target)
        after = tree_hashes(source)
        paths = sorted(before.keys() | after.keys())
        for relative in paths:
            txn.capture(target / relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix='.stark-stage-', dir=target.parent))
        old = temporary.with_name(temporary.name + '-old')
        published = False
        try:
            shutil.copytree(source, temporary, dirs_exist_ok=True)
            # Recheck immediately before publishing, so editor changes are not discarded.
            if tree_hashes(target) != before:
                raise Error(f'Concurrent plugin edit: {target}')
            if target.exists():
                target.rename(old)
            try:
                temporary.rename(target)
                published = True
            except BaseException:
                if old.exists():
                    old.rename(target)
                raise
        finally:
            if published:
                for relative in paths:
                    txn.observe(target / relative)
            if temporary.exists():
                shutil.rmtree(temporary)
            if old.exists():
                shutil.rmtree(old)

    def native(self, txn, command):
        """The native command owns shell.json serialization. Back up and audit its changes."""
        txn.capture(self.shell)
        expected = txn.journal['files'][str(self.shell)]['expected']
        current = read(self.shell)
        if (digest(current) if current is not None else None) != expected:
            raise Error('shell.json changed during installation. Retry after finishing desktop edits.')
        try:
            result = run(command, check=False)
        finally:
            txn.observe(self.shell)
        load_json(self.shell, {})
        if result.returncode:
            raise Error(f'Native command failed: {command}\n{result.stderr or result.stdout}')

    def discover(self, ids):
        run(['omarchy-shell', 'shell', 'rescanPlugins'])
        for _ in range(40):
            data = json.loads(run(['omarchy', 'plugin', 'list', '--json']).stdout)
            if set(ids) <= {item['id'] for item in data}:
                return
            time.sleep(0.1)
        raise Error('Omarchy did not discover the staged plugin copies. Check shell logs; transaction will roll back.')

    def reload(self, shell=False, hypr=False):
        if hypr:
            run(['hyprctl', 'reload'])
            errors = run(['hyprctl', 'configerrors']).stdout.strip()
            if errors:
                raise Error('Hyprland rejected the override: ' + errors)
        if shell:
            run(['omarchy', 'restart', 'shell'], timeout=60)

    def preflight_existing(self, state, names):
        self.verify_owned(state)
        for name in names:
            id_ = self.lock['components'][name]['id']
            target = self.plugins / id_
            guard_destination(target)
            if name not in state.get('components', {}) and (target.exists() or target.is_symlink()):
                raise Error(f'Existing unmanaged plugin: {target}. It belongs to your prototype or another installer. '
                            'It will not be adopted or overwritten. Use a fresh account/VM or manually relocate it after backing it up.')

    def install(self, args, updating=False):
        environment = self.environment()
        previous = self.state()
        args.animations = args.animations or previous.get('options', {}).get('animations', False)
        args.fonts = args.fonts or previous.get('options', {}).get('fonts', False)
        names = self.select(args.components.split(',') if args.components else
                            list(previous.get('components', {})) if previous else ['visualizer'])
        names = self.select(list(previous.get('components', {})) + names)
        if updating and not previous:
            raise Error('Nothing managed by Stark Shell is installed. Run install.sh first.')
        self.preflight_existing(previous, names)
        print('Components:', ', '.join(names))
        print('Method: validated managed copies; stock bar retained unless island is selected.')
        resources = {}
        if args.animations:
            hypr_config = self.config / 'hypr/hyprland.lua'
            if not hypr_config.exists() or hypr_config.is_symlink():
                raise Error('Animation module requires a regular ~/.config/hypr/hyprland.lua. Convert/adapt manually; no legacy config rewrite is performed.')
            resources[str(self.config / 'hypr/stark-shell-animations.lua')] = self.repo / 'hypr/stark-animations.lua'
        if args.fonts:
            if not environment['optional']['fc-cache']:
                raise Error('--fonts requires fc-cache. Install fontconfig first.')
            font_lock = load_json(self.repo / 'packaging/fonts.lock.json')
            for name, expected in font_lock['files'].items():
                source = self.repo / 'fonts/ShantellSans' / safe_relative(name)
                if digest(source.read_bytes()) != expected:
                    raise Error(f'Font asset hash mismatch: {source}')
                resources[str(self.home / '.local/share/fonts/stark-shell' / source.name)] = source
        for name in resources:
            guard_destination(Path(name))
            if Path(name).exists() and name not in previous.get('resources', {}):
                raise Error(f'Refusing existing unmanaged resource: {name}')
        # Staging and pure manifest validation happen before writing any desktop files.
        with tempfile.TemporaryDirectory(prefix='stark-shell-stage-') as temporary:
            staged = self.materialize(names, Path(temporary))
            for name in names:
                id_ = self.lock['components'][name]['id']
                print(f'  {id_} -> {self.plugins / id_}')
            for target in resources:
                print('  optional resource ->', target)
            if args.dry_run:
                print('Dry run complete. No configuration, plugin, font, or installation-state files changed.')
                return
            run(['omarchy-shell', 'shell', 'ping'])
            self.ensure_no_pending()
            txn = Transaction(self.state_dir, 'update' if updating else 'install')
            before = load_json(self.shell, {})
            state = copy.deepcopy(previous) if previous else {'schema': 1, 'components': {}, 'resources': {},
                                                             'shell_changes': [], 'hypr_block': None,
                                                             'shell_existed': self.shell.exists(),
                                                             'shell_mode': self.shell.stat().st_mode & 0o777 if self.shell.exists() else 0o600}
            changed = False
            hypr_changed = False
            fonts_changed = False
            try:
                for name, stage in staged.items():
                    id_ = self.lock['components'][name]['id']
                    target = self.plugins / id_
                    new_files = tree_hashes(stage)
                    old_files = previous.get('components', {}).get(name, {}).get('files', {})
                    if old_files != new_files:
                        self.replace_plugin(txn, target, stage)
                        changed = True
                    state['components'][name] = {'id': id_, 'files': new_files,
                                                 'version': load_json(stage / 'manifest.json')['version']}
                for target, source in resources.items():
                    data = source.read_bytes()
                    if read(Path(target)) != data:
                        txn.write(Path(target), data, 0o644)
                        hypr_changed = hypr_changed or target.endswith('stark-shell-animations.lua')
                        fonts_changed = fonts_changed or '/fonts/' in target
                    state['resources'][target] = {'sha256': digest(data)}
                if args.animations and not state.get('hypr_block'):
                    block = '\n-- BEGIN STARK SHELL ANIMATIONS\ndofile(os.getenv("HOME") .. "/.config/hypr/stark-shell-animations.lua")\n-- END STARK SHELL ANIMATIONS\n'
                    content = read(hypr_config).decode()
                    if 'BEGIN STARK SHELL ANIMATIONS' in content:
                        raise Error('Unmanaged Stark animation marker already exists; resolve it first.')
                    txn.write(hypr_config, (content + block).encode())
                    state['hypr_block'] = {'path': str(hypr_config), 'text': block}
                    hypr_changed = True
                if changed or not previous:
                    self.discover([self.lock['components'][name]['id'] for name in names])
                for name in names:
                    if name in previous.get('components', {}):
                        continue  # preserve user placements and disabled states on repeat/update
                    id_ = self.lock['components'][name]['id']
                    command = ['omarchy', 'plugin', 'enable', id_]
                    if name == 'visualizer':
                        command += ['--section', 'centerEnd']
                    self.native(txn, command)
                after = load_json(self.shell, {})
                # Existing edits are kept; compose new edits against the original baseline.
                baseline, conflicts = reverse_changes(before, state.get('shell_changes', []))
                if conflicts and before != after:
                    raise Error('Previously managed configuration was edited: ' + ', '.join(conflicts))
                if before != after or not previous:
                    state['shell_changes'] = diff(baseline, after)
                state['options'] = {'animations': bool(args.animations), 'fonts': bool(args.fonts)}
                if (self.repo / '.git').exists():
                    state['repository_commit'] = run(['git', '-C', self.repo, 'rev-parse', 'HEAD'], check=False).stdout.strip()
                state['release'] = self.lock['release']
                state['environment'] = environment
                state['last_transaction'] = str(txn.directory)
                if not args.no_reload:
                    if fonts_changed:
                        run(['fc-cache', '-f', self.home / '.local/share/fonts/stark-shell'])
                    self.reload(shell=changed or fonts_changed, hypr=hypr_changed)
                txn.write(self.state_path, json_bytes(state))
                txn.finish()
                print('Stark Shell installed. Receipt:', self.state_path)
            except BaseException:
                conflicts = txn.rollback()
                # Empty staging-owned directories must not obstruct a retry.
                self.prune_directories(names)
                if not args.no_reload:
                    run(['omarchy-shell', 'shell', 'rescanPlugins'], check=False)
                    if args.animations:
                        run(['hyprctl', 'reload'], check=False)
                if conflicts:
                    print('Rollback retained concurrent edits:', ', '.join(conflicts), file=sys.stderr)
                raise

    def prune_directories(self, names):
        for name in names:
            path = self.plugins / self.lock['components'][name]['id']
            if path.exists() and not path.is_symlink():
                for item in sorted(path.rglob('*'), reverse=True):
                    if item.is_dir():
                        try:
                            item.rmdir()
                        except OSError:
                            pass
                try:
                    path.rmdir()
                except OSError:
                    pass

    def ensure_no_pending(self):
        for path in (self.state_dir / 'transactions').glob('*/journal.json'):
            status = load_json(path)['status']
            if status in ('pending', 'rollback-conflict'):
                raise Error(f'Unfinished transaction: {path.parent}. Run ./install.sh --recover before another change.')

    def recover(self, args):
        for path in sorted((self.state_dir / 'transactions').glob('*/journal.json')):
            journal = load_json(path)
            if journal['status'] not in ('pending', 'rollback-conflict'):
                continue
            print('Recover:', path.parent)
            if args.dry_run:
                continue
            txn = Transaction.__new__(Transaction)
            txn.directory, txn.journal = path.parent, journal
            conflicts = txn.rollback()
            if conflicts:
                raise Error('Recovery retained modified files: ' + ', '.join(conflicts))
        print('Recovery check complete. Restart the shell after reviewing restored files.')

    def uninstall(self, args):
        state = self.state()
        if not state:
            print('No Stark-managed installation exists; nothing removed.')
            return
        self.verify_owned(state)
        self.ensure_no_pending()
        current = load_json(self.shell, {})
        restored, conflicts = reverse_changes(current, state['shell_changes'])
        if args.keep_config:
            for record in state['components'].values():
                if record['id'] in json.dumps(current):
                    raise Error('--keep-config requires removing all references to managed plugin IDs first: ' + record['id'])
            restored, conflicts = current, []
        if conflicts:
            raise Error('Configuration conflict; nothing removed. Edited paths: ' + ', '.join(conflicts) +
                        '. See docs/UNINSTALL.md. Your changes are retained.')
        block = state.get('hypr_block')
        hypr_data = None
        if block:
            content = read(Path(block['path'])).decode()
            if block['text'] in content:
                hypr_data = content.replace(block['text'], '', 1).encode()
            elif 'BEGIN STARK SHELL ANIMATIONS' in content:
                raise Error('Your animation include was edited. Nothing removed; retain and resolve the changed block.')
        print('Remove only receipt-owned plugins and resources; reverse unchanged configuration edits.')
        if args.dry_run:
            print('Dry run: no files changed.')
            return
        txn = Transaction(self.state_dir, 'uninstall')
        try:
            if restored != current:
                txn.write(self.shell, None if not restored and not state.get('shell_existed', True) else json_bytes(restored), state.get('shell_mode', 0o600))
            if hypr_data is not None:
                txn.write(Path(block['path']), hypr_data)
            for record in state['components'].values():
                for relative in record['files']:
                    txn.write(self.plugins / record['id'] / relative, None)
            for filename in state.get('resources', {}):
                txn.write(Path(filename), None)
            if not args.no_reload:
                self.reload(shell=True, hypr=bool(block))
                if shutil.which('fc-cache') and any('/fonts/' in key for key in state.get('resources', {})):
                    run(['fc-cache', '-f'])
            txn.write(self.state_path, None)
            txn.finish()
            self.prune_directories(list(state['components']))
            print('Removed Stark-owned installation. Immutable backups retained in', self.state_dir / 'transactions')
        except BaseException:
            txn.rollback()
            raise


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['install', 'update', 'uninstall', 'doctor', 'build'])
    p.add_argument('--components', help='Comma-separated components; default: visualizer, or current installation')
    p.add_argument('--dry-run', action='store_true', help='Validate and preview without changing desktop files')
    p.add_argument('--animations', action='store_true', help='Opt into isolated Hyprland Lua animation overrides')
    p.add_argument('--fonts', action='store_true', help='Install bundled Shantell Sans fonts; does not change terminal fonts')
    p.add_argument('--no-reload', action='store_true', help='Defer shell/Hyprland reloads; restart manually afterward')
    p.add_argument('--keep-config', action='store_true', help='Uninstall only after manually removing owned plugin references')
    p.add_argument('--recover', action='store_true', help='Recover an interrupted transaction conservatively')
    p.add_argument('--output', type=Path, help='Build output directory, required with build')
    return p


def main():
    args = parser().parse_args()
    manager = Manager()
    def interrupted(signum, _frame):
        raise Error(f'Interrupted by signal {signum}; rolling back.')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    if args.action == 'doctor':
        manager.environment()
        print('Managed components:', ', '.join(manager.state().get('components', {})) or 'none')
        return
    if args.action == 'build':
        if not args.output or args.output.exists():
            raise Error('build needs --output pointing to a new directory.')
        manager.materialize(manager.select((args.components or 'visualizer').split(',')), args.output)
        print('Built and validated:', args.output)
        return
    if args.dry_run:
        if args.recover:
            manager.recover(args)
        elif args.action == 'uninstall':
            manager.uninstall(args)
        else:
            manager.install(args, updating=args.action == 'update')
        return
    manager.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (manager.state_dir / '.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Error('Another Stark Shell operation is running.') from error
        if args.recover:
            manager.recover(args)
        elif args.action == 'uninstall':
            manager.uninstall(args)
        else:
            manager.install(args, updating=args.action == 'update')


if __name__ == '__main__':
    try:
        main()
    except (Error, OSError, ValueError, subprocess.SubprocessError) as error:
        print('stark-shell:', error, file=sys.stderr)
        sys.exit(1)
