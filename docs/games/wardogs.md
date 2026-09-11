# Wardogs — plugins identifiables

Observation locale du 11 septembre 2026. Installation : `D:\SteamLibrary\steamapps\common\Wardogs`, projet interne `Wardogs`.

**Six familles de plugins identifiées par leurs chemins et binaires livrés. La liste complète reste indisponible : 31 index sont chiffrés et aucun descripteur `.uplugin` n'a été lu.** La présence d'un binaire ne démontre pas son chargement pendant une partie.

| Composant / dossier du plugin | Binaires justificatifs | Versions de fichiers PE observées |
|---|---|---|
| AMD FSR — `External/FSR` | `amd_fidelityfx_framegeneration_dx12.dll`, `amd_fidelityfx_upscaler_dx12.dll` | 4.0.0.604 / 4.0.3.604 |
| NVIDIA DLSS — `External/Nvidia/DLSS` | `nvngx_dlss.dll`, `nvngx_dlssd.dll` | 310,6,0,0 |
| NVIDIA StreamlineCore — `External/Nvidia/StreamlineCore` | `sl.common.dll`, `sl.reflex.dll`, `sl.dlss_g.dll`, `nvngx_dlssg.dll`, notamment | 2,11,1,0 pour les `sl.*` ; 310,6,0,0 pour les `nvngx_*` |
| Intel XeSS — `External/XeSS` | `libxess.dll`, `libxess_dx11.dll` | 2.0.1.41 |
| Sentry — `External/Sentry` | `crashpad_handler.exe`, `crashpad_wer.dll` | 0.12.8 |
| VivoxCore — `Online/VivoxCore` | `vivoxsdk.dll` | 5.27.1.33971 |

Les dossiers ci-dessus sont relatifs à `Wardogs/Plugins/`. Les numéros viennent des ressources Windows `FileVersion` des binaires : ce ne sont pas des versions de descripteurs Unreal, ni une identification automatique des générations commerciales des technologies. Plusieurs bibliothèques appartiennent au même groupe de plugin.

## Couverture des archives

- 16 PAK, 17 UTOC et 17 UCAS dans `Wardogs/Content/Paks`.
- 33 lecteurs enregistrés, dont **31 index chiffrés** : les 16 PAK et 15 UTOC.
- `global.utoc` n'a pas d'index de répertoires.
- Le seul index monté, `pakchunk10optional-WindowsClient.utoc`, contient deux chemins `.uptnl` de textures. Ces données optionnelles ne permettent pas d'identifier d'autres plugins.
- Aucun descripteur, manifeste ou registre accessible. État du rapport : `partial`, avec seulement 2 chemins lisibles.
- 49 binaires hors archives : 43 DLL et 6 EXE ; 17 de ces fichiers appartiennent aux six dossiers de plugins ci-dessus.

L'installation contient aussi des fichiers `.pak` Chromium/CEF hors du dossier de conteneurs Unreal ; ils ne sont pas comptés comme archives de contenu du jeu. Ne pas confondre le nombre global de fichiers portant cette extension avec le nombre de PAK Unreal.

## Profil moteur et preuves

Les huit `.uasset` livrés directement sous `Wardogs/Content/Binks` contiennent chacun deux structures compatibles avec `FEngineVersion` : **5.7.4**, branche `++Wardogs+EarlyAccess-0.1`. Observation obtenue en décodant les champs `uint16 Major/Minor/Patch`, `uint32 Changelist`, puis le `FString` de branche et sa longueur. Cela décrit la version sérialisée dans ces assets ; le build exécutable courant n'est pas nécessairement identique.

La ressource de version de `WardogsClient-Win64-Shipping.exe` indique `++Wardogs+Live-CL-499738`. Le profil choisi est `GAME_UE5_7`. Les observations avec chemins et offsets sont conservées localement dans `version-evidence.json` ; les versions PE détaillées sont dans `loose-plugin-binary-versions.json`.

## Reproduire et compléter

```powershell
python scripts/analyze.py --profile profiles/wardogs.json --game-dir "D:\SteamLibrary\steamapps\common\Wardogs"
python scripts/configure_fmodel.py --profile profiles/wardogs.json --game-dir "D:\SteamLibrary\steamapps\common\Wardogs"
```

Sans clé adaptée, le résultat attendu reste partiel. Le GUID demandé est `00000000000000000000000000000000` : il identifie un emplacement de clé, ce n'est pas une clé AES nulle. La [procédure générale](../procedure.md#4-distinguer-les-deux-cas-de-chiffrement) explique le fichier local `UE_INVENTORY_AES_FILE`. Après fourniture d'une clé valide, refaire une analyse dans un nouveau dossier afin d'obtenir les descripteurs et déclarations internes.

Pour reproduire la lecture des versions de binaires dans PowerShell :

```powershell
Get-ChildItem 'D:\SteamLibrary\steamapps\common\Wardogs\Wardogs\Plugins' -Recurse -File |
    Where-Object { $_.Extension -in '.dll', '.exe' } |
    ForEach-Object { $_.VersionInfo | Select-Object FileName, FileVersion, ProductVersion }
```

Les tailles et dates de modification de l'installation sont inchangées avant/après le scan. Les fichiers bruts et données extraites restent locaux et ignorés par Git.

## Tentative de récupération de clé sur disque

Une passe supplémentaire a examiné l'exécutable du client, le lanceur, `coreinit.dll` et `runtime.dll`. Quatre signatures d'initialisation de constantes, documentées dans le [code d'aesdumpster-rs](https://github.com/yuhkix/aesdumpster-rs/blob/main/src/key_dumpster.rs), ont été recherchées avec un script local, ainsi que les chaînes ASCII hexadécimales de 64 caractères. Le code d'[UEAESKeyFinder](https://github.com/EZFNDEV/UEAESKeyFinder) a été examiné ; son programme n'a pas été lancé.

Résultat : **7 candidates brutes**, soit 26 valeurs distinctes en tenant compte des variantes d'ordre des octets/mots. Elles ont été testées en AES-ECB sur le début des **16 index PAK chiffrés** : aucune ne produit un point de montage Unreal plausible. Aucune clé n'est validée, et les archives ne sont pas débloquées.

L'exécutable principal possède des sections `.text`, `.data` et `.pdata` d'entropie voisine de 8 bits/octet et n'importe que `coreinit.dll`. `runtime.dll` comporte des sections nommées `packer0`, `packer1`, etc. Ces observations suggèrent un emballage ou une protection du code ; elles ne déterminent pas à elles seules l'algorithme ou la façon dont la clé d'archives est fournie. L'entropie d'une candidate n'est jamais considérée comme une validation cryptographique.

Les diagnostics et candidates restent dans `.tools/research/wardogs/`, ignoré par Git. Une clé valide, une version du client dont le code est directement analysable ou des données de diagnostic adaptées restent nécessaires pour poursuivre. Le résultat de cette tentative est négatif, pas une preuve que la clé ne peut jamais être récupérée.

## Multijoueur et réplication : ce qui est établi

- La [politique officielle de Wardogs](https://www.wardogs.com/enforcement) décrit un navigateur de serveurs, des serveurs officiels et des serveurs communautaires loués à des hébergeurs.
- Les fichiers du client livrent `VivoxCore/vivoxsdk.dll`, indice de l'intégration du SDK de communication Vivox ; ce n'est pas une preuve du système qui réplique les acteurs de gameplay.
- Les configurations locales lisibles ne donnent aucun résultat pour `Iris`, `ReplicationGraph`, `ReplicationDriver`, `NetDriver`, `OnlineSubsystem` ou `SteamSockets`. Aucun journal de jeu `.log` exploitable n'a été trouvé dans le dossier local `Wardogs` lors de cette passe.
- **Le système de réplication sous-jacent, le NetDriver, le tickrate serveur et les détails de prédiction/compensation de latence ne sont pas établis.** Une architecture de prédiction côté client est néanmoins confirmée par le témoignage technique ci-dessous. La version de sauvegarde UE5.7.4 ne prouve pas l'utilisation d'Iris.

[La documentation Epic](https://dev.epicgames.com/documentation/unreal-engine/introduction-to-iris-in-unreal-engine) précise qu'Iris est un choix explicite. [Iris et Replication Graph sont deux systèmes distincts](https://dev.epicgames.com/documentation/unreal-engine/migrate-to-iris-in-unreal-engine) ; on ne peut pas attribuer l'un ou l'autre au jeu sans configuration, symboles ou traces probantes.

### Source directe : Salty Panda Studios

La [fiche Wardogs publiée par Salty Panda Studios](https://saltypandastudios.com/wardogs-bulkhead/), consultée le 11 septembre 2026, contient un témoignage attribué à **Chris Eaves, Technical Director chez BULKHEAD**. Il explique avoir confié au partenaire des problèmes difficiles de réplication et confirme la livraison d'une architecture unifiée de prédiction côté client, accompagnée d'outils de gestion. Le témoignage souligne également leur travail d'optimisation bas niveau et leur connaissance du réseau de gameplay Unreal.

Extrait : « unified client side prediction architecture ».

Cette source permet d'identifier un prestataire et une contribution technique concrète au netcode de Wardogs. Elle ne nomme ni Iris, ni Replication Graph, ni le plugin Epic Network Prediction ; elle ne décrit pas non plus l'implémentation complète du build installé. Une architecture de prédiction peut s'appuyer sur un système de réplication existant : ce témoignage n'établit pas le remplacement de toute la couche réseau Unreal.

### Cadre général : War Dynamics Framework

Le communiqué BULKHEAD/Team17 du 5 février 2026, [reproduit intégralement par Saving Content](https://www.savingcontent.com/2026/02/05/wardogs-announced-by-bulkhead-and-team17-this-new-tactical-fps-is-enters-early-access-this-year/), présente le **War Dynamics Framework** comme un framework propriétaire construit sur Unreal Engine pour soutenir le jeu à grande échelle, les véhicules, les armes et les systèmes persistants. Ce nom décrit un ensemble technologique plus large ; il ne suffit pas à identifier l'algorithme de réplication ou à rattacher précisément la contribution de Salty Panda à un module particulier.
