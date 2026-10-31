# Automatic Etsy catalog

The website reads active listings from **ClayAndCactusMarket** hourly and on each
push to `main`. It keeps the existing layout and purchase links. Draft, inactive,
expired and sold-out listings are excluded; the website does not publish or edit Etsy.
Titles, descriptions, tags, prices and the first photo come from Etsy. Etsy is the
source of truth after activation, so update listing content there. Existing manual
catalog data remains in Git history as a backup.

## One-time setup (repository administrator)

1. In **Settings → Secrets and variables → Actions**, add repository secrets
   `ETSY_API_KEY` (the app's keystring) and `ETSY_SHARED_SECRET` (its shared secret).
   Never put either value in a file, commit, issue, chat message or website JavaScript.
2. In **Settings → Pages**, set **Source** to **GitHub Actions**. Retain the existing
   custom domain `clayandcactusmarket.com` and HTTPS settings.
3. Merge these changes to `main`.
4. In **Actions → Sync Etsy and publish website**, choose **Run workflow**.
5. Verify the completed deployment and compare the ceramics page to the Etsy shop.

The workflow needs Pages write and identity-token permissions only for deployment;
it cannot change Etsy. It publishes an artifact rather than committing generated
catalog data. The repository's checked-in catalog therefore remains the manual
snapshot, while the deployed page reflects the latest successful Etsy fetch.

## Behavior and failures

- GitHub's hourly schedule is approximate and can be delayed. Run the workflow
  manually when an immediate refresh is needed. In public repositories, GitHub may
  disable scheduled workflows after 60 days without repository activity; re-enable
  it in Actions if needed.
- Sold-out or removed pieces disappear on the next successful refresh. Checkout
  stays on Etsy, which checks current availability and final pricing.
- All pages and photos must load successfully before publishing. On API or build
  failure the last deployed website stays live. Inspect the failed Actions run.
- A legitimately empty shop produces the existing “New pieces are on the way” view.
- The workflow uses public read endpoints and does not need buyer data or OAuth.
- Only public site files enter the deployment artifact. Repository secrets remain
  in GitHub's Actions environment and are not sent to visitors.

## Local checks

Requires Python 3.9+ and PowerShell 7:

```sh
python3 -m unittest discover -s tests
pwsh -File build-ceramics.ps1
python3 scripts/stage_site.py
python3 -m http.server 5174 --bind 0.0.0.0 --directory _site
```

Local generation uses the checked-in manual data unless `scripts/sync_etsy.py` is
run first with both secrets supplied through the process environment. Do not type
secret values directly into a shell command saved in history.

Official API documentation:
- https://developers.etsy.com/documentation/essentials/requests/
- https://developer.etsy.com/documentation/reference/#operation/findAllActiveListingsByShop
- https://developer.etsy.com/documentation/reference/#operation/getListingImages
