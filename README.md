# Clay & Cactus Market Website

A static website for Clay & Cactus Market built with HTML and CSS.

## Project Structure

- index.html: Home page
- about.html: About page
- visit.html: Visit page
- apply.html: Vendor application page
- ceramics.html: Ceramics by Jaymi page
- data/ceramics.json: Ceramics product list (edit this to add, remove, or change listings)
- ceramics.js: Builds the ceramics grid and detail view from ceramics.json
- assets/ceramics/: Product photos
- style.css: Shared site styles
- main.js: Shared mobile navigation script
- assets/: Images and fonts

## Run Locally

Because this is a static site, you can:

1. Open index.html directly in your browser, or
2. Serve with a local web server for best results.

Example using VS Code Live Server:

1. Install the Live Server extension
2. Right-click index.html
3. Select "Open with Live Server"

## Edit Content

- Main homepage content: index.html
- Shared colors, typography, layout: style.css
- Shared mobile menu behavior: main.js
- Secondary page content: about.html, visit.html, apply.html

## Manage Ceramics Listings

1. Add the product photo to assets/ceramics/
2. Add an entry to the products list in data/ceramics.json (id, name, price, currency, image, imageAlt, description, seoDescription, tags, etsyUrl, available)
3. Set "available": false to show a Sold badge and hide the Buy button

The ceramics page loads the JSON with fetch, so test it with Live Server rather than opening the file directly. A future Etsy sync can simply regenerate data/ceramics.json in the same format.
The page also creates schema.org structured data (CollectionPage + ItemList + Product + Offer) from this JSON to support search indexing.

## Google Indexing Checklist

1. Deploy the latest files (`ceramics.html`, `ceramics.js`, `data/ceramics.json`, `sitemap.xml`)
2. In Google Search Console, submit:
   - `https://clayandcactusmarket.com/sitemap.xml`
   - `https://clayandcactusmarket.com/ceramics.html` via URL Inspection > Request Indexing
3. Verify the page is crawlable:
   - `robots.txt` allows crawling
   - canonical points to `https://clayandcactusmarket.com/ceramics.html`
4. Re-submit indexing whenever products or product text is updated significantly

## Deploy (Static Hosting)

This site can be deployed to any static host, including:

- GitHub Pages
- Netlify
- Vercel (static)
- Cloudflare Pages

### Important

Some hosts are case-sensitive.

- Current homepage file is named index.html (lowercase i)

## Footer Notice

Current footer copy:

"© 2026 Clay & Cactus LLC. All rights reserved."

## Contact Forms

Formspree endpoints currently in use:

- Stay in the Loop form: https://formspree.io/f/xbdzkvpv
- Contact form: https://formspree.io/f/mdawwndp
- Vendor application form: https://formspree.io/f/xjgaazdv
