# FINAL FANTASY VII REBIRTH — retour d'expérience

Observation locale du 11 septembre 2026. Projet interne : `End`.

## Profil et stockage

- Profil : **`GAME_FinalFantasy7Rebirth`**, profil dédié de CUE4Parse.
- Le `.uproject` livré a une association moteur vide. Le profil est rattaché à une base de compatibilité UE4.26 dans CUE4Parse ; ne pas en déduire une version exacte du moteur personnalisé.
- 50 PAK, 51 UTOC et 51 UCAS, dont `global.*` et des conteneurs `optional`.
- 101 lecteurs enregistrés, 100 montés ; le lecteur global n'a pas d'index de répertoires. Ce cas n'est pas un échec de déchiffrement.
- Aucun index ou fichier indexé n'est signalé chiffré dans cette passe.

## Résultats

- **841 364 chemins effectifs**, autant que dans la somme des index individuels de cet instantané.
- 717 440 chemins `.uasset`, 112 285 `.ubulk`, 14 `.uptnl` et **10 509 `.umap`**. Ces niveaux incluent potentiellement des sous-niveaux et découpages de monde, pas 10 509 cartes jouables.
- **73 descripteurs de plugins**, dont **21 projet** et **52 moteur**.
- 73 entrées dans le manifeste.
- 22 déclarations de plugins activées et 84 désactivées dans le projet. Cela n'est pas le nombre de plugins réellement chargés.
- **31 dossiers racines de contenu**.
- **129 métadonnées extraites**, comprenant 73 descripteurs, 54 INI, le `.uproject` et le manifeste.
- Aucun `AssetRegistry.bin` ou `DevelopmentAssetRegistry.bin` visible dans les index lus. Les classes et parents de Blueprints ne sont pas inventoriés à partir d'un registre.

## Plugins du projet identifiés

`ACLPlugin`, `AcrePreBuild`, `AssetBuilderTools`, `BodyDriverPlugin`, `BonamikPlugin`, `Commandlet`, `EndCascade`, `EndInjectCommand`, `EndSpriteSheet`, `EndTextResourceEditor`, `EndNaviMapEd`, `EndResavePackages`, `EndMenuCore`, `EndTextResource`, `HappySadFaceLipSync`, `ImGui`, `KBDPlugins`, `KineDriverPlugin`, `SQEXSEAD`, `VFXNiagara`, `VisualStudioTools`.

Le projet déclare les modules `EndCore`, `EndDataObject`, `EndDataBase`, `EndGame`, `EndDebug` et `EndEditor`. Le dernier est de type Editor. La distribution contient également des descripteurs tels que `DLSSSubset`, `FSRSubset`, `StreamlineSubset`, `OodleData` et `BinkMedia` côté moteur.

## Particularité retoc

retoc 0.1.5 peut lire l'index de répertoires, mais signale `Failed to parse ContainerHeader` sur un conteneur testé. Le profil spécifique de CUE4Parse permet de produire l'inventaire consolidé. Une lecture des noms ne valide pas la conversion des assets avec un profil générique.

## Reproduire

```powershell
python scripts/analyze.py --profile profiles/ff7-rebirth.json --game-dir "D:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH"
python scripts/configure_fmodel.py --profile profiles/ff7-rebirth.json --game-dir "D:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH" --activate
```

Les métadonnées originales et paramètres INI restent dans les sorties locales ignorées par Git. L'exploration exhaustive des objets et les prévisualisations constituent une étape distincte de cet inventaire.

FModel aug-2026 a également été lancé avec ce profil : titre `FF7R2 (GAME_FinalFantasy7Rebirth)`, journal `Project: End | Mounted: 100/101 | Files: x841364`. Des PAK vides ont un point de montage `/` que le parseur normalise ; ces avertissements n'ont pas empêché l'indexation.
