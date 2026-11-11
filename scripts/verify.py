"""Verify exact original prose, local links and binary media preservation."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "/pro-ter-pa-v2/"


def normalize(text):
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+([.,;:!?])", r"\1", text)


source = json.loads((ROOT / "source/manifest.json").read_text())
inventory = json.loads((DOCS / "preservation-inventory.json").read_text())
checks = {"routes": 0, "source_text_blocks": 0, "original_media": 0, "local_links": 0}
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
assert len(inventory["media"]) == len(source["assets"]) == 55
assert (DOCS / ".nojekyll").is_file()
assert "91189438400013" in (DOCS / "mentions-legales/index.html").read_text()
print(json.dumps(checks, indent=2))
