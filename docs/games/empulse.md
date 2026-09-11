# EMPULSE — retour d'expérience

Observation locale du 11 septembre 2026. Projet interne : `Orion`.

## Stockage et limite constatée

- 4 PAK, 5 UTOC et 5 UCAS sous `Orion/Content/Paks`.
- 9 lecteurs enregistrés : **8 index chiffrés**, plus un lecteur global sans index de répertoires.
- repak ne peut pas lister le PAK principal sans clé ; retoc signale une clé manquante sur le conteneur principal.
- Le GUID de chiffrement demandé est nul (`00000000000000000000000000000000`). Ce GUID identifie un emplacement de clé ; **ce n'est pas une clé constituée de zéros**.
- Aucun chemin interne, descripteur ou registre n'a été récupéré. Il est donc impossible d'en donner un décompte exhaustif à ce stade.

La version exacte du moteur n'est pas confirmée. `GAME_UE5_LATEST` est un profil provisoire utilisé uniquement pour observer les en-têtes de conteneurs, pas une attribution de version. Le binaire expose `Orion-CL-643073`, qui ne suffit pas à établir une version mineure Unreal.

## Informations accessibles hors archives

66 binaires sont livrés directement sur disque : 61 DLL et 5 exécutables. Les chemins fournissent des indices de distribution pour :

- **WwiseSoundEngine** : moteur audio et bibliothèques d'effets sous `Engine/Plugins/Audio`.
- **Sentry** : composants de rapport de crash.
- **DiscordPartnerSDK**.
- **AMD FSR**.
- **NVIDIA DLSS**.
- **NVIDIA StreamlineCore**.
- **MerlinAntiCheat / equ8_client**, dans un chemin `RemappedPlugins`.

Des DLL EOS SDK, Steamworks, Opus et d'autres bibliothèques sont également visibles. Un ensemble de DLL n'est pas autant de plugins Unreal distincts. Ces observations confirment des fichiers livrés, pas l'exécution de chaque composant.

## Reproduire et reprendre

```powershell
python scripts/analyze.py --profile profiles/empulse.json --game-dir "D:\SteamLibrary\steamapps\common\EMPULSE"
```

Le résultat attendu sans clé est `blocked-encrypted-indexes`, accompagné de l'inventaire hors archives. Une clé AES adaptée est nécessaire pour poursuivre l'arborescence, les plugins et les métadonnées internes. La procédure pour fournir localement une clé au scanner figure dans [la méthode générale](../procedure.md#4-distinguer-les-deux-cas-de-chiffrement).

Après ouverture des index, confirmer la version/profil moteur à partir des données accessibles puis relancer dans un **nouveau dossier de résultats**. Ne pas réutiliser un rapport vide comme preuve d'absence d'assets.
