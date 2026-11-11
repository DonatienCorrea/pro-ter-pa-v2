"""Build the static site from the preserved, reviewed original-site inventory."""

import hashlib
import html
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "/pro-ter-pa-v2/"
SITE = "https://donatiencorrea.github.io/pro-ter-pa-v2/"
BUSINESS_MAPS = "https://www.google.com/maps/place/Pro-ter-pa+Perrier+Pascal/@48.9606852,1.336873,17z/data=!3m1!4b1!4m6!3m5!1s0x8869340ff8acce9f:0x84d9202bb15a14e1!8m2!3d48.9606852!4d1.336873!16s%2Fg%2F11krfhtlq0"
NAV = [
    ("", "Accueil"),
    ("chantier-de-terrassement", "Terrassement"),
    ("nos-amenagements", "Aménagements"),
    ("assainissement", "Assainissement"),
    ("galerie-photos", "Réalisations"),
    ("contact", "Parlons de votre projet"),
]
CATEGORIES = {
    "toutes": "Toutes",
    "terrassement": "Terrassement",
    "amenagements": "Aménagements",
    "assainissement": "Assainissement",
}


def escape(value):
    return html.escape(str(value), quote=True)


def url(route=""):
    return BASE + (route.strip("/") + "/" if route else "")


def versioned_asset(path):
    digest = hashlib.sha256((DOCS / path).read_bytes()).hexdigest()[:12]
    return f"{BASE}{path}?v={digest}"


def image(asset, alt, variant="display", eager=False, css=""):
    media = DATA["media"][asset]
    chosen = media.get(variant, media["original"])
    return (
        f'<img src="{BASE}{escape(chosen["path"])}" alt="{escape(alt)}" '
        f'width="{chosen["width"]}" height="{chosen["height"]}" '
        f'loading="{"eager" if eager else "lazy"}" decoding="async"'
        f'{" fetchpriority=high" if eager else ""}'
        f'{" class=" + escape(css) if css else ""}>'
    )


def header(route):
    links = "".join(
        f'<a href="{url(target)}"'
        f'{" aria-current=page" if target == route else ""}'
        f'{" class=nav-contact" if target == "contact" else ""}>'
        f"{label}</a>"
        for target, label in NAV
    )
    return (
        '<a class="skip" href="#contenu">Aller au contenu</a>'
        '<header class="site-header">'
        f'<a class="brand" href="{BASE}" aria-label="Pro-Ter-Pa — Accueil">'
        f'{image(DATA["logo"], "Pro-Ter-Pa Perrier Pascal", eager=False)}</a>'
        '<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu</button>'
        f'<nav class="nav" id="navigation" aria-label="Navigation principale">{links}</nav>'
        "</header>"
    )


def footer():
    links = "".join(f'<a href="{url(route)}">{label}</a>' for route, label in NAV[1:5])
    return (
        '<footer class="site-footer"><div class="footer-top">'
        '<div><a class="footer-title" href="' + BASE + '">Pro-Ter-Pa<span translate="no">.</span></a>'
        '<p>Perrier Pascal<br>Terrassement · Aménagements extérieurs · Assainissement</p></div>'
        '<nav aria-label="Services et réalisations">' + links + "</nav>"
        '<div><a href="tel:+33762058945">07 62 05 89 45</a><br>'
        '<a href="mailto:proterpa@orange.fr">proterpa@orange.fr</a>'
        '<p>7 bis rue des Bois<br>27120 Boisset-les-Prévanches<br>Du lundi au vendredi, de 8h à 18h</p></div>'
        '</div><div class="footer-bottom"><span>Pro-Ter-Pa Perrier Pascal · Boisset-les-Prévanches</span>'
        f'<a href="{url("mentions-legales")}">Mentions légales & confidentialité</a></div></footer>'
    )


def contact_band():
    return (
        '<section class="contact-band" aria-labelledby="contact-title">'
        '<div><h2 id="contact-title">Et si l’on parlait de votre terrain ?</h2>'
        '<p>Un projet de terrassement, d’aménagement ou d’assainissement ? Contactez Pascal Perrier.</p></div>'
        '<div><a class="contact-phone" href="tel:+33762058945">07 62 05 89 45</a>'
        '<p>Du lundi au vendredi, de 8h à 18h</p><div class="actions">'
        f'<a class="button" href="{url("contact")}">Parlons de votre projet</a>'
        '<a class="button secondary" href="mailto:proterpa@orange.fr">Écrire un e-mail</a>'
        "</div></div></section>"
    )


def gallery(items):
    cards = []
    for item in items:
        original = DATA["media"][item["asset"]]["original"]
        label = item["caption"]
        cards.append(
            f'<figure{" class=uncropped" if item.get("uncropped") else ""} data-gallery-item data-categories="{escape(" ".join(item_categories(item)))}">'
            f'<a href="{BASE}{escape(original["path"])}" data-photo="{item["asset"]}" data-caption="{escape(label)}"'
            f' data-width="{original["width"]}" data-height="{original["height"]}"'
            f' aria-label="Agrandir : {escape(label)}">'
            f'{image(item["asset"], item["alt"], "thumb")}</a>'
            f'<figcaption>{escape(label)}'
            + ('<span class="photo-credit">Publié par Pro-Ter-Pa sur Google</span>' if item.get("source_type") == "google-owner" else "")
            + "</figcaption></figure>"
        )
    return '<div class="gallery">' + "".join(cards) + "</div>"


def item_categories(item):
    return [category for category, assets in PHOTO_CATEGORIES.items() if item["asset"] in assets]


def gallery_filters():
    buttons = "".join(
        f'<button type="button" data-filter="{category}" aria-pressed="{"true" if category == "toutes" else "false"}">'
        f'{label} <span aria-hidden="true">{len(DATA["gallery"]) if category == "toutes" else len(PHOTO_CATEGORIES[category])}</span></button>'
        for category, label in CATEGORIES.items()
    )
    return (
        f'<div class="gallery-tools"><div data-gallery-filters role="group" aria-label="Filtrer les réalisations" hidden>{buttons}</div>'
        f'<p data-gallery-count aria-live="polite" aria-atomic="true">{len(DATA["gallery"])} photos · Toutes les réalisations</p></div>'
    )


def quick_contact(route):
    if route in ["contact", "mentions-legales"]:
        return ""
    return (
        '<nav class="quick-contact" aria-label="Contact rapide">'
        '<a href="tel:+33762058945">Appeler <span class="visually-hidden">Pro-Ter-Pa au 07 62 05 89 45</span>'
        '<span aria-hidden="true">↗</span></a>'
        f'<a href="{url("contact")}">Votre projet <span aria-hidden="true">↗</span></a></nav>'
    )


def lightbox():
    return (
        '<dialog id="lightbox" aria-label="Photographies des réalisations">'
        '<div class="lightbox-top"><p>Les réalisations Pro-Ter-Pa · <span data-counter aria-live="polite"></span></p>'
        '<div class="lightbox-buttons"><button data-previous aria-label="Photographie précédente">←</button>'
        '<button data-next aria-label="Photographie suivante">→</button>'
        '<button data-close aria-label="Fermer la photographie">×</button></div></div>'
        f'{image(DATA["hero"], "", "thumb", css="lightbox-image")}'
        '<div class="lightbox-footer"><p class="lightbox-caption"></p>'
        '<button type="button" class="copy-link" data-copy>Copier le lien</button>'
        '<a data-share-link>Lien de cette photo</a>'
        '<p class="copy-status" data-copy-status role="status" aria-live="polite"></p></div></dialog>'
    )


def media_archive():
    photographs = {item["asset"] for item in DATA["gallery"]}
    items = "".join(
        f'<figure><a href="{BASE}{escape(media["original"]["path"])}">'
        f'{image(key, media.get("caption") or media["original_name"].removesuffix(".webp"), "thumb")}</a>'
        f'<figcaption>{escape(media.get("caption") or media["original_name"])}</figcaption></figure>'
        for key, media in DATA["media"].items() if key not in photographs
    )
    return (
        '<section class="section media-archive"><details><summary>Les autres visuels du site d’origine</summary>'
        '<p>Logos, pictogrammes et carte : tous les éléments d’origine sont conservés et consultables ci-dessous. '
        'Une variante du logo publiée sur Google est également conservée à titre d’archive ; '
        'les mentions présentes dans ce visuel ne constituent pas de nouvelles déclarations sur cette version.</p>'
        f'<div class="archive-grid">{items}</div></details>'
        f'<p><a href="{BASE}preservation-inventory.json">Consulter l’inventaire complet des pages et des visuels (JSON)</a></p></section>'
    )


def service_list():
    return '<div class="service-list">' + "".join(
        f'<div class="service-row"><a class="service-visual" href="{url(route)}" tabindex="-1" aria-hidden="true">'
        f'{image(asset, "", "thumb")}</a><h3><a href="{url(route)}">{escape(section["title"])}</a></h3>'
        f'<div class="prose">{section["html"]}</div><a class="arrow" href="{url(route)}" aria-label="Découvrir : {escape(section["title"])}">↗</a></div>'
        for route, section, asset in zip(
            ["chantier-de-terrassement", "nos-amenagements", "assainissement"],
            DATA["pages"][""]["sections"][1:4],
            [DATA["gallery"][2]["asset"], DATA["gallery"][3]["asset"], DATA["gallery"][24]["asset"]],
        )
    ) + "</div>"


def home():
    page = DATA["pages"][""]
    return (
        '<section class="hero"><div class="hero-copy">'
        '<h1>Votre terrain.<br>Tout son potentiel.</h1>'
        '<p>Terrassement, aménagements extérieurs et assainissement à Boisset-les-Prévanches et ses alentours.</p>'
        '<div class="actions">'
        f'<a class="button" href="{url("contact")}">Parlons de votre projet</a>'
        f'<a class="button secondary" href="{url("galerie-photos")}">Voir les réalisations</a>'
        '</div></div><div class="hero-photo">'
        f'{image(DATA["hero"], DATA["hero_alt"], eager=True)}'
        '<div class="photo-caption"><span>Les chantiers de Pro-Ter-Pa</span><span>Boisset-les-Prévanches · Eure</span></div>'
        '</div></section><div class="territory-bar">'
        '<strong>Un professionnel pour vos travaux extérieurs.</strong>'
        '<span>Dans un rayon de 30 km autour de Boisset-les-Prévanches</span></div>'
        f'<section class="section intro"><h2>{escape(page["title"])}</h2>'
        f'<div class="prose"><h3>{escape(page["sections"][0]["title"])}</h3>{page["sections"][0]["html"]}</div></section>'
        '<section class="section" id="savoir-faire"><div class="section-heading">'
        '<h2>Les travaux prennent forme.</h2><p>Trois savoir-faire, un même interlocuteur.</p></div>'
        + service_list()
        + '</section><section class="section intro strengths"><h2>Nos points forts.</h2>'
        f'<div class="prose">{page["sections"][4]["html"]}</div>'
        + '</section><section class="section photo-section"><div class="section-heading">'
        '<h2>Sur le terrain, en images.</h2>'
        f'<a class="text-link" href="{url("galerie-photos")}">Toutes les réalisations ↗</a></div>'
        + gallery([GOOGLE_PROJECTS[-1], GOOGLE_PROJECTS[1]] + DATA["gallery"][:3])
        + '</section><section class="section intro"><h2>À vos côtés, dans l’Eure.</h2>'
        f'<div class="prose"><h3>{escape(page["sections"][5]["title"])}</h3>{page["sections"][5]["html"]}'
        '<p>7 bis rue des Bois, 27120 Boisset-les-Prévanches</p>'
        f'<p><a href="{escape(BUSINESS_MAPS)}" rel="noopener" target="_blank">Voir l’itinéraire sur Google Maps (nouvel onglet) ↗</a></p>'
        "</div></section>"
        + contact_band()
    )


def page_title(route):
    page = DATA["pages"][route]
    return (
        f'<div class="breadcrumb"><a href="{BASE}">Accueil</a> / {escape(page["short"])}</div>'
        f'<section class="page-title"><h1>{escape(page["title"])}</h1>'
        f'<p>{escape(page["summary"])}</p></section>'
    )


def service(route):
    page = DATA["pages"][route]
    return (
        page_title(route)
        + '<section class="section service-detail">'
        f'<div class="prose">{page["html"]}<div class="actions">'
        f'<a class="button" href="{url("contact")}">Discutons de vos travaux</a></div></div>'
        '<figure class="detail-photo">'
        f'{image(page["photo"], page["photo_alt"])}'
        f'<figcaption>{escape(page["photo_alt"])}</figcaption></figure></section>'
        + (('<section class="section photo-section"><div class="section-heading"><h2>Les réalisations en images.</h2>'
            f'<a class="text-link" href="{url("galerie-photos")}">Voir toute la galerie ↗</a></div>'
            + gallery(page["gallery"]) + '</section>') if page.get("gallery") else "")
        + contact_band()
    )


def contact():
    return (
        page_title("contact")
        + '<section class="section contact-layout"><div class="contact-details">'
        '<h2>Contactez Pascal Perrier.</h2>'
        '<a class="contact-phone" href="tel:+33762058945">07 62 05 89 45</a>'
        '<dl><dt>E-mail</dt><dd><a href="mailto:proterpa@orange.fr">proterpa@orange.fr</a></dd>'
        '<dt>Adresse</dt><dd>Pro-Ter-Pa Perrier Pascal<br>7 bis rue des Bois<br>27120 Boisset-les-Prévanches</dd>'
        '<dt>Horaires</dt><dd>Du lundi au vendredi, de 8h à 18h</dd>'
        '<dt>Zone d’intervention</dt><dd>Dans un rayon de 30 km autour de Boisset-les-Prévanches : '
        'Vernon, Saint-André-de-l’Eure, Pacy-sur-Eure, Évreux, Bueil et Serez.</dd></dl>'
        f'<div class="actions"><a class="button secondary" href="{escape(BUSINESS_MAPS)}" target="_blank" rel="noopener">'
        'Voir l’itinéraire<span class="visually-hidden"> (nouvel onglet)</span></a></div></div>'
        '<aside class="contact-note"><h2>Votre projet commence par un échange.</h2>'
        '<p>Décrivez votre besoin, le lieu des travaux et vos coordonnées directement par e-mail ou par téléphone.</p>'
        '<a class="button" href="mailto:proterpa@orange.fr">Écrire à Pro-Ter-Pa</a>'
        '<p class="legacy-content">Cette nouvelle version ne recueille aucune demande via un formulaire. '
        'Le lien ci-dessus ouvre votre messagerie ; aucun message n’est envoyé automatiquement.</p>'
        '<p>Vous préférez le formulaire du site d’origine ? Il reste accessible sur sa page de contact.</p>'
        '<a class="text-link" href="https://www.pro-ter-pa.fr/contact" target="_blank" rel="noopener">'
        'Ouvrir le formulaire d’origine (nouvel onglet) ↗</a></aside></section>'
        '<section class="section"><div class="prose"><h2>Informations du site d’origine</h2>'
        '<p>Le site d’origine propose de laisser un message avec cette indication :</p><blockquote>'
        + DATA["pages"]["contact"]["html"] + "</blockquote></div></section>"
    )


def legal():
    return (
        page_title("mentions-legales")
        + '<article class="section legal prose"><h2>Cette version du site</h2>'
        '<p>Cette version V2 conserve les informations et photographies du site '
        '<a href="https://www.pro-ter-pa.fr/">www.pro-ter-pa.fr</a>. '
        'Les informations historiques du site d’origine sont reproduites ci-dessous et identifiées comme telles.</p>'
        '<h3>Hébergement de la V2</h3><p>Cette version est hébergée par GitHub Pages, un service de GitHub, Inc., '
        '88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis. '
        '<a href="https://docs.github.com/fr/site-policy/privacy-policies/github-general-privacy-statement">'
        'Consulter la politique de confidentialité de GitHub</a>.</p>'
        '<h3>Données personnelles et cookies</h3>'
        '<p>La V2 ne comporte ni traceur publicitaire, ni outil de mesure d’audience, ni formulaire de collecte. '
        'Aucun cookie applicatif n’est déposé par cette version. GitHub peut traiter des données techniques, '
        'dont l’adresse IP, pour assurer l’hébergement et sa sécurité, conformément à sa politique de confidentialité.</p>'
        '<p>Les liens e-mail et téléphone utilisent les applications de votre appareil. '
        'Google Maps et le formulaire du site d’origine sont des services externes : '
        'leurs propres politiques s’appliquent après ouverture de ces liens.</p>'
        '<h3>Polices de caractères</h3><p>Barlow et Barlow Semi Condensed sont hébergées localement, '
        'sous licence SIL Open Font License 1.1. '
        f'<a href="{BASE}assets/fonts/barlow-LICENSE.txt">Licence Barlow</a> · '
        f'<a href="{BASE}assets/fonts/barlow-semi-condensed-LICENSE.txt">Licence Barlow Semi Condensed</a>.</p>'
        '<h2>Mentions du site d’origine</h2>'
        '<p>Les mentions suivantes décrivent l’édition, la réalisation et l’hébergement du site d’origine. '
        'Les références à Local.fr et à OVH ne désignent pas la réalisation ou l’hébergement de cette V2.</p>'
        '<div class="legacy-content">'
        + DATA["pages"]["mentions-legales"]["html"]
        +         '<p>© 2026 PRO-TER-PA. Liens de gestion du site d’origine : <a href="https://www.localetmoi.fr" target="_blank" rel="noopener">'
        'Mettre à jour mon site internet (nouvel onglet)</a>. Site d’origine créé par '
        '<a href="https://www.local.fr/" target="_blank" rel="noopener">Local.fr (nouvel onglet)</a>.</p></div></article>'
    )


def render(route, body):
    page = DATA["pages"][route]
    title = page["title"] + " | Pro-Ter-Pa"
    description = page["summary"]
    contract = (
        "<!-- THESIS: A landscape-maker's photographic monograph, not a generic contractor template.\n"
        "OWN-WORLD: Chalk white, woodland green and fresh chartreuse; bold practical sans, generous photographs and open rows.\n"
        "STORY: Understand the three services, inspect real work, contact Pascal directly.\n"
        "FIRST VIEWPORT: Oversized left-aligned promise, right-hand real chantier photograph, green contact action and lime image caption.\n"
        "FORM: Landscape monograph, grounded candidate 3; seed 3cd0af47; photographic facing-page staging. -->"
    )
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{escape(title)}</title><meta name="description" content="{escape(description)}">'
        '<meta name="theme-color" content="#f8f9f4">'
        f'<link rel="canonical" href="{SITE}{route + "/" if route else ""}">'
        f'<meta property="og:title" content="{escape(title)}">'
        f'<meta property="og:description" content="{escape(description)}">'
        '<meta property="og:type" content="website"><meta property="og:locale" content="fr_FR">'
        f'<meta property="og:url" content="{SITE}{route + "/" if route else ""}">'
        f'<meta property="og:image" content="{SITE}{DATA["media"][DATA["hero"]]["display"]["path"]}">'
        f'<link rel="icon" href="{BASE}{DATA["media"][DATA["logo"]]["original"]["path"]}">'
        f'<link rel="preload" href="{BASE}assets/fonts/barlow-semi-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>'
        f'<link rel="stylesheet" href="{versioned_asset("assets/site.css")}">'
        f'<script src="{versioned_asset("assets/site.js")}" defer></script>'
        '<noscript><style>.menu-toggle{display:none}.nav{display:flex;position:static;flex-wrap:wrap}'
        '.site-header{position:static;flex-wrap:wrap}.nav a{font-size:14px}</style></noscript>'
        f'</head><body{" class=has-quick-contact" if quick_contact(route) else ""}>' + contract + header(route)
        + '<p class="page-notice" data-gallery-status role="status" hidden></p>'
        + f'<main id="contenu" tabindex="-1"{" class=gallery-page" if route == "galerie-photos" else ""}>'
        + body + "</main>" + footer() + quick_contact(route) + (lightbox() if "data-photo" in body else "") + "</body></html>"
    )


def create_variants(data):
    """Keep original binaries intact and create fast, local image derivatives."""
    for media in data["media"].values():
        original = media["original"]
        source = ROOT / original["source"]
        destination = DOCS / original["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        with Image.open(source) as raw:
            original["width"], original["height"] = raw.size
            for name, bound in [("display", 1600), ("thumb", 800)]:
                target = destination.with_name(destination.stem + f"-{name}.webp")
                photo = ImageOps.exif_transpose(raw)
                if photo.mode not in ["RGB", "RGBA"]:
                    photo = photo.convert("RGBA" if "transparency" in photo.info else "RGB")
                photo.thumbnail((bound, bound), Image.Resampling.LANCZOS)
                photo.save(target, "WEBP", quality=86, method=6)
                media[name] = {
                    "path": str(target.relative_to(DOCS)),
                    "width": photo.width,
                    "height": photo.height,
                }
        original["sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()


if __name__ == "__main__":
    DATA = json.loads((ROOT / "source/content.json").read_text())
    DATA["current_maps"] = BUSINESS_MAPS
    PHOTO_CATEGORIES = json.loads((ROOT / "source/gallery-categories.json").read_text())
    google = json.loads((ROOT / "source/google-photos.json").read_text())
    GOOGLE_PROJECTS = []
    for photo in google["photos"]:
        key = "google-" + photo["sha256"][:12]
        path = Path("assets/google") / photo["file"]
        original = DOCS / path
        if hashlib.sha256(original.read_bytes()).hexdigest() != photo["sha256"]:
            raise ValueError(f"Imported Google image altered: {photo['file']}")
        DATA["media"][key] = {
            "url": photo["download_url"], "source_type": google["source_type"],
            "publisher": google["publisher"], "profile_url": google["profile_url"],
            "photo_id": photo["photo_id"], "role": photo["role"], "caption": photo["caption"],
            "original_name": photo["original_filename"], "sha256": photo["sha256"],
            "original": {"source": str(Path("docs") / path), "path": str(path)},
        }
        if photo["role"] == "project-photo":
            item = {
                "asset": key, "caption": photo["caption"], "alt": photo["caption"] + " — photographie publiée par Pro-Ter-Pa sur Google",
                "categories": photo["categories"], "source_type": "google-owner", "uncropped": True,
            }
            GOOGLE_PROJECTS.append(item)
            DATA["gallery"].append(item)
            for category in photo["categories"]:
                PHOTO_CATEGORIES[category].append(key)
    DATA["google_photos"] = {
        "profile_url": google["profile_url"], "place_url": google["place_url"],
        "selection_note": google["selection_note"], "captured_count": len(google["photos"]),
        "project_images_added": len(GOOGLE_PROJECTS),
    }
    DATA["coverage"].update({
        "original_media_count": 55, "additional_google_media_count": len(google["photos"]),
        "media_count": len(DATA["media"]), "original_project_images": 40,
        "preserved_photographs_and_banners": len(DATA["gallery"]),
    })
    all_photos = {item["asset"] for item in DATA["gallery"]}
    if set().union(*(set(assets) for assets in PHOTO_CATEGORIES.values())) != all_photos:
        raise ValueError("Gallery categories must cover exactly the preserved photographs.")
    for item in DATA["gallery"]:
        item["categories"] = item_categories(item)
    fonts = DOCS / "assets/fonts"
    fonts.mkdir(exist_ok=True)
    for package, files in {
        "barlow": ["barlow-latin-400-normal.woff2", "barlow-latin-700-normal.woff2"],
        "barlow-semi-condensed": ["barlow-semi-condensed-latin-700-normal.woff2"],
    }.items():
        package_root = ROOT / "node_modules/@fontsource" / package
        for file in files:
            shutil.copyfile(package_root / "files" / file, fonts / file)
        shutil.copyfile(package_root / "LICENSE", fonts / f"{package}-LICENSE.txt")
    create_variants(DATA)
    bodies = {
        "": home(),
        "chantier-de-terrassement": service("chantier-de-terrassement"),
        "nos-amenagements": service("nos-amenagements"),
        "assainissement": service("assainissement"),
        "galerie-photos": page_title("galerie-photos") + '<section class="section gallery-section">' + gallery_filters() + '<div class="prose gallery-intro">' + DATA["pages"]["galerie-photos"]["html"] + '<p>9 visuels de chantier publiés par Pro-Ter-Pa sur Google complètent la galerie d’origine. <a href="' + escape(google["profile_url"]) + '" target="_blank" rel="noopener">Voir les photos publiques de Pro-Ter-Pa sur Google Maps (nouvel onglet) ↗</a></p></div>' + gallery(DATA["gallery"]) + '</section>' + media_archive() + contact_band(),
        "contact": contact(),
        "mentions-legales": legal(),
    }
    for route, body in bodies.items():
        path = DOCS / route / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(route, body))
    (DOCS / "preservation-inventory.json").write_text(json.dumps(DATA, ensure_ascii=False, indent=2))
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{SITE}{route + '/' if route else ''}</loc></url>" for route in bodies)
        + "</urlset>"
    )
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    print(f"Built {len(bodies)} routes; preserved 55 original image assets and added {len(google['photos'])} owner-published Google images.")
