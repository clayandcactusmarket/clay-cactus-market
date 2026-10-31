import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts import state_store


class StateTests(unittest.TestCase):
    def test_state_survives_independent_checkouts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            remote = root / 'remote.git'
            def git(*args, cwd=root):
                return subprocess.run(['git', *args], cwd=cwd, check=True,
                                      capture_output=True, text=True).stdout
            git('init', '--bare', str(remote))
            checkout = root / 'first'
            git('clone', str(remote), str(checkout))
            (checkout / 'index.html').write_text('website')
            git('add', '.', cwd=checkout)
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                'commit', '-m', 'Initial site', cwd=checkout)
            git('push', 'origin', 'HEAD', cwd=checkout)
            with patch.object(state_store, 'ROOT', checkout), patch.object(
                    state_store, 'STATE', checkout / '_sync_state'):
                state_store.prepare()
                (state_store.STATE / 'oauth.enc').write_text('encrypted-test-value')
                state_store.save()
                self.assertEqual((checkout / 'index.html').read_text(), 'website')
            second = root / 'second'
            git('clone', str(remote), str(second))
            with patch.object(state_store, 'ROOT', second), patch.object(
                    state_store, 'STATE', second / '_sync_state'):
                state_store.prepare()
                self.assertEqual((state_store.STATE / 'oauth.enc').read_text(), 'encrypted-test-value')
                self.assertFalse((state_store.STATE / 'index.html').exists())
                (state_store.STATE / 'catalog.json').write_text('{"products":[]}')
                state_store.save()
