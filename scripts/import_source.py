"""Normalize the authorized source capture without executing legacy code."""

import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
BASE = "/pro-ter-pa-v2/"
MANIFEST = json.loads((SOURCE / "manifest.json").read_text())


def canonical(value):
    return unquote(value).replace("18:12- 2023", "18-12-2023")


def clean(fragment):
    soup = BeautifulSoup(str(fragment), "html.parser")
    for element in soup.select("script,style,form,img,picture,iframe,input,textarea,button,svg"):
        element.decompose()
    allowed = {"p", "strong", "em", "a", "ul", "ol", "li", "br", "h2", "h3"}
    for element in list(soup.find_all(True)):
        if element.name not in allowed:
            element.unwrap()
            continue
        attributes = {}
        if element.name == "a":
            href = element.get("href", "")
            if href.startswith("javascript:"):
                element.unwrap()
                continue
            if href:
                if href == "http://www.local.fr":
                    href = "https://www.local.fr/"
                parts = urlsplit(href)
                if parts.netloc in ["www.pro-ter-pa.fr", "pro-ter-pa.fr"]:
                    route = parts.path.strip("/")
                    href = BASE + (route + "/" if route else "") + ("#" + parts.fragment if parts.fragment else "")
                attributes["href"] = href
            if element.get("id"):
                attributes["id"] = element["id"]
        element.attrs = attributes
    for paragraph in soup.select("p"):
        if not paragraph.get_text(strip=True):
            paragraph.decompose()
    return str(soup).strip()


def sections(soup):
    first = soup.h1
    footer = soup.select_one("#wt-container-instance-39549721")
    elements = list(soup.find_all(True))
    start, end = elements.index(first), elements.index(footer)
    result = []
    current = {"title": "", "html": "", "blocks": []}
    for element in elements[start + 1:end]:
        if element.name not in ["h2", "h3", "article"]:
            continue
        if element.find_parent(["article", "h1", "h2", "h3", "form"]):
            continue
        if element.name in ["h2", "h3"]:
            if current["title"] or current["html"]:
                result.append(current)
            current = {"title": element.get_text(" ", strip=True), "html": "", "blocks": []}
            continue
        fragment = clean(element.decode_contents())
        text = BeautifulSoup(fragment, "html.parser").get_text(" ", strip=True)
        if not text:
            continue
        if text in ["Chantier de terrassement", "Nos aménagements", "Assainissement", "Galerie photos"]:
            continue
        if not fragment.startswith(("<p", "<ul", "<ol")):
            fragment = "<p>" + fragment + "</p>"
        current["html"] += fragment
        current["blocks"].append(text)
    if current["title"] or current["html"]:
        result.append(current)
    return result


CAPTIONS = [
    "Une cour pavée, jusque dans les détails",
    "Extraction d’une souche à la pelleteuse",
    "Préparation d’un bassin de piscine",
    "Un muret de pierre pour dessiner le jardin",
    "Muret paysager en pierre naturelle",
    "Préparation d’une cour devant la maison",
    "Pavage au pied de la façade",
    "Un jardin avant son aménagement",
    "Muret arrondi et bordures paysagères",
    "Mise en œuvre du pavage",
    "Cour et bordures en cours de réalisation",
    "Finition d’une cour pavée",
    "Jardin arboré et espace extérieur",
    "Allée et jardin avant travaux",
    "Terrassement d’une tranchée",
    "Préparation du sol et niveaux",
    "Enrochement et bordure de jardin",
    "Installation d’un équipement d’assainissement",
    "Création d’un muret dans le jardin",
    "Revêtement et grille d’évacuation",
    "Aménagement d’une entrée de maison",
    "Muret et massifs paysagers",
    "Pierre naturelle et terrain préparé",
    "Terrassement d’un bassin de piscine",
    "Pose d’une cuve d’assainissement",
    "Cour et caniveau linéaire",
    "L’espace extérieur avant aménagement",
    "Bordures de pierre et préparation du sol",
    "Assemblage et finition des pavés",
    "Aménagement d’une cour de maison",
    "Pavage et évacuation des eaux",
    "Préparation du terrain devant la maison",
    "Pavage en cours de réalisation",
    "Un chantier au pied de la maison",
    "Finition du sol et évacuation des eaux",
    "Canalisation dans une tranchée",
    "Cour et bordures de pierre",
    "Réseau enterré en cours d’installation",
    "Les travaux de terrassement et d’aménagement — panorama",
    "Les chantiers Pro-Ter-Pa — panorama",
]

data = {"origin": MANIFEST["origin"], "pages": {}, "media": {}, "gallery": [], "coverage": {}}
asset_ids = {}
for index, asset in enumerate(MANIFEST["assets"]):
    key = hashlib.sha256(asset["url"].encode()).hexdigest()[:12]
    asset_ids[canonical(asset["url"])] = key
    destination = Path("docs/assets/originals") / Path(asset["file"]).name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / asset["file"], ROOT / destination)
    data["media"][key] = {
        "url": asset["url"],
        "original_name": asset["original_name"],
        "sha256": asset["sha256"],
        "original": {"source": str(destination), "path": str(destination.relative_to("docs"))},
        "original_alts": [],
    }
    if index < len(CAPTIONS):
        data["gallery"].append({"asset": key, "caption": CAPTIONS[index], "alt": CAPTIONS[index] + " — réalisation Pro-Ter-Pa"})

data["logo"] = asset_ids[canonical(next(a["url"] for a in MANIFEST["assets"] if a["original_name"] == "Logo.webp"))]
data["hero"] = data["gallery"][3]["asset"]
data["hero_alt"] = "Muret arrondi en pierre naturelle entourant un massif dans un jardin — réalisation Pro-Ter-Pa"
summaries = {
    "": "Terrassement, aménagements extérieurs et assainissement à Boisset-les-Prévanches et dans un rayon de 30 km. Découvrez les réalisations de Pro-Ter-Pa.",
    "chantier-de-terrassement": "Préparation de terrains, terrassement de piscines, fouilles, tranchées, enlèvement de terre et transport des déchets.",
    "nos-amenagements": "Dessouchage, terrains de pétanque, clôtures, murets et aménagement paysager dans l’Eure.",
    "assainissement": "Gestion des eaux usées, débouchage et détartrage des canalisations, vidange et pose de fosses septiques.",
    "galerie-photos": "Tous les chantiers en images : terrassement, cours, pavages, murets, aménagements paysagers et assainissement.",
    "contact": "Contactez Pascal Perrier au 07 62 05 89 45 ou à proterpa@orange.fr. Du lundi au vendredi de 8h à 18h.",
    "mentions-legales": "Informations légales de Pro-Ter-Pa, mentions du site d’origine et confidentialité de cette version hébergée sur GitHub Pages.",
}
shorts = {"": "Accueil", "chantier-de-terrassement": "Terrassement", "nos-amenagements": "Aménagements extérieurs", "assainissement": "Assainissement", "galerie-photos": "Réalisations", "contact": "Contact", "mentions-legales": "Mentions légales"}

for page in MANIFEST["pages"]:
    route = page["route"].strip("/")
    soup = BeautifulSoup((SOURCE / page["file"]).read_text(), "html.parser")
    for photo in soup.select("img[src]"):
        key = asset_ids.get(canonical(photo["src"]))
        if key and photo.get("alt") not in data["media"][key]["original_alts"]:
            data["media"][key]["original_alts"].append(photo.get("alt", ""))
    page_data = {
        "source_url": page["url"], "title": soup.h1.get_text(" ", strip=True),
        "short": shorts[route], "summary": summaries[route],
        "source_assets": [asset_ids[canonical(value)] for value in page["assets"]],
    }
    if route == "mentions-legales":
        legal_sections = []
        for section in soup.select(".legal-notes-container > .section"):
            heading = section.h2
            title = heading.get_text(" ", strip=True)
            heading.decompose()
            for h4 in section.select("h4"):
                h4.name = "h3"
            anchor = section.find("a", id=True)
            identifier = anchor.get("id") if anchor else ""
            if anchor:
                anchor.decompose()
            body = clean(section.decode_contents())
            legal_sections.append(f'<section><h2{(" id=" + html.escape(identifier)) if identifier else ""}>{html.escape(title)}</h2><div>{body}</div></section>')
        page_data["html"] = "".join(legal_sections)
        page_data["sections"] = []
    else:
        page_data["sections"] = sections(soup)
        page_data["html"] = "".join(
            (f'<h2>{html.escape(item["title"])}</h2>' if index == 0 else f'<h3>{html.escape(item["title"])}</h3>')
            + item["html"] for index, item in enumerate(page_data["sections"])
        )
    if route in ["chantier-de-terrassement", "nos-amenagements", "assainissement"]:
        photographs = [key for key in page_data["source_assets"] if any(item["asset"] == key for item in data["gallery"])]
        if route == "chantier-de-terrassement":
            photographs = [data["gallery"][2]["asset"], data["gallery"][1]["asset"]] + photographs
        page_data["photo"] = photographs[0]
        selected = next(item for item in data["gallery"] if item["asset"] == photographs[0])
        page_data["photo_alt"] = selected["alt"]
        page_data["gallery"] = [next(item for item in data["gallery"] if item["asset"] == key) for key in photographs]
    data["pages"][route] = page_data
    data["coverage"][route] = {"source_blocks": [item["title"] for item in page_data["sections"]] + [block for item in page_data["sections"] for block in item["blocks"]]}

home_soup = BeautifulSoup((SOURCE / "pages/index.html").read_text(), "html.parser")
data["maps"] = next(link["href"] for link in home_soup.select("a[href]") if "google.com/maps" in link["href"])
data["coverage"]["media_count"] = len(data["media"])
data["coverage"]["source_gallery_photos"] = 28
data["coverage"]["preserved_photographs_and_banners"] = len(data["gallery"])
data["coverage"]["original_form"] = {
    "url": "https://www.pro-ter-pa.fr/contact",
    "method": "POST",
    "captcha": True,
    "migration": "Direct email and phone; explicit link to original form. No submission endpoint copied or simulated.",
}
(SOURCE / "content.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Normalized {len(data['pages'])} pages, {len(data['media'])} media, {len(data['gallery'])} photographs and banners.")
