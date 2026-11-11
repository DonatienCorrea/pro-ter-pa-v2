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

La galerie rassemble 40 photographies et bannières, dont toutes les 28 photographies de la galerie d’origine. Les 15 autres visuels (logos, carte et pictogrammes) sont accessibles dans la section dépliable de la galerie. Les légendes décrivent les images ; les anciens textes alternatifs sont conservés dans l’inventaire.

Les anciens CSS et JavaScript ont servi de référence de capture uniquement. Ils ne sont pas utilisés par la V2. L’archive de transfert complète reste dans la branche `source-import`, sans duplication de son archive binaire dans `main`. Les contenus et visuels conservent leurs droits d’origine ; aucune licence libre sur ces éléments n’est accordée par cette refonte.

## Construction et vérification

Python 3 et Node.js sont nécessaires uniquement pour reconstruire et vérifier le site :

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
npm run verify
npm test
```

Le navigateur des tests est Google Chrome, installé à `/usr/bin/google-chrome` dans l’environnement de validation. Les fichiers publiés sont déjà construits et ne nécessitent aucune installation pour fonctionner.

`npm run verify` compare les textes substantiels de chacune des sept pages aux originaux, contrôle les 55 empreintes des médias, les liens locaux, les ancres et les dimensions des images. `npm test` vérifie les sept pages sur ordinateur et mobile, l’accessibilité WCAG AA avec axe, les images, le menu, la galerie au clavier, le retour du focus, les contacts et les liens essentiels sans JavaScript. Les captures et résultats sont produits dans `test-results/`, non versionné.

`scripts/import_source.py` a normalisé la capture initiale. Il requiert les médias de l’archive de transfert dans `source/assets/` ; il n’est pas nécessaire pour les reconstructions courantes.
