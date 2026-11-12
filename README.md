# Portfolio — Ansoumana Thiam

Site portfolio d'Ansoumana « Ansou » Thiam, copywriter, creative director et brand strategist basé à Dakar.

## Structure

```
index.html            la page entière (HTML, CSS et JS dans un seul fichier)
img/
  ansou-cutout.png    portrait détouré du hero
  reel-1…6.jpg        miniatures des vidéos Instagram
  logos/              logos des clients (grille « Ils m'ont fait confiance »)
  avatars/            photos des commentateurs (voir le README du dossier)
scripts/              texte intégral des scripts, affiché dans le lecteur du site
  img/                images de la brand strategy Mission & Sens
tools/convert_docs.py convertit les exports Google Docs en fragments pour scripts/
```

## À savoir avant de modifier

- **Pas de `<!doctype>`, `<html>`, `<head>` ni `<body>`** dans `index.html` : la page est aussi publiée comme artefact Claude, qui ajoute ce squelette lui-même. Pour l'ouvrir directement dans un navigateur ou l'héberger (GitHub Pages, Netlify…), il faut envelopper le contenu dans un squelette HTML standard.
- **Couleurs** : tout passe par les variables CSS en haut du `<style>` (`--bg`, `--fg`, `--accent`, `--frame`…). Le thème clair est défini sur `:root`, le thème sombre deux fois (préférence système et `[data-theme="dark"]`). Modifier une couleur = modifier la variable dans les trois blocs.
- **Thème** : le bouton lune/soleil pose `data-theme` sur `<html>` et mémorise le choix dans `localStorage`.
- **Polices** (Google Fonts) : Big Shoulders Display (titres), Familjen Grotesk (texte), Courier Prime (labels façon scénario).
- **Projets** : chaque ligne `.shot` a un attribut `data-t` (`script`, `brand`, `video`) utilisé par les filtres. Les compteurs des filtres sont écrits à la main.

## Logos à remplacer si possible

Neurotech (LinkedIn), Teranga Tech Incub et Zadada (Instagram) viennent d'images de 100 à 150 px : des fichiers originaux fournis par les clients seraient plus nets.

## Scripts (lecteur intégré)

Les liens « DOC » des réalisations ouvrent le script dans un panneau du site. Le texte vient des Google Docs d'Ansou, copié dans `scripts/<nom>.html` ; la correspondance identifiant Google Doc → fichier est dans l'objet `SCRIPTS` du `<script>` de `index.html`. Le lien Google Docs reste accessible dans le panneau.

Pour mettre à jour un script après une modification du Google Doc :

```bash
curl -L -o exports/<nom>.html "https://docs.google.com/document/d/<ID>/export?format=html"
python3 tools/convert_docs.py exports scripts
```

Le lecteur charge les fichiers avec `fetch` : il faut servir le site par HTTP (un simple `python3 -m http.server` suffit en local), pas l'ouvrir en `file://`.
