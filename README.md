# Répertoire IA

Répertoire personnel d'outils d'intelligence artificielle, de ressources
de formation et de vidéos pédagogiques.

## Contenu

-   `index.html` : page d'accueil du répertoire.
-   `monitor.py` : programme de vérification des liens.
-   `requirements.txt` : dépendances Python du programme.
-   `.github/workflows/weekly-link-check.yml` : automatisation GitHub
    Actions.

## Surveillance des liens

Le contrôle est prévu chaque semaine avec GitHub Actions. Il peut
également être lancé manuellement depuis l'onglet **Actions** du dépôt.

Les résultats et les mises à jour dépendent du bon fonctionnement de
`monitor.py` et du workflow. Vérifiez le rapport généré après chaque
exécution.

## Hébergement

Le site est destiné à être publié avec GitHub Pages depuis la branche
`principal`, à la racine du dépôt.

## Maintenance

Après toute modification des fichiers, vérifiez l'exécution du workflow
dans GitHub Actions et consultez les éventuels rapports d'erreur.
