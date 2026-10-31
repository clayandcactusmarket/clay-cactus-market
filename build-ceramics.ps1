# Regenerates the pre-rendered ceramics collection in ceramics.html.
# data/ceramics.json is the single source of truth for listings:
# edit it, then run this script (.\build-ceramics.ps1) before publishing.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$dataFile = Join-Path $root 'data\ceramics.json'
$pageFile = Join-Path $root 'ceramics.html'
$beginMarker = '<!-- CERAMICS:BEGIN-GENERATED -->'
$endMarker = '<!-- CERAMICS:END-GENERATED -->'
$siteUrl = 'https://clayandcactusmarket.com'
$indent = '            '
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function ConvertTo-HtmlEncoded([string]$value) {
    return $value.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;').Replace('"', '&quot;')
}

function Format-Price($product) {
    $amount = ([decimal]$product.price).ToString('0.00', [System.Globalization.CultureInfo]::InvariantCulture)
    if ($product.currency -and $product.currency -ne 'USD') { return $product.currency + ' ' + $amount }
    return '$' + $amount
}

function Build-Card($product) {
    $name = ConvertTo-HtmlEncoded $product.name
    $altText = if ($product.imageAlt) { $product.imageAlt } else { $product.name }
    $alt = ConvertTo-HtmlEncoded $altText
    $lines = @(
        '<li class="ceramics-card">'
        '    <button class="ceramics-card__button" type="button" aria-label="View details for ' + $name + '" data-product-id="' + (ConvertTo-HtmlEncoded $product.id) + '">'
        '        <span class="ceramics-card__media">'
        '            <img src="' + (ConvertTo-HtmlEncoded $product.image) + '" alt="' + $alt + '" loading="lazy">'
    )
    if ($product.available -eq $false) {
        $lines += '            <span class="ceramics-card__badge">Sold</span>'
    }
    $lines += @(
        '        </span>'
        '        <span class="ceramics-card__body">'
        '            <span class="ceramics-card__name">' + $name + '</span>'
        '            <span class="ceramics-card__price">' + (ConvertTo-HtmlEncoded (Format-Price $product)) + '</span>'
        '        </span>'
        '    </button>'
        '</li>'
    )
    return $lines
}

function Build-StructuredData($products) {
    $items = @()
    $position = 0
    foreach ($product in $products) {
        $position += 1
        $availability = if ($product.available -eq $false) { 'https://schema.org/SoldOut' } else { 'https://schema.org/InStock' }
        $description = if ($product.seoDescription) { $product.seoDescription } elseif ($product.description) { $product.description } else { $product.name }
        $items += [ordered]@{
            '@type'   = 'ListItem'
            position  = $position
            url       = $product.etsyUrl
            item      = [ordered]@{
                '@type'      = 'Product'
                name         = $product.name
                image        = if ($product.image -match '^https://') { $product.image } else { $siteUrl + '/' + ($product.image -replace '^/', '') }
                description  = $description
                brand        = [ordered]@{ '@type' = 'Brand'; name = 'Ceramics by Jaymi' }
                creator      = [ordered]@{ '@type' = 'Person'; name = 'Jaymi' }
                offers       = [ordered]@{
                    '@type'        = 'Offer'
                    priceCurrency  = if ($product.currency) { $product.currency } else { 'USD' }
                    price          = $product.price
                    availability   = $availability
                    url            = $product.etsyUrl
                }
            }
        }
    }
    return [ordered]@{
        '@context'   = 'https://schema.org'
        '@type'      = 'CollectionPage'
        name         = 'Handmade Pottery & Ceramics by Jaymi'
        url          = "$siteUrl/ceramics.html"
        description  = 'Handmade pottery and ceramics by Jaymi in Henderson, Nevada, sold through the Clay & Cactus Market Etsy shop.'
        isPartOf     = [ordered]@{ '@type' = 'WebSite'; name = 'Clay & Cactus Market'; url = "$siteUrl/" }
        about        = [ordered]@{ '@type' = 'Person'; name = 'Jaymi' }
        mainEntity   = [ordered]@{
            '@context'       = 'https://schema.org'
            '@type'          = 'ItemList'
            name             = 'Ceramics by Jaymi'
            itemListElement  = $items
        }
    }
}

$data = [System.IO.File]::ReadAllText($dataFile, $utf8NoBom) | ConvertFrom-Json
$products = @($data.products)

$blocks = @()
if ($products.Count -gt 0) {
    $blocks += '<p id="ceramics-status" class="ceramics__status" role="status" hidden></p>'
    $cardLines = @()
    foreach ($product in $products) {
        foreach ($line in (Build-Card $product)) {
            $cardLines += '    ' + $line
        }
    }
    $blocks += '<ul id="ceramics-grid" class="ceramics-grid">' + "`n" + ($cardLines -join "`n") + "`n" + '</ul>'
} else {
    $blocks += '<p id="ceramics-status" class="ceramics__status" role="status">New pieces are on the way. Check back soon!</p>'
    $blocks += '<ul id="ceramics-grid" class="ceramics-grid"></ul>'
}

$modalProducts = @()
foreach ($product in $products) {
    $modalProducts += [ordered]@{
        id          = $product.id
        name        = $product.name
        price       = $product.price
        currency    = if ($product.currency) { $product.currency } else { 'USD' }
        image       = $product.image
        imageAlt    = $product.imageAlt
        description = $product.description
        etsyUrl     = $product.etsyUrl
        available   = ($product.available -ne $false)
    }
}
$modalJson = (([ordered]@{ products = $modalProducts }) | ConvertTo-Json -Depth 5) -replace '</', '<\/'
$blocks += '<script type="application/json" id="ceramics-data">' + "`n" + $modalJson + "`n" + '</script>'

$ldJson = ((Build-StructuredData $products) | ConvertTo-Json -Depth 10) -replace '</', '<\/'
$blocks += '<script type="application/ld+json">' + "`n" + $ldJson + "`n" + '</script>'

$generatedLines = @()
foreach ($block in $blocks) {
    foreach ($line in (($block -replace "`r`n", "`n") -split "`n")) {
        if ($line.Trim().Length -gt 0) { $generatedLines += $indent + $line } else { $generatedLines += '' }
    }
}
$generated = ($generatedLines -join "`n")

$page = [System.IO.File]::ReadAllText($pageFile, $utf8NoBom)
$beginIndex = $page.IndexOf($beginMarker)
$endIndex = $page.IndexOf($endMarker)
if ($beginIndex -lt 0 -or $endIndex -lt 0 -or $endIndex -lt $beginIndex) {
    throw 'Could not find the CERAMICS generated markers in ceramics.html.'
}

$newline = if ($page -match "`r`n") { "`r`n" } else { "`n" }
if ($newline -eq "`r`n") { $generated = $generated -replace "`n", "`r`n" }

$next = $page.Substring(0, $beginIndex) + $beginMarker + $newline + $generated + $newline + $indent + $page.Substring($endIndex)
[System.IO.File]::WriteAllText($pageFile, $next, $utf8NoBom)
Write-Host ("Regenerated ceramics.html with {0} product(s) from data\ceramics.json." -f $products.Count)
