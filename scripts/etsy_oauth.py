"""Refresh read-only Etsy authorization and encrypt the latest refresh token."""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

TOKEN_URL = 'https://api.etsy.com/v3/public/oauth/token'


def refresh(state_dir, persist):
    from cryptography.fernet import Fernet, InvalidToken
    try:
        cipher = Fernet(os.environ['ETSY_STATE_KEY'].encode())
        target = state_dir / 'oauth.enc'
        if target.exists():
            token = json.loads(cipher.decrypt(target.read_bytes()))['refresh_token']
        else:
            token = os.environ['ETSY_REFRESH_TOKEN'].strip()
        request = Request(TOKEN_URL, data=urlencode({
            'grant_type': 'refresh_token', 'client_id': os.environ['ETSY_API_KEY'].strip(),
            'refresh_token': token,
        }).encode(), headers={'Content-Type': 'application/x-www-form-urlencoded'})
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        access = result['access_token']
        new_refresh = result['refresh_token']
        if not access or not new_refresh:
            raise ValueError()
        if result.get('scope') and 'listings_r' not in result['scope'].split():
            raise ValueError()
        # Persist rotation before other API requests; never publish plaintext tokens.
        target.write_bytes(cipher.encrypt(json.dumps({'refresh_token': new_refresh}).encode()))
        persist()
        return access
    except (HTTPError, URLError, KeyError, ValueError, InvalidToken):
        raise ValueError('Etsy listing authorization needs attention. Reconnect the shop; current website preserved.') from None
