# ARC Raiders

Observation locale du 11 septembre 2026. Projet interne : `PioneerGame`. Résultat **partiel**, exploitable pour explorer des chemins et indices de composants.

```powershell
python scripts/analyze.py --profile profiles/arc-raiders.json --game-dir "D:\SteamLibrary\steamapps\common\Arc Raiders"
python scripts/configure_fmodel.py --profile profiles/arc-raiders.json --game-dir "D:\SteamLibrary\steamapps\common\Arc Raiders"
```

Le profil dédié `GAME_ArcRaiders` de [CUE4Parse](https://github.com/FabianFG/CUE4Parse/blob/master/CUE4Parse/UE4/Versions/EGame.cs) utilise une base de compatibilité UE5.7. Aucune métadonnée moteur exploitable ne permet ici de confirmer la version exacte du build installé.

## Résultats accessibles

| Mesure | Observation |
|---|---:|
| Conteneurs dans `PioneerGame/Content/Paks` | 28 PAK, 29 UTOC, 29 UCAS |
| Lecteurs enregistrés | 29 UTOC ; les 28 PAK sont rejetés |
| Index IoStore montés indépendamment | 28 |
| Chemins effectifs / entrées cumulées | 187 220 / 187 220 |
| Chemins `.uasset` | 125 290 |
| Chemins `.ubulk` | 60 371 |
| Chemins `.umap` | 1 545 |
| Chemins `.ushaderbytecode` | 14 |
| Dossiers racines de contenu du projet | 8 |
| Racines de contenu de plugins visibles | 17 |
| Binaires hors archives | 50 : 42 DLL et 8 EXE |
| Descripteurs, manifeste, registre | Indisponibles dans les index accessibles |

Une autre archive PAK appartient au CrashReportClient ; elle n'est pas comptée comme archive du jeu ciblé. L'installation comprend également 57 fichiers `.meta` associés aux conteneurs. Leur présence ne prouve pas à elle seule un mécanisme de protection précis.

Le contenu principal est `PioneerGame/Content/Pioneer` : 183 127 chemins, dont 122 901 packages `.uasset/.umap`. Les autres racines sont CustomDepthStencils, DebugInterface, DemoRoom, Developers, Meshes, ThirdPerson et Tools. Un chemin de carte ne prouve pas qu'une zone est accessible dans le jeu commercial.

Les index exposent des racines de contenu **Niagara**, **ControlRig**, **Interchange/Runtime**, **Embark**, **SpeedTreeImporter**, **KantanCharts**, **AudioModulation**, **HDRIBackdrop**, **HoudiniEngine**, **MovieRenderPipeline**, **MeshModelingToolsetExp**, **CommonUI**, **WebBrowserWidget**, **MediaPlate**, **ACLPlugin**, **AnimationSharing** et **MeshModelingToolset**. Il s'agit de chemins de contenu, sans descripteur validé ni preuve d'activation des modules. L'onglet **Contenu de plugins** conserve cette distinction.

Les chemins de binaires livrés identifient cinq groupes supplémentaires : **EmbarkCrashReporting**, **AMD FSR**, **Intel XeSS**, **Nvidia DLSS** et **StreamlineCore**. Le rapport conserve les fichiers justificatifs.

## Erreurs et repli

1. CUE4Parse rejette les 28 PAK avec `unknown format`. `repak 0.2.3 info/list` échoue aussi sur le premier PAK.
2. Le montage global échoue dans `IoGlobalData`, lecture `ScriptObjects`, avec `Read size is smaller than zero`.
3. `retoc 0.1.5 info` échoue sur le premier UTOC avec `invalid chunk type for version >= UE5: 143`.
4. Le scanner tente alors les index de répertoires IoStore indépendamment. Les 28 index sont montés et donnent les chemins ci-dessus. Les erreurs de PAK et de montage global restent dans `raw/scan-diagnostics.json` et `raw/parser.log`.

Ce repli ne répare pas les données globales et ne démontre pas la lisibilité des données des assets. Les indicateurs de chiffrement des lecteurs UTOC enregistrés sont faux ; cela n'exclut pas une protection ou transformation hors de ces indicateurs. Fournir simplement une clé AES n'est donc pas une résolution établie de ce cas.

Le profil FModel est enregistré, mais le succès du scanner avec son repli personnalisé ne signifie pas que FModel peut ouvrir l'installation intégralement. Utiliser le rapport HTML pour les résultats vérifiés. La poursuite demanderait un lecteur compatible avec les PAK/données globales de cette installation. Aucun asset ni code du jeu n'est publié dans le dépôt ; tailles et dates de modification sont inchangées après le scan.
