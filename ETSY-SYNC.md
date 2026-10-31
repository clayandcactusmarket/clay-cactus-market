# Etsy catalog and sold-piece portfolio

The hourly GitHub Actions workflow reads active and sold-out listings from
ClayAndCactusMarket. Available pieces appear first. Sold pieces keep their photos,
descriptions and Sold badge, hide the Etsy purchase button, and show **Request a
Custom Order** linking to `/#contact`. Expired, inactive and draft pieces are not
published. Disappearance from the active feed is never treated as proof of sale.

## Authorization and private settings

The Etsy app requests only `listings_r`. It cannot edit Etsy listings or access
customer orders/payments. Register this exact callback in the app:
`https://clayandcactusmarket.com/etsy-connect.html`.

Repository Actions secrets:
- `ETSY_API_KEY`: app keystring.
- `ETSY_SHARED_SECRET`: app shared secret.
- `ETSY_REFRESH_TOKEN`: initial token obtained through OAuth authorization-code
  flow with PKCE and a verified one-use state value.
- `ETSY_STATE_KEY`: a Fernet encryption key used to protect renewal tokens.

Never commit plaintext credentials or print them in workflow logs. The callback
page has no external assets and sets a no-referrer policy. Its authorization code
is exchanged from the setup environment using the private PKCE verifier, not by
public website JavaScript. Clear the callback query after exchange.

## Durable state

The build job has repository contents-write permission to maintain the separate
`etsy-sync-state` branch. It stores public catalog snapshots and photo copies,
plus `oauth.enc`, an encrypted renewal token. The encryption key remains in GitHub
secrets. Each run refreshes authorization and persists the rotated token before
fetching listings. Do not delete that branch or change the encryption key without
reconnecting Etsy. No plaintext token enters the Pages artifact.

Confirmed sold pieces remain in the portfolio even if later absent from Etsy.
If Etsy makes the piece active again, its availability and purchase link return.
Photos are archived under `assets/etsy/` in the deployed website. The ordinary
source branch keeps its existing manual catalog as a backup; deployed data comes
from the last successful import and the state branch.

## Deployment and operations

Pages source is **GitHub Actions**. Keep the existing custom domain and HTTPS.
Run **Actions → Sync Etsy and publish website → Run workflow** for an immediate
refresh. The hourly schedule is approximate; GitHub can delay jobs or disable
public-repository schedules after 60 days without repository activity.

A failed authorization, fetch, archive write or build stops deployment and leaves
the previous website online. Check the failed Actions run. If Etsy authorization
is revoked, repeat the PKCE approval flow, update the initial refresh-token secret,
and remove only `oauth.enc` from the state branch before retrying; preserve the
catalog and photos. Keep the encryption key unchanged unless deliberately rotating
it together with a new authorization.

## Local validation

Python 3.12+, PowerShell 7, and `cryptography>=46,<47` are used in Actions:

```sh
python3 -m unittest discover -s tests
pwsh -File build-ceramics.ps1
python3 scripts/stage_site.py
python3 -m http.server 5174 --bind 0.0.0.0 --directory _site
```

Local rendering uses the checked-in manual data unless a live import is run.
Do not run the production state-writing flow in an untrusted checkout.

Official references:
- https://developers.etsy.com/documentation/essentials/authentication/
- https://developer.etsy.com/documentation/reference/#operation/getListingsByShop
