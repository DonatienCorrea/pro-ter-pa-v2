# Pro-Ter-Pa V2

Site français de Pro-Ter-Pa Perrier Pascal : terrassement, aménagements extérieurs et assainissement dans l’Eure.

**Site publié : https://donatiencorrea.github.io/pro-ter-pa-v2/**

## Publication

GitHub Pages publie directement la branche `main`, dossier `/docs`. Le site est statique, sans service tiers nécessaire à son affichage, sans traceur ajouté et sans formulaire simulé. Le téléphone et l’e-mail fonctionnent directement ; le formulaire historique reste accessible par un lien explicitement identifié.

Les sept routes d’origine sont conservées sous le préfixe `/pro-ter-pa-v2/`. Les mentions d’origine sont distinguées des informations concernant l’hébergement GitHub Pages et la confidentialité de la V2.

## Préservation

- `source/manifest.json` : inventaire de la capture d’origine et empreintes SHA-256.
- `source/pages/` : pages HTML de référence, non publiées et jamais exécutées ; valeurs des jetons éphémères du formulaire retirées.
- `source/content.json` : contenu normalisé, textes complets, provenance et correspondance des médias.
- `docs/preservation-inventory.json` : inventaire publié des pages, contenus et médias.
- `docs/assets/originals/` : les 55 fichiers images originaux, conservés à l’identique, avec des dérivés WebP pour l’affichage.

La galerie rassemble 49 photographies et montages : les 40 photographies et bannières préservées, dont les 28 photographies de la galerie d’origine, plus neuf visuels de chantier publiés par Pro-Ter-Pa sur [son profil public Google Maps](https://www.google.com/maps/contrib/114227483729375855289/photos/). Les montages sont affichés en entier, sans recadrage. Les 15 autres visuels d’origine (logos, carte et pictogrammes) et une variante du logo publiée sur Google restent accessibles dans la section dépliable de la galerie. Les légendes décrivent les images ; les anciens textes alternatifs sont conservés dans l’inventaire.

`source/google-photos.json` conserve la provenance, les catégories et les empreintes des dix images supplémentaires capturées sur le profil du propriétaire, sans photos de clients. Leurs octets d’origine sont dans `docs/assets/google/`. Seules ces dix images ont été importées, et non l’ensemble annoncé par Google. Aucun nom de fichier d’origine ni nouvelle licence n’est supposé. Le logo principal n’est pas remplacé ; la variante reste un document d’archive. Le lien d’itinéraire actuel pointe vers la fiche vérifiée du professionnel ; l’ancien lien reste consigné dans l’inventaire.

Les anciens CSS et JavaScript ont servi de référence de capture uniquement. Ils ne sont pas utilisés par la V2. La branche temporaire de transfert a été supprimée après import : les pages de référence, les contenus, le manifeste et les images nécessaires sont conservés dans `main`. Les contenus et visuels conservent leurs droits d’origine ; aucune licence libre sur ces éléments n’est accordée par cette refonte.

## Construction et vérification

Python 3 et Node.js sont nécessaires uniquement pour reconstruire et vérifier le site :

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci
npm run build
npm run verify
npm test
```

Le navigateur des tests est Google Chrome (`/usr/bin/google-chrome` sous Linux, application Google Chrome sous macOS), configurable avec `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`. Les fichiers publiés sont déjà construits et ne nécessitent aucune installation pour fonctionner.

`npm run verify` compare les textes substantiels de chacune des sept pages aux originaux, contrôle séparément les 55 empreintes des médias d’origine et les dix ajouts Google, les liens locaux, les ancres, les dimensions des images et les versions des ressources. La construction ajoute aux URL CSS/JS une empreinte de leur contenu : une nouvelle version ne dépend pas du cache d’une ancienne ressource. `npm test` vérifie les sept pages sur ordinateur et mobile, l’accessibilité WCAG AA avec axe, les images, les filtres et compteurs, les liens profonds et l’historique, les retours du presse-papiers, le retour du focus, le menu, les contacts, les animations réduites et les liens essentiels sans JavaScript. Les captures et résultats sont produits dans `test-results/`, non versionné.

`scripts/import_source.py` a normalisé la capture initiale ; il n’est pas nécessaire pour les reconstructions courantes. Il peut aussi utiliser les originaux déjà conservés dans `docs/assets/originals/`, sans archive de transfert. `source/gallery-categories.json` classe les photographies d’après leur contenu visuel, et non les noms de fichiers historiques parfois trompeurs.

## Confort de consultation

Les services utilisent leurs vraies photographies de chantier. La galerie propose des filtres avec compteurs et des liens partageables (`?categorie=assainissement&photo=…`), compatibles avec le retour du navigateur. Les photos originales restent accessibles sans JavaScript. Le bouton de copie indique explicitement les refus du presse-papiers et conserve un lien utilisable manuellement.

Sur mobile, une barre de contact réservant son propre espace permet d’appeler ou d’ouvrir la page du projet ; elle s’efface pendant la navigation et la consultation des photos. Les polices Barlow et Barlow Semi Condensed sont hébergées localement au format WOFF2, sous licence SIL Open Font License ; les licences sont incluses dans `docs/assets/fonts/`.
