# Bodycam — retour d'expérience

Observation locale du 11 septembre 2026. Projet interne : `Bodycam`.

## Profil et stockage

- Profil : `GAME_UE5_5`.
- Preuve : `EngineAssociation: 5.5` dans le `.uproject` livré.
- 86 PAK, sans IoStore dans le dossier de contenu observé.
- Index non chiffrés ; compression Oodle.

## Résultats

- 114 132 chemins uniques dans les index.
- 224 descripteurs de plugins : 24 projet, 200 moteur.
- Manifeste contenant 224 entrées ; différences de champs/defaults possibles avec les descripteurs originaux.
- 48 plugins explicitement activés et 5 désactivés dans les déclarations du projet. Les restrictions de modules et plateformes s'appliquent.
- 147 dossiers racines de contenu.
- 44 459 entrées du registre, correspondant à 42 569 packages distincts.
- 164 chemins `.umap`.
- 227 métadonnées extraites ; 106 fichiers INI chiffrés.

Quelques descripteurs du projet : `BodycamAnimationFramework` (2025.1.0), `BodycamPostProcessFramework` (1.0), `Imperfecter` (1.5.1), `CrazyIvy` (1.0), `HostMigrationSystemV2` (1.0), `SteamCorePro` (1.0.5.6), `GameAnalytics` (6.1.2), `LootLockerSDK` (6.0.0), `VTSCommonUIExtension` (0.7).

Les versions sont celles de `VersionName`. Exemple de différence : le dossier `DLSS v8.8.0` contient un descripteur annonçant `8.7.2-NGX310.6.0`.

Le registre donne notamment 15 468 `Texture2D`, 5 580 `StaticMesh`, 6 070 `SoundWave` et 1 535 `BlueprintGeneratedClass`. Ce sont des classes du registre, pas une déduction à partir des noms de fichiers.

## FModel et limites

FModel peut afficher `Unknown (GAME_UE5_5)` parce que `DefaultGame.ini` est chiffré. Son journal indique 114 132 fichiers et `Mounted: 84/86` après reclassement des deux archives contenant des fichiers chiffrés. Les index de ces archives restent lisibles. Le scanner commun conserve ces lecteurs indexés et distingue `encryptedIndexedFiles` du chiffrement de l'index.

Le registre livré ne contient pas de table de dépendances exploitable dans cette passe. Les références de modules sont tirées des tags `/Script/...` ; elles ne prouvent pas leur chargement en jeu.

## Reproduire

```powershell
python scripts/analyze.py --profile profiles/bodycam.json --game-dir "D:\SteamLibrary\steamapps\common\Bodycam"
```

Le scanner commun reproduit les mêmes compteurs que l'inventaire initial réalisé avec repak et un lecteur de registre séparé.
