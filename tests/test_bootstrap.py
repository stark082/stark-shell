"""Bootstrap failure tests never access the network or desktop."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    def invoke(self, *args, git_body='exit 128'):
        with tempfile.TemporaryDirectory(prefix='stark bootstrap ') as directory:
            root = Path(directory)
            script = root / 'git'
            script.write_text('#!/bin/bash\n' + git_body + '\n')
            script.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + ':' + os.environ['PATH'], TMPDIR=directory)
            result = subprocess.run(['bash', str(ROOT / 'bootstrap.sh'), *args],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['git'])
            return result

    def test_release_requires_trusted_commit(self):
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires --commit', result.stderr)

    def test_failed_download_propagates(self):
        result = self.invoke('--dev-branch', 'main', '--dry-run')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('download failed', result.stderr)

    def test_missing_argument(self):
        self.assertNotEqual(self.invoke('--ref').returncode, 0)

    def test_commit_mismatch_never_executes_installer(self):
        body = 'if [[ "$*" == *rev-parse* ]]; then echo ' + 'b' * 40 + '; fi'
        result = self.invoke('--commit', 'a' * 40, git_body=body)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('integrity mismatch', result.stderr)
