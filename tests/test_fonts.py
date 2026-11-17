"""Verify the actual bundled fonts using a private Fontconfig config/cache."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('fc-cache') and shutil.which('fc-match'), 'fontconfig unavailable')
class PackagedFontTests(unittest.TestCase):
    def test_bundled_family_resolves_in_isolated_cache(self):
        with tempfile.TemporaryDirectory(prefix='stark font test ') as directory:
            root = Path(directory)
            fonts = root / 'fonts'
            fonts.mkdir()
            config = root / 'fonts.conf'
            config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">'
                              '<fontconfig><dir>' + escape(str(fonts)) + '</dir><cachedir>'
                              + escape(str(root / 'cache')) + '</cachedir></fontconfig>')
            env = dict(os.environ, FONTCONFIG_FILE=str(config), FONTCONFIG_PATH=str(root),
                       XDG_CACHE_HOME=str(root / 'xdg-cache'))
            for source in (ROOT / 'fonts/ShantellSans').glob('*.ttf'):
                shutil.copyfile(source, fonts / source.name)
            subprocess.run(['fc-cache', '-f', str(fonts)], env=env, check=True, capture_output=True)
            result = subprocess.run(['fc-match', '-f', '%{family}\n', 'Shantell Sans'],
                                    env=env, check=True, capture_output=True, text=True)
            self.assertIn('Shantell Sans', [name.strip() for name in result.stdout.strip().split(',')])
            self.assertTrue((root / 'cache').is_dir())
