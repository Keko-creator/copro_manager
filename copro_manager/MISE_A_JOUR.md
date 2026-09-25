# Mise à jour de l'application sans perdre les données

Toutes les données saisies sont dans **un seul fichier** :
`instance\copro_manager.db`. Le code de l'application et les données sont deux
choses séparées : mettre à jour le code ne touche jamais la base.

## Procédure de mise à jour (sur le poste d'hébergement)

1. **Sauvegarde de sécurité** (30 secondes, à faire systématiquement) :
   double-cliquer sur `sauvegarde.bat`, ou copier manuellement
   `instance\copro_manager.db` ailleurs.
2. **Arrêter le serveur** : aller dans la console du serveur et faire CTRL+C.
3. **Récupérer la nouvelle version** :
   - si installé via Git : `git pull`
   - sinon : remplacer les fichiers du code par la nouvelle version, **sans
     toucher aux dossiers `instance\` et `sauvegardes\`**
4. **Relancer** : double-cliquer sur `demarrer.bat`.

C'est tout. Les données saisies restent intactes.

## Règles d'or

- **Ne jamais** supprimer ni remplacer `instance\copro_manager.db` lors d'une
  mise à jour, sauf restauration explicite d'une sauvegarde.
- **Ne jamais** mettre `instance\` dans Git, OneDrive ou un dossier synchronisé.
- Si un nouveau champ doit être ajouté aux fiches (ex. une nouvelle colonne),
  demander le changement **avant** que la saisie ne commence, ou vérifier que la
  mise à jour prévoit une migration qui préserve les données existantes.

## En cas de problème

Si après une mise à jour l'application affiche une erreur ou des données
manquantes :

1. Arrêter le serveur (CTRL+C).
2. Restaurer la dernière sauvegarde : copier le fichier le plus récent de
   `sauvegardes\` dans `instance\copro_manager.db` (remplacer l'existant).
3. Relancer `demarrer.bat`.
4. Signaler le problème pour qu'il soit corrigé.

## Restaurer sur un nouveau poste

1. Installer l'application (voir `INSTALLATION.md`).
2. **Avant le premier démarrage**, copier la sauvegarde de la base dans
   `instance\copro_manager.db`.
3. Lancer `demarrer.bat` : les données sont là.

> ⚠️ La base est un fichier « à copier froid » : ne la copier que serveur
> arrêté, sinon le fichier copié peut être incomplet.
