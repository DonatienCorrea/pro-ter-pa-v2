"""Verify exact original prose, local links and binary media preservation."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "/pro-ter-pa-v2/"


def normalize(text):
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+([.,;:!?])", r"\1", text)


source = json.loads((ROOT / "source/manifest.json").read_text())
inventory = json.loads((DOCS / "preservation-inventory.json").read_text())
checks = {"routes": 0, "source_text_blocks": 0, "original_media": 0, "additional_google_media": 0, "versioned_assets": 0, "local_links": 0}
for page in source["pages"]:
    route = page["route"].strip("/")
    old = BeautifulSoup((ROOT / "source" / page["file"]).read_text(), "html.parser")
    new = BeautifulSoup((DOCS / route / "index.html").read_text(), "html.parser")
    assert new.html["lang"] == "fr"
    assert len(new.select("h1")) == 1
    assert all(image.has_attr("alt") and image.has_attr("width") and image.has_attr("height") for image in new.select("img"))
    text = normalize(new.main.get_text(" ", strip=True))
    if route == "mentions-legales":
        blocks = [section.get_text(" ", strip=True) for section in old.select(".legal-notes-container > .section")]
    else:
        elements = list(old.find_all(True))
        start = elements.index(old.h1)
        stop = elements.index(old.select_one("#wt-container-instance-39549721"))
        blocks = [
            element.get_text(" ", strip=True)
            for element in elements[start:stop]
            if element.name in ["h1", "h2", "h3", "article"]
            and not element.find_parent(["article", "h1", "h2", "h3", "form"])
            and len(element.get_text(" ", strip=True)) >= 40
        ]
    for block in blocks:
        assert normalize(block) in text, f"Original text missing from {route}: {block}"
        checks["source_text_blocks"] += 1
    for element in new.select("a[href],img[src],script[src],link[href]"):
        value = element.get("href", element.get("src"))
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme in ["https", "mailto", "tel"], f"Unexpected protocol: {value}"
            continue
        assert parsed.path.startswith(BASE) or not parsed.path, f"Incorrect base path: {value}"
        path = DOCS / unquote(parsed.path.removeprefix(BASE)) if parsed.path else DOCS / route / "index.html"
        if path.is_dir():
            path = path / "index.html"
        assert path.is_file(), f"Missing internal target: {value}"
        if path in [DOCS / "assets/site.css", DOCS / "assets/site.js"]:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
            assert parse_qs(parsed.query) == {"v": [digest]}, f"Stale shared asset version: {value}"
            checks["versioned_assets"] += 1
        if parsed.fragment and path.suffix == ".html":
            target = BeautifulSoup(path.read_text(), "html.parser")
            assert target.find(id=parsed.fragment), f"Missing fragment: {value}"
        checks["local_links"] += 1
    checks["routes"] += 1

for asset in source["assets"]:
    media = next(item for item in inventory["media"].values() if item["url"] == asset["url"])
    path = DOCS / media["original"]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"]
    checks["original_media"] += 1

gallery_source = BeautifulSoup((ROOT / "source/pages/galerie-photos.html").read_text(), "html.parser")
gallery_urls = {image["src"] for image in gallery_source.select("img[src]") if "/18-12-2023/" in image["src"]}
preserved_gallery = {inventory["media"][item["asset"]]["url"] for item in inventory["gallery"]}
assert gallery_urls <= preserved_gallery, gallery_urls - preserved_gallery
assert len(source["assets"]) == 55
original_content = json.loads((ROOT / "source/content.json").read_text())
assert len(original_content["gallery"]) == 40
assert {item["asset"] for item in original_content["gallery"]} <= {item["asset"] for item in inventory["gallery"]}
assert len(inventory["gallery"]) == 49
google = json.loads((ROOT / "source/google-photos.json").read_text())
assert len(google["photos"]) == 10
published_gallery = BeautifulSoup((DOCS / "galerie-photos/index.html").read_text(), "html.parser")
gallery_ids = {item["data-photo"] for item in published_gallery.select(".gallery [data-photo]")}
assert len(gallery_ids) == 49
for photo in google["photos"]:
    key = "google-" + photo["sha256"][:12]
    media = inventory["media"][key]
    assert media["profile_url"] == google["profile_url"]
    assert media["url"] == photo["download_url"]
    assert media["original_name"] is None
    assert hashlib.sha256((DOCS / media["original"]["path"]).read_bytes()).hexdigest() == photo["sha256"]
    assert (media["original"]["width"], media["original"]["height"]) == (photo["width"], photo["height"])
    assert (key in gallery_ids) == (photo["role"] == "project-photo")
    checks["additional_google_media"] += 1
assert len(inventory["media"]) == 65
assert len(published_gallery.select(".archive-grid figure")) == 16
assert {BASE + media["original"]["path"] for media in inventory["media"].values()} <= {
    link["href"] for link in published_gallery.select("a[href]")
}
assert published_gallery.find("a", href=google["profile_url"])
assert checks["versioned_assets"] == 14
assert (DOCS / ".nojekyll").is_file()
assert "91189438400013" in (DOCS / "mentions-legales/index.html").read_text()
print(json.dumps(checks, indent=2))
