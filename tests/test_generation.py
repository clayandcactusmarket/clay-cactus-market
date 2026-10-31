import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PWSH = os.environ.get('PWSH') or shutil.which('pwsh')


@unittest.skipUnless(PWSH, 'PowerShell 7 required for HTML generation test')
class GenerationTests(unittest.TestCase):
    def test_remote_photo_and_script_escaping(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copy(ROOT / 'build-ceramics.ps1', root)
            shutil.copy(ROOT / 'ceramics.html', root)
            (root / 'data').mkdir()
            product = {'id': '123', 'name': '<Cup> & bowl', 'price': 12.50,
                       'currency': 'USD', 'image': 'https://i.etsystatic.com/photo.jpg',
                       'description': '</script><script>alert(1)</script>',
                       'etsyUrl': 'https://www.etsy.com/listing/123', 'available': True}
            (root / 'data/ceramics.json').write_text(json.dumps({'products': [product]}))
            subprocess.run([PWSH, '-NoProfile', '-File', str(root / 'build-ceramics.ps1')],
                           check=True, capture_output=True)
            page = (root / 'ceramics.html').read_text()
            self.assertIn('&lt;Cup&gt; &amp; bowl', page)
            self.assertNotIn(product['description'], page)
            modal = re.search(r'id="ceramics-data">(.*?)</script>', page, re.S).group(1)
            self.assertEqual(json.loads(modal)['products'][0]['description'], product['description'])
            schema = re.search(r'type="application/ld\+json">(.*?)</script>', page, re.S).group(1)
            self.assertEqual(json.loads(schema)['mainEntity']['itemListElement'][0]['item']['image'], product['image'])
