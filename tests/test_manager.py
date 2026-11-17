"""Isolated integration tests. Every file and command belongs to a temporary HOME."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stark_manager', ROOT / 'tools/stark_manager.py')
stark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stark)

MOCK = r'''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
name=Path(sys.argv[0]).name; a=sys.argv[1:]; home=Path.home()
log=home/'commands.jsonl'
with log.open('a') as f: f.write(json.dumps([name]+a)+'\n')
config=home/'.config/omarchy/shell.json'
def read(): return json.loads(config.read_text()) if config.exists() else {}
def write(value):
 config.parent.mkdir(parents=True,exist_ok=True);temp=config.with_suffix('.new');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(config)
if name=='fc-cache': print('ok')
elif name=='quickshell': print('Quickshell 0.3.2')
elif name=='hyprctl':
 if a==['version']: print('Hyprland '+os.environ.get('MOCK_HYPR_VERSION','0.56.2'))
 elif a==['configerrors']: print(os.environ.get('MOCK_HYPR_ERRORS',''))
 else: print('ok')
elif name=='omarchy-shell': print('ok')
elif a==['version']: print(os.environ.get('MOCK_OMARCHY_VERSION','4.5.0-3'))
elif a[:2]==['restart','shell']:
 marker=home/'reload-failed'
 if os.environ.get('MOCK_FAIL_RELOAD') and not marker.exists(): marker.touch();sys.exit(1)
 print('ok')
elif a[:2]==['plugin','validate']:
 if a[-1]!='--help':
  p=Path(a[-1]);m=json.loads((p/'manifest.json').read_text())
  assert m['schemaVersion']==1 and not m['id'].startswith('omarchy.')
  assert all((p/value).is_file() for value in m['entryPoints'].values())
elif a[:3]==['plugin','list','--json']:
 print(json.dumps([json.loads(p.read_text()) for p in (home/'.config/omarchy/plugins').glob('*/manifest.json')]))
elif a[:2]==['plugin','enable']:
 id=a[2]
 if os.environ.get('MOCK_FAIL_ENABLE')==id: sys.exit(1)
 m=json.loads((home/'.config/omarchy/plugins'/id/'manifest.json').read_text());c=read()
 bar=c.setdefault('bar',{});layout=bar.setdefault('layout',{})
 if 'bar' in m['kinds']: bar['id']=id
 else:
  source=m.get('omarchy',{}).get('clonedFrom');found=False
  for section,entries in layout.items():
   for entry in entries:
    if entry['id']==source: entry['id']=id;found=True
    elif entry['id']==id: found=True
  if not found:
   section=a[a.index('--section')+1] if '--section' in a else 'right'
   layout.setdefault(section,[]).append({'id':id})
 write(c)
else: sys.exit('Unexpected mocked command: '+str([name]+a))
'''


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='stark-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        self.home.mkdir()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.native = self.root / 'omarchy'
        self.native.mkdir()
        for relative, token in {'shell/Ui/BarWidget.qml':'function setting',
                                'shell/Commons/Style.qml':'function duration',
                                'shell/services/PluginRegistry.qml':'clonedFrom'}.items():
            p = self.native / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(token)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        for command in ['omarchy', 'omarchy-shell', 'quickshell', 'hyprctl', 'fc-cache']:
            script = self.bin / command
            script.write_text(MOCK)
            script.chmod(0o755)
        self.environment = patch.dict(os.environ, {'HOME': str(self.home),
            'OMARCHY_PATH': str(self.native), 'XDG_CONFIG_HOME': str(self.home / '.config'),
            'XDG_STATE_HOME': str(self.home / '.local/state'), 'PATH': str(self.bin)+':'+os.environ['PATH']})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for name in list(os.environ):
            if name.startswith('MOCK_'):
                os.environ.pop(name)
        self.plan = {'schema':1,'release':'0.1.0','components':{}}
        for component, id_, kind, source, deps in [
            ('visualizer','stark.visualizer','bar-widget',None,[]),
            ('island','stark.bar','bar','omarchy.bar',[]),
            ('launcher','stark.menu','bar-widget','omarchy.menu',['island'])]:
            directory=self.repo/'plugins'/id_;directory.mkdir(parents=True)
            manifest={'schemaVersion':1,'id':id_,'name':id_,'version':'0.1.0','kinds':[kind],
                      'entryPoints':{'bar' if kind=='bar' else 'barWidget':'Main.qml'}}
            if source: manifest['omarchy']={'clonedFrom':source}
            (directory/'manifest.json').write_text(json.dumps(manifest))
            (directory/'Main.qml').write_text('import QtQuick\nItem {}\n')
            files={}
            for p in directory.iterdir():
                files[p.name]={'overlay':str(p.relative_to(self.repo)),'sha256':stark.digest(p.read_bytes())}
            self.plan['components'][component]={'id':id_,'dependencies':deps,'files':files}
        (self.repo/'packaging').mkdir()
        (self.repo/'hypr').mkdir()
        (self.repo/'hypr/stark-animations.lua').write_text('-- isolated animation module\n')
        (self.repo/'fonts/ShantellSans').mkdir(parents=True)
        (self.repo/'fonts/ShantellSans/Test.ttf').write_bytes(b'font-fixture')
        (self.repo/'packaging/fonts.lock.json').write_text(json.dumps({'files':{'Test.ttf':stark.digest(b'font-fixture')}}))
        self.save_plan()
        self.original={'bar':{'id':'omarchy.bar','layout':{'left':[{'id':'omarchy.menu','custom':'keep'}],
            'center':[{'id':'omarchy.clock','format':'HH:mm'}],'right':[{'id':'third.party','answer':42}]}},
            'plugins':[{'id':'private.plugin','setting':'keep'}], 'personal':{'preserve':True}}
        self.config=self.home/'.config/omarchy/shell.json'
        self.config.parent.mkdir(parents=True)
        self.config.write_bytes(stark.json_bytes(self.original))
        hypr=self.home/'.config/hypr/hyprland.lua';hypr.parent.mkdir();hypr.write_text('-- my bindings stay\n')
        self.manager=stark.Manager(self.repo)

    def save_plan(self):
        (self.repo/'packaging/upstreams.lock.json').write_bytes(stark.json_bytes(self.plan))

    def args(self, **changes):
        values=dict(components=None,dry_run=False,animations=False,fonts=False,no_reload=False,keep_config=False)
        values.update(changes)
        return argparse.Namespace(**values)

    def install(self, **changes):
        self.manager.install(self.args(**changes))

    def uninstall(self, **changes):
        self.manager.uninstall(self.args(**changes))

    def test_fresh_install_keeps_stock_bar(self):
        self.install()
        c=stark.load_json(self.config)
        self.assertEqual(c['bar']['id'],'omarchy.bar')
        self.assertEqual(c['personal'],self.original['personal'])
        self.assertEqual(c['bar']['layout']['centerEnd'],[{'id':'stark.visualizer'}])
        self.assertTrue(self.manager.state_path.exists())

    def test_repeated_install_has_no_duplicate_or_reactivation(self):
        self.install();before=self.config.read_bytes();self.install()
        self.assertEqual(before,self.config.read_bytes())
        calls=[json.loads(line) for line in (self.home/'commands.jsonl').read_text().splitlines()]
        self.assertEqual(sum(c[:3]==['omarchy','plugin','enable'] for c in calls),1)

    def test_selective_install_resolves_dependencies_preserves_settings(self):
        self.install(components='launcher')
        c=stark.load_json(self.config)
        self.assertEqual(set(self.manager.state()['components']),{'island','launcher'})
        self.assertEqual(c['bar']['layout']['left'],[{'id':'stark.menu','custom':'keep'}])
        self.assertEqual(c['bar']['layout']['right'],self.original['bar']['layout']['right'])

    def test_missing_optional_cava_is_not_fatal(self):
        original=shutil.which
        with patch.object(stark.shutil,'which',side_effect=lambda n: None if n=='cava' else original(n)):
            self.install()
        self.assertFalse(self.manager.state()['environment']['optional']['cava'])

    def test_unsupported_environment_refuses_before_modification(self):
        os.environ['MOCK_OMARCHY_VERSION']='3.0.0'
        with self.assertRaises(stark.Error): self.install()
        self.assertEqual(stark.load_json(self.config),self.original)
        self.assertFalse(self.manager.state_path.exists())

    def test_unsupported_hyprland_refuses(self):
        os.environ['MOCK_HYPR_VERSION']='0.57.0'
        with self.assertRaises(stark.Error): self.install()

    def test_dry_run_has_no_desktop_or_state_writes(self):
        before=self.config.read_bytes();self.install(dry_run=True)
        self.assertEqual(before,self.config.read_bytes())
        self.assertFalse(self.manager.plugins.exists());self.assertFalse(self.manager.state_dir.exists())

    def test_existing_unmanaged_prototype_is_never_adopted(self):
        target=self.manager.plugins/'stark.visualizer';target.mkdir(parents=True)
        (target/'personal.txt').write_text('keep')
        with self.assertRaises(stark.Error): self.install()
        self.assertEqual((target/'personal.txt').read_text(),'keep')

    def test_uninstall_restores_existing_config(self):
        self.install(components='launcher,visualizer');self.uninstall()
        self.assertEqual(stark.load_json(self.config),self.original)
        self.assertFalse(self.manager.state_path.exists())
        self.assertFalse((self.manager.plugins/'stark.menu').exists())

    def test_unrelated_edits_survive_uninstall(self):
        self.install();c=stark.load_json(self.config);c['new-personal-key']={'yes':True};self.config.write_bytes(stark.json_bytes(c))
        self.uninstall();expected=copy.deepcopy(self.original);expected['new-personal-key']={'yes':True}
        self.assertEqual(stark.load_json(self.config),expected)

    def test_modified_widget_list_is_conflict_and_nothing_removed(self):
        self.install();c=stark.load_json(self.config);c['bar']['layout']['centerEnd'].append({'id':'new.widget'});self.config.write_bytes(stark.json_bytes(c))
        before=self.config.read_bytes()
        with self.assertRaises(stark.Error): self.uninstall()
        self.assertEqual(self.config.read_bytes(),before);self.assertTrue(self.manager.state_path.exists())

    def test_modified_plugin_is_conflict_for_update_and_uninstall(self):
        self.install();p=self.manager.plugins/'stark.visualizer/Main.qml';p.write_text('my edit')
        with self.assertRaises(stark.Error): self.install()
        with self.assertRaises(stark.Error): self.uninstall()
        self.assertEqual(p.read_text(),'my edit')

    def test_failed_activation_rolls_back_files_and_config(self):
        os.environ['MOCK_FAIL_ENABLE']='stark.menu'
        with self.assertRaises(stark.Error): self.install(components='launcher')
        self.assertEqual(stark.load_json(self.config),self.original)
        self.assertFalse(self.manager.state_path.exists());self.assertFalse((self.manager.plugins/'stark.bar').exists())

    def test_failed_reload_rolls_back(self):
        os.environ['MOCK_FAIL_RELOAD']='1'
        with self.assertRaises(stark.Error): self.install()
        self.assertEqual(stark.load_json(self.config),self.original)
        self.assertFalse(self.manager.state_path.exists())

    def test_upgrade_changes_owned_files_keeps_layout(self):
        self.install();before=self.config.read_bytes()
        p=self.repo/'plugins/stark.visualizer/Main.qml';p.write_text('import QtQuick\nItem { property bool upgraded: true }\n')
        self.plan['components']['visualizer']['files']['Main.qml']['sha256']=stark.digest(p.read_bytes())
        self.plan['release']='0.1.1';self.save_plan();self.manager=stark.Manager(self.repo)
        self.manager.install(self.args(),updating=True)
        self.assertEqual(self.config.read_bytes(),before)
        self.assertIn('upgraded',(self.manager.plugins/'stark.visualizer/Main.qml').read_text())
        self.assertEqual(self.manager.state()['release'],'0.1.1')

    def test_isolated_animations_preserve_manual_text_edits(self):
        self.install(animations=True)
        hypr=self.home/'.config/hypr/hyprland.lua';hypr.write_text(hypr.read_text()+'-- later personal settings\n')
        self.uninstall()
        self.assertEqual(hypr.read_text(),'-- my bindings stay\n-- later personal settings\n')

    def test_modified_animation_block_is_conflict(self):
        self.install(animations=True);p=self.home/'.config/hypr/hyprland.lua';p.write_text(p.read_text().replace('dofile(', '-- dofile('))
        with self.assertRaises(stark.Error): self.uninstall()

    def test_optional_fonts_install_and_remove_only_owned_files(self):
        other=self.home/'.local/share/fonts/Other.ttf';other.parent.mkdir(parents=True);other.write_text('keep')
        self.install(fonts=True);self.assertTrue((other.parent/'stark-shell/Test.ttf').exists())
        self.uninstall();self.assertEqual(other.read_text(),'keep')

    def test_source_hash_rejects_incompatible_upstream(self):
        source=self.native/'source.qml';source.write_text('wrong source')
        rec=self.plan['components']['visualizer']['files']['Main.qml'];rec.pop('overlay');rec['source']='source.qml';rec['source_sha256']='0'*64
        self.save_plan();self.manager=stark.Manager(self.repo)
        with self.assertRaises(stark.Error): self.install()
        self.assertFalse(self.manager.plugins.exists())

    def test_recovery_preserves_concurrent_edit(self):
        txn=stark.Transaction(self.manager.state_dir,'test');p=self.home/'owned';txn.write(p,b'installed');p.write_bytes(b'personal')
        conflicts=txn.rollback();self.assertEqual(conflicts,[str(p)]);self.assertEqual(p.read_bytes(),b'personal')

    def test_recovery_restores_original(self):
        p=self.home/'owned';p.write_bytes(b'original');txn=stark.Transaction(self.manager.state_dir,'test');txn.write(p,b'installed')
        self.manager.recover(self.args());self.assertEqual(p.read_bytes(),b'original')

    def test_keep_config_refuses_dangling_references(self):
        self.install()
        with self.assertRaises(stark.Error): self.uninstall(keep_config=True)

    def test_existing_symlink_plugin_refused(self):
        target=self.root/'mine';target.mkdir();self.manager.plugins.mkdir(parents=True)
        (self.manager.plugins/'stark.visualizer').symlink_to(target,target_is_directory=True)
        with self.assertRaises(stark.Error): self.install()

    def test_update_without_install_refused(self):
        with self.assertRaises(stark.Error): self.manager.install(self.args(),updating=True)

    def test_missing_interface_refused(self):
        (self.native/'shell/Ui/BarWidget.qml').unlink()
        with self.assertRaises(stark.Error): self.install()
        self.assertFalse(self.manager.state_path.exists())

    def test_parent_directory_symlink_refused(self):
        external=self.root/'external';external.mkdir()
        (self.home/'.config/omarchy/plugins').symlink_to(external,target_is_directory=True)
        with self.assertRaises(stark.Error): self.install()
        self.assertEqual(list(external.iterdir()),[])

    def test_upgrade_removes_obsolete_owned_files(self):
        self.install()
        self.plan['components']['visualizer']['files'].pop('Main.qml')
        # The manifest now names a newly introduced entry point.
        directory=self.repo/'plugins/stark.visualizer'
        p=directory/'New.qml';p.write_text('import QtQuick\nItem {}\n')
        self.plan['components']['visualizer']['files']['New.qml']={'overlay':str(p.relative_to(self.repo)),'sha256':stark.digest(p.read_bytes())}
        p=directory/'manifest.json';m=json.loads(p.read_text());m['entryPoints']['barWidget']='New.qml';p.write_text(json.dumps(m))
        self.plan['components']['visualizer']['files']['manifest.json']['sha256']=stark.digest(p.read_bytes())
        self.save_plan();self.manager=stark.Manager(self.repo)
        self.manager.install(self.args(),updating=True)
        self.assertFalse((self.manager.plugins/'stark.visualizer/Main.qml').exists())
        self.assertTrue((self.manager.plugins/'stark.visualizer/New.qml').exists())

    def test_absent_shell_config_is_restored_to_absent(self):
        self.config.unlink();self.install();self.uninstall()
        self.assertFalse(self.config.exists())

    def test_original_config_mode_restored(self):
        self.config.chmod(0o640);self.install();self.uninstall()
        self.assertEqual(self.config.stat().st_mode & 0o777,0o640)

    def test_changed_font_asset_refused_before_install(self):
        (self.repo/'fonts/ShantellSans/Test.ttf').write_bytes(b'bad')
        with self.assertRaises(stark.Error): self.install(fonts=True)
        self.assertFalse(self.manager.plugins.exists())

    def test_no_install_uninstall_is_noop(self):
        self.uninstall();self.assertEqual(stark.load_json(self.config),self.original)


if __name__=='__main__': unittest.main()
