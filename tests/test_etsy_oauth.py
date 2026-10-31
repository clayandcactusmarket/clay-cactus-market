import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from urllib.parse import parse_qs
from cryptography.fernet import Fernet
from scripts import etsy_oauth


class OAuthTests(unittest.TestCase):
    def test_refresh_rotation_is_encrypted_and_persisted(self):
        key = Fernet.generate_key()
        env = {'ETSY_STATE_KEY': key.decode(), 'ETSY_REFRESH_TOKEN': 'initial-token', 'ETSY_API_KEY': 'app-key'}
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', env):
            state = Path(folder)
            persist = Mock()
            for expected, new in [('initial-token', 'second-token'), ('second-token', 'third-token')]:
                def respond(req, timeout):
                    self.assertEqual(parse_qs(req.data.decode())['refresh_token'], [expected])
                    return io.BytesIO(json.dumps({'access_token': 'access', 'refresh_token': new,
                                                 'scope': 'listings_r'}).encode())
                with patch.object(etsy_oauth, 'urlopen', side_effect=respond):
                    self.assertEqual(etsy_oauth.refresh(state, persist), 'access')
                ciphertext = (state / 'oauth.enc').read_bytes()
                self.assertNotIn(new.encode(), ciphertext)
                self.assertEqual(json.loads(Fernet(key).decrypt(ciphertext))['refresh_token'], new)
            self.assertEqual(persist.call_count, 2)

    def test_invalid_state_does_not_reset_authorization(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {
                'ETSY_STATE_KEY': Fernet.generate_key().decode()}):
            state = Path(folder)
            (state / 'oauth.enc').write_bytes(b'invalid')
            with self.assertRaises(ValueError), patch.object(etsy_oauth, 'urlopen') as api:
                etsy_oauth.refresh(state, Mock())
            api.assert_not_called()
