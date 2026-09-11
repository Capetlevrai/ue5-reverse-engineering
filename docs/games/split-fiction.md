# Split Fiction

Observation locale du 11 septembre 2026. Projet interne : `Split`.

```powershell
python scripts/analyze.py --profile profiles/split-fiction.json --game-dir "D:\SteamLibrary\steamapps\common\Split Fiction"
python scripts/configure_fmodel.py --profile profiles/split-fiction.json --game-dir "D:\SteamLibrary\steamapps\common\Split Fiction" --activate
```

Le profil dédié `GAME_SplitFiction` de [CUE4Parse](https://github.com/FabianFG/CUE4Parse/blob/master/CUE4Parse/UE4/Versions/EGame.cs) utilise une base de compatibilité UE5.4. Le `.uproject` livré ne renseigne pas `EngineAssociation` : la version exacte du build moteur n'est pas établie indépendamment.

## Résultats

| Mesure | Observation |
|---|---:|
| Conteneurs du jeu | 9 PAK, 10 UTOC, 10 UCAS |
| Lecteurs montés | 18 sur 19 ; global sans index de répertoires |
| Chemins effectifs | 282 110 |
| Descripteurs / entrées de manifeste | 102 / 102 |
| Plugins projet / moteur | 4 / 98 |
| Déclarations explicites activées / désactivées | 29 / 88 |
| Dossiers racines de contenu | 21 |
| Chemins `.umap` | 1 173 |
| Métadonnées extraites / indisponibles | 163 / 0 |
| Entrées du registre / packages distincts | 97 698 / 89 835 |
| Scripts `.as` hors archives | 15 812 |

Les quatre plugins du projet sont **FSR3** (3.1.0), **HazelightToolkit** (1.0), **UtgStatRes** (1.0) et **Wwise** (2022.1.4.8200.2650). Les descripteurs moteur comprennent notamment **Angelscript** et **HazeWindowsGamingInput**. Les modules déclarés du projet sont `Split`, `SplitEditor`, `EAOnline` et `SteamAPI`. Ces déclarations ne mesurent pas l'activation pendant une partie.

Le registre donne notamment 13 640 `AnimSequence`, 11 299 `MaterialInstanceConstant`, 9 963 `Texture2D`, 8 975 `HazeAudioEvent`, 7 505 `StaticMesh`, 4 683 `BlueprintGeneratedClass` et 3 928 `Blueprint`. Les catégories Blueprint et classe générée sont des entrées distinctes, pas un total de Blueprints uniques.

## Scripts livrés

`Split/Script` contient des sources AngelScript lisibles. Le catalogue conserve leurs chemins et tailles, sans copier le code source. L'onglet **Scripts .as** permet de rechercher les noms ; ouvrir ensuite le fichier correspondant dans l'installation avec un éditeur de texte. La [documentation officielle Hazelight](https://angelscript.hazelight.se/) décrit cette intégration d'AngelScript dans Unreal Engine.

| Sous-dossier | Fichiers `.as` |
|---|---:|
| LevelSpecific | 11 992 |
| Audio | 1 191 |
| Animation | 919 |
| Gameplay | 831 |
| Core | 513 |
| GUI | 123 |
| Editor | 88 |
| Examples | 69 |
| Effects | 58 |
| Environment | 28 |

Les sources, assets et inventaires détaillés restent locaux sous l'installation ou `runs/`. Le scan complet vérifié n'a changé ni les tailles ni les dates de modification des fichiers installés. L'état `indexed` concerne les index et métadonnées ciblées ; tous les assets n'ont pas été décodés individuellement.

FModel a également été lancé avec `GAME_SplitFiction` : son journal confirme 18/19 lecteurs montés et 282 110 fichiers, en accord avec le scanner. Les onglets du rapport et la recherche des scripts ont été vérifiés dans un navigateur.
