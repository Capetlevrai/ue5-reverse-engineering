# Inventorier un jeu Unreal Engine installé

Procédure et outils réutilisables pour identifier les **plugins distribués**, les **dossiers de contenu**, les **archives** et les **métadonnées accessibles** d'un jeu Unreal Engine 4 ou 5, en lecture seule sur son installation.

Un plugin présent dans les archives n'est pas nécessairement chargé pendant une partie. Un dossier nommé comme un pack d'assets n'est pas une preuve de provenance commerciale. Les rapports distinguent les observations, les déclarations et les limites.

## Démarrage rapide — Windows

Prérequis : **Python 3.10+**, **SDK .NET 10**, Git. Le SDK inclut le runtime nécessaire au scanner ; FModel demande le runtime Windows Desktop .NET 10. Aucune bibliothèque Python supplémentaire n'est nécessaire.

```powershell
git clone https://github.com/Capetlevrai/ue5-reverse-engineering.git
cd ue5-reverse-engineering
python scripts/setup_tools.py

python scripts/analyze.py --profile profiles/ff7-rebirth.json --game-dir "D:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH"
```

La commande affiche le chemin de `explorer.html`, un rapport autonome ouvrable directement dans un navigateur. Chaque analyse crée un dossier horodaté sous `runs/`. Les archives du jeu restent à leur emplacement d'origine.

Pour FModel, fermer l'application avant de modifier son profil :

```powershell
python scripts/configure_fmodel.py --profile profiles/ff7-rebirth.json --game-dir "D:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH" --activate
.\Ouvrir-FModel.cmd
```

Les autres profils FModel sont conservés ; une sauvegarde des paramètres est créée sous `.tools/settings-backups/`.

## Procédure détaillée

- [Méthode de bout en bout](docs/procedure.md) : identification des conteneurs, profils moteur, chiffrement, métadonnées, interprétation et vérification.
- [Formats de sortie et limitations](docs/results.md).
- [Ajouter un autre jeu](docs/new-game.md).
- Retours d'expérience : [Bodycam](docs/games/bodycam.md), [FINAL FANTASY VII REBIRTH](docs/games/ff7-rebirth.md), [EMPULSE](docs/games/empulse.md), [Split Fiction](docs/games/split-fiction.md), [ARC Raiders](docs/games/arc-raiders.md).

## Résultats observés le 11 septembre 2026

| Jeu | Stockage | Chemins lisibles | Descripteurs de plugins | État |
|---|---|---:|---:|---|
| Bodycam | 86 PAK | 114 132 | 224 (24 projet / 200 moteur) | Index et registre lisibles ; 106 INI chiffrés |
| FF VII REBIRTH | 50 PAK + 51 paires IoStore | 841 364 | 73 (21 projet / 52 moteur) | Index et 129 métadonnées lisibles ; registre absent des index |
| EMPULSE | 4 PAK + 5 paires IoStore | Indisponible | Indisponible | 8 index chiffrés ; inventaire des fichiers hors archives disponible |

| Split Fiction | 9 PAK + 10 paires IoStore | 282 110 | 102 (4 projet / 98 moteur) | Registre lisible ; 15 812 scripts AngelScript livrés |
| ARC Raiders | 28 PAK + 29 paires IoStore | 187 220, couverture partielle | Indisponible | Index IoStore lisibles indépendamment ; PAK non reconnus et données globales illisibles |

Les `.ucas` sont les données des `.utoc` : les deux fichiers d'une paire ne constituent pas deux index indépendants. `global.utoc` peut ne contenir aucun index de répertoires exploitable.

## Outils employés

| Outil | Rôle |
|---|---|
| [FModel](https://github.com/4sval/FModel) | Explorer graphiquement PAK / IoStore et les assets pris en charge |
| [CUE4Parse](https://github.com/FabianFG/CUE4Parse) | Scanner commun de ce dépôt ; profils spécifiques aux jeux et lecture du registre |
| [repak](https://github.com/trumank/repak) | Vérifier / lister les archives PAK |
| [retoc](https://github.com/trumank/retoc) | Examiner les conteneurs IoStore et leurs chunks |
| [UE Viewer / UModel](https://github.com/gildor2/UEViewer) | Interface « Choose a package to open » ; ancien exécutable, compatibilité UE5 limitée |
| [UAssetGUI / UAssetAPI](https://github.com/atenfyr/UAssetGUI) | Inspecter des assets individuels compatibles, déjà extraits |

Les versions et SHA256 des exécutables sont figés dans `tools.lock.json`. Les paquets .NET sont figés dans `src/UnrealInventory/packages.lock.json`. Le scanner conserve les erreurs au lieu de transformer une lecture impossible en inventaire vide présenté comme complet.

## Contenu du dépôt

Ce dépôt versionne la procédure, les scripts, les profils de compatibilité et des synthèses. Les exécutables téléchargés, clés AES, mappings, configurations locales, fichiers extraits et inventaires détaillés restent dans les dossiers ignorés par Git. Aucun asset original d'un jeu n'est nécessaire pour cloner le dépôt ou lire la documentation.

## Vérifications

```powershell
python -m unittest discover -s tests -v
dotnet build src/UnrealInventory/UnrealInventory.csproj -c Release -p:RestoreLockedMode=true
```

Le scanner compare la taille et la date de modification des fichiers installés avant/après une analyse. Ce contrôle n'est pas un calcul d'empreinte intégrale des archives. Les métadonnées extraites disposent, elles, d'un SHA256 individuel.
