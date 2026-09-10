# Ashenveil — Le Sanctuaire Fendu

**Ashenveil** est un RPG tactique en 2D, jouable localement en coopération de 2 à 4 joueurs. Il reprend une ambiance de cavernes, de silhouettes insectoïdes et de ruines mélancoliques, tout en utilisant un univers et des personnages originaux. La scène utilise maintenant un décor illustré, cinq sprites manga originaux, des halos, impacts, particules et textes de dégâts animés.

## Lancer le jeu

Le jeu fonctionne avec Python 3 et Pygame lorsqu’il est lancé depuis les sources.

```bash
python3 -m pip install --user pygame
python3 ashenveil.py
```

Sous Linux, le lanceur peut également être utilisé :

```bash
chmod +x lancer.sh
./lancer.sh
```

## Version Windows `.exe`

Le projet contient le script `construire_exe_windows.bat`. Sur Windows, installe d’abord **Python 3.11 ou une version plus récente** depuis [python.org](https://www.python.org/downloads/windows/) et coche l’option **Add Python to PATH** pendant l’installation.

Ensuite, décompresse l’archive, ouvre le dossier `ashenveil_rpg`, puis double-clique sur `construire_exe_windows.bat`. Le script installe automatiquement Pygame et PyInstaller, puis crée l’exécutable autonome dans `dist\\Ashenveil.exe`.

Tu peux ensuite copier uniquement `dist\\Ashenveil.exe` sur une autre machine Windows. Windows Defender peut afficher un avertissement parce que l’exécutable est généré localement et n’est pas signé numériquement ; c’est attendu pour un build personnel.

## Contrôles

| Moment | Commande |
|---|---|
| Menu | `←` / `→` : choisir 2 à 4 joueurs ; `Entrée` : commencer |
| Combat | `A` : attaque ; `S` : sort ; `G` : garde ; `P` : potion |
| Combat | `Tab` ou `←` / `→` : changer de cible |
| Fin de partie | `R` : recommencer ; `Échap` : revenir au menu |

La coopération est en **pass-and-play** : chaque joueur contrôle un héros quand son tour arrive, avec un clavier partagé.

## Manette

Le jeu détecte automatiquement les manettes compatibles avec Pygame, notamment les contrôleurs Xbox et PlayStation vus comme des périphériques XInput/SDL. Une ou plusieurs manettes peuvent être branchées ; les commandes s’appliquent au héros dont c’est le tour.

| Manette | Fonction |
|---|---|
| Stick gauche horizontal ou croix directionnelle | Choisir le nombre de joueurs dans le menu ; changer de cible en combat |
| A / Croix | Commencer ; attaque |
| X / Carré | Sort |
| B / Rond | Garde |
| Y / Triangle | Potion |
| LB / L1 | Joueur précédent dans le menu ; cible précédente en combat |
| RB / R1 | Joueur suivant dans le menu ; cible suivante en combat |

Les boutons de la manette et le clavier peuvent être utilisés simultanément.

## Héros

| Héros | Rôle | Particularité |
|---|---|---|
| Vesper | Lame-ombre | Attaques puissantes et coups critiques |
| Myr | Tisseuse | Soin de groupe |
| Orun | Gardien | Réduction des dégâts pour toute l’équipe |
| Nox | Chante-sort | Sort de zone touchant tous les ennemis |

Chaque personnage dispose de points de vie, de mana, de puissance, d’armure et de deux potions. Le combat alterne entre les tours des héros et ceux des ennemis.

## État du prototype

Cette version est une base jouable et locale, centrée sur la boucle de combat. Elle est prête à être étendue avec une carte d’exploration, des salles générées, davantage d’ennemis, de l’équipement, des sauvegardes et un mode réseau.

## Licence

Prototype fourni pour usage personnel et expérimentation.
