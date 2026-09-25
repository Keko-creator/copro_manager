# Copro Manager — Installation multi-utilisateurs (Windows)

Ce document explique comment installer l'application sur **un poste d'hébergement**
(PC ou VM Windows allumé en permanence). Les autres utilisateurs y accèdent ensuite
depuis leur navigateur, sans rien installer.

> ⚠️ **Ne pas installer l'application dans OneDrive ou un dossier réseau partagé.**
> La base de données (SQLite) serait corrompue par la synchronisation. Seules les
> **sauvegardes** peuvent être copiées sur un partage / OneDrive.

---

## 1. Prérequis (poste d'hébergement)

- Windows 10/11
- [Python 3.12](https://www.python.org/downloads/windows/) — **cocher « Add python.exe to PATH »** à l'installation
- Le code de l'application (ce dossier), copié dans un emplacement local, par ex. `C:\copro_manager`

## 2. Installation (à faire une seule fois)

Ouvrir une invite de commandes (`cmd`) dans le dossier de l'application :

```bat
cd C:\copro_manager

python -m venv venv
venv\Scripts\pip install -r requirements.txt
copy .env.example .env
```

Éditer ensuite le fichier `.env` : remplacer `change-moi...` par une clé secrète
longue et aléatoire (40+ caractères). Elle ne doit jamais être partagée.

Si une base de données existe déjà (migration depuis un ancien poste), copier
votre fichier `copro_manager.db` dans le sous-dossier `instance\` avant le
premier démarrage.

## 3. Lancement

Double-cliquer sur **`demarrer.bat`**. La console affiche :

```
Copro Manager démarré sur http://0.0.0.0:5000 (CTRL+C pour arrêter)
```

L'application est alors accessible :

- depuis le poste d'hébergement : `http://localhost:5000`
- depuis les autres postes : `http://<adresse-IP-du-poste>:5000`
  (trouver l'IP avec `ipconfig`, ligne « Adresse IPv4 »)

Laisser la console ouverte tant que l'application doit rester accessible.

## 4. Pare-feu Windows (une seule fois)

Pour que les autres postes puissent se connecter, ouvrir le port 5000 en
administrateur (`cmd` en tant qu'administrateur) :

```bat
netsh advfirewall firewall add rule name="Copro Manager" dir=in action=allow protocol=TCP localport=5000
```

## 5. Démarrage automatique (optionnel)

Pour que l'application démarre automatiquement au démarrage du poste, créer un
raccourci vers `demarrer.bat` dans le dossier Démarrage : `Win+R` →
`shell:startup` → coller le raccourci.

## 6. Sauvegardes automatiques (important)

Toutes les données sont dans un seul fichier : `instance\copro_manager.db`.
Planifier une sauvegarde quotidienne :

1. Ouvrir le **Planificateur de tâches** Windows.
2. Créer une tâche → Déclencheur : quotidien (ex. 22h00).
3. Action : démarrer un programme → `C:\copro_manager\sauvegarde.bat`.
4. Le dossier `sauvegardes\` (créé à côté de l'application) conserve les 30
   dernières copies. Il est recommandé d'ajouter ce dossier à OneDrive ou à un
   partage réseau pour une sauvegarde hors du poste.

## 7. Pour les autres utilisateurs

Rien à installer. Ouvrir un navigateur et aller sur :

```
http://<adresse-IP-du-poste-d'hébergement>:5000
```

Ajouter la page aux favoris, ou épingler à la barre de tâches.

## 8. Mise à jour de l'application

Voir **MISE_A_JOUR.md** : procédure détaillée qui ne risque pas les données saisies.

Étapes abrégées :

1. Arrêter la console du serveur (CTRL+C).
2. Récupérer la nouvelle version du code (Git : `git pull`).
3. Relancer `demarrer.bat`. La base de données et les sauvegardes ne sont pas
   touchées.

## 9. Dépannage

| Problème | Solution |
|---|---|
| « venv introuvable » au lancement | Refaire l'étape 2 (création du venv) |
| Les autres postes n'accèdent pas | Vérifier le pare-feu (étape 4) et que l'IP est correcte |
| `python` n'est pas reconnu | Réinstaller Python en cochant « Add to PATH » |
| Base corrompue / données perdues | Restaurer la dernière sauvegarde de `sauvegardes\` : copier le fichier dans `instance\copro_manager.db` (serveur arrêté) |
