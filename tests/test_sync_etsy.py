import copy
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from scripts import sync_etsy
from scripts.sync_etsy import convert_listing, fetch_listings


def listing(number):
    return {"listing_id": number, "shop_id": 42, "state": "active", "quantity": 1,
            "title": "Clay &amp; Cactus", "description": "Handmade\n&lt;cup&gt;",
            "price": {"amount": 4500, "divisor": 100, "currency_code": "USD"}, "tags": ["pottery"]}


IMAGES = [{"rank": 2, "url_570xN": "https://i.etsystatic.com/last.jpg"},
          {"rank": 1, "url_570xN": "https://i.etsystatic.com/main.jpg", "alt_text": "Blue cup"}]


class SyncTests(unittest.TestCase):
    def test_money_text_and_main_image(self):
        product = convert_listing(listing(1), IMAGES)
        self.assertEqual(product["price"], 45)
        self.assertEqual(product["name"], "Clay & Cactus")
        self.assertEqual(product["description"], "Handmade\n<cup>")
        self.assertEqual(product["image"], "https://i.etsystatic.com/main.jpg")
        self.assertEqual(product["etsyUrl"], "https://www.etsy.com/listing/1")

    def api(self, total=101, failure=None):
        def request(path, **params):
            if path == "shops":
                return {"results": [{"shop_id": 99, "shop_name": "ClayAndCactusMarketOther"},
                                    {"shop_id": 42, "shop_name": "ClayAndCactusMarket"}]}
            if path.endswith("/images"):
                if failure == "images":
                    raise ValueError("Image fetch failed")
                return {"results": IMAGES}
            self.assertEqual(path, "shops/42/listings/active")
            offset = params["offset"]
            rows = [listing(i) for i in range(offset + 1, min(total, offset + 100) + 1)]
            if offset and failure == "duplicate":
                rows[0] = listing(1)
            if offset and failure == "incomplete":
                rows = []
            count = total + (1 if offset and failure == "changed" else 0)
            return {"count": count, "results": rows}
        return request

    def test_all_pages(self):
        products = fetch_listings(self.api())["products"]
        self.assertEqual(len(products), 101)
        self.assertEqual(products[-1]["id"], "101")

    def test_empty_shop(self):
        self.assertEqual(fetch_listings(self.api(total=0))["products"], [])

    def test_sold_archive_and_restock(self):
        base = self.api(total=1)
        def api(path, **params):
            if path == 'shops/42/listings':
                self.assertEqual(params['state'], 'sold_out')
                sold = listing(2)
                sold.update(state='sold_out', quantity=0)
                return {'count': 1, 'results': [sold]}
            return base(path, **params)
        old = convert_listing(dict(listing(3), state='sold_out'), IMAGES)
        restocked = convert_listing(dict(listing(1), state='sold_out'), IMAGES)
        withdrawn = convert_listing(listing(4), IMAGES)
        products = fetch_listings(api, include_sold=True,
            previous={'products': [old, restocked, withdrawn]})['products']
        self.assertEqual([p['id'] for p in products], ['1', '3', '2'])
        self.assertTrue(products[0]['available'])
        self.assertTrue(all(not p['available'] for p in products[1:]))

    def test_incomplete_fetch_aborts(self):
        for failure in ("duplicate", "incomplete", "changed", "images"):
            with self.subTest(failure=failure), self.assertRaises(ValueError):
                fetch_listings(self.api(failure=failure))

    def test_missing_images_and_invalid_urls_abort(self):
        with self.assertRaises(ValueError):
            convert_listing(listing(1), [])
        bad = copy.deepcopy(IMAGES)
        bad[1]["url_570xN"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            convert_listing(listing(1), bad)

    def test_failed_fetch_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            target = root / 'data/ceramics.json'
            target.write_text('previous catalog')
            with patch.object(sync_etsy, 'ROOT', root), patch.object(
                    sync_etsy, 'fetch_listings', side_effect=ValueError('test failure')):
                self.assertEqual(sync_etsy.main(), 1)
            self.assertEqual(target.read_text(), 'previous catalog')


if __name__ == "__main__":
    unittest.main()
