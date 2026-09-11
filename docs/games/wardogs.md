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
