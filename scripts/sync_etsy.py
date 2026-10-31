"""Read public Etsy listings; replace catalog only after a complete, valid fetch."""
import html
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SHOP = "ClayAndCactusMarket"
BASE = "https://openapi.etsy.com/v3/application/"


def request(path, **params):
    key = os.environ.get("ETSY_API_KEY", "").strip()
    secret = os.environ.get("ETSY_SHARED_SECRET", "").strip()
    if not key or not secret:
        raise ValueError("Set ETSY_API_KEY and ETSY_SHARED_SECRET in repository secrets.")
    url = BASE + path + ("?" + urlencode(params) if params else "")
    for attempt in range(4):
        try:
            time.sleep(0.15)  # Stay below the app's 10 requests/second limit.
            req = Request(url, headers={"x-api-key": key + ":" + secret,
                                       "Accept": "application/json"})
            with urlopen(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code != 429 and exc.code < 500:
                raise ValueError(f"Etsy returned HTTP {exc.code}; catalog unchanged.") from None
            if attempt == 3:
                raise ValueError("Etsy is temporarily unavailable; catalog unchanged.") from None
            time.sleep(min(60, max(2 ** attempt, int(exc.headers.get("Retry-After", "1")))))
        except (URLError, TimeoutError):
            if attempt == 3:
                raise ValueError("Unable to reach Etsy; catalog unchanged.") from None
            time.sleep(2 ** attempt)


def fetch_listings(api=request):
    shops = api("shops", shop_name=SHOP, limit=100)["results"]
    matches = [s for s in shops if s["shop_name"].casefold() == SHOP.casefold()]
    if len(matches) != 1:
        raise ValueError("Could not identify the exact Etsy shop; catalog unchanged.")
    shop_id = matches[0]["shop_id"]
    listings = []
    expected = None
    while True:
        page = api(f"shops/{shop_id}/listings/active", limit=100, offset=len(listings))
        if expected is None:
            expected = page["count"]
        if page["count"] != expected:
            raise ValueError("Listings changed during synchronization; retry the workflow.")
        rows = page["results"]
        listings.extend(rows)
        if len(listings) >= expected:
            break
        if not rows:
            raise ValueError("Etsy returned an incomplete page; catalog unchanged.")
    if len(listings) != expected or len({x["listing_id"] for x in listings}) != expected:
        raise ValueError("Etsy returned incomplete or duplicate listings; catalog unchanged.")
    products = []
    for listing in listings:
        if listing["shop_id"] != shop_id or listing["state"] != "active":
            raise ValueError("Unexpected shop or listing state; catalog unchanged.")
        if listing["quantity"] < 1:
            continue
        images = api(f"listings/{listing['listing_id']}/images")["results"]
        products.append(convert_listing(listing, images))
    return {"collection": "Ceramics by Jaymi", "shopUrl": f"https://www.etsy.com/shop/{SHOP}",
            "products": products}


def convert_listing(listing, images):
    images = sorted(images, key=lambda image: image["rank"])
    if not images:
        raise ValueError(f"Listing {listing['listing_id']} has no photos; catalog unchanged.")
    image = images[0]
    image_url = image.get("url_570xN") or image.get("url_fullxfull")
    parsed = urlparse(image_url or "")
    if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".etsystatic.com"):
        raise ValueError("Unexpected Etsy image URL; catalog unchanged.")
    money = listing["price"]
    if money["divisor"] <= 0 or money["amount"] < 0:
        raise ValueError("Invalid Etsy price; catalog unchanged.")
    name = html.unescape(listing["title"])
    description = html.unescape(listing["description"])
    return {"id": str(listing["listing_id"]), "name": name,
            "price": money["amount"] / money["divisor"], "currency": money["currency_code"],
            "image": image_url, "imageAlt": html.unescape(image.get("alt_text") or name),
            "description": description, "seoDescription": description,
            "tags": [html.unescape(tag) for tag in listing.get("tags", [])],
            "etsyUrl": f"https://www.etsy.com/listing/{listing['listing_id']}", "available": True}


def main():
    try:
        data = fetch_listings()
        target = ROOT / "data/ceramics.json"
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
        print(f"Synchronized {len(data['products'])} active listings from {SHOP}.")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        # Never log request headers, credentials, or API response bodies.
        print(f"Synchronization failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
