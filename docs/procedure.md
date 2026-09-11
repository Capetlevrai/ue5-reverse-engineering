# Procédure réutilisable

## 1. Inventorier les fichiers livrés

Repérer le vrai répertoire du projet, qui peut différer du nom commercial : `Bodycam`, `End` pour REBIRTH, `Orion` pour EMPULSE.

Chercher son dossier `Content/Paks` et les extensions :

- `.pak` : archive PAK.
- `.utoc` + `.ucas` : index et données IoStore ; conserver toutes les partitions, archives optionnelles et `global.*` à leur place.
- `.uplugin` : descripteur de plugin.
- `.uproject` : modules et déclarations explicites de plugins du projet.
- `.upluginmanifest` : descripteurs présents dans la distribution.
- `AssetRegistry.bin` : registre d'assets, lorsqu'il est livré.
- `.dll` et chemins `Plugins`, `RemappedPlugins` : indices supplémentaires hors archives.

Un dossier de DLL incomplet n'est pas un inventaire exhaustif : des plugins peuvent être compilés dans l'exécutable ou n'avoir que du contenu dans les archives.

## 2. Choisir le profil de lecture

Utiliser un profil propre au jeu s'il existe dans [CUE4Parse/EGame.cs](https://github.com/FabianFG/CUE4Parse/blob/master/CUE4Parse/UE4/Versions/EGame.cs). Pour REBIRTH : `GAME_FinalFantasy7Rebirth`.

À défaut, choisir une version UE étayée par le fichier projet, les informations de build, les logs ou des assets lisibles. Noter la source de cette conclusion dans `version_evidence`. Une association de projet vide, une chaîne `UE5-CL-0` ou une valeur de profil choisie par défaut ne confirme pas une version mineure.

Le profil de REBIRTH est rattaché à une base de compatibilité UE4.26 dans CUE4Parse. Cela ne décrit pas toutes les modifications du moteur Square Enix. Ne pas sélectionner arbitrairement UE5 parce que ce dépôt porte ce nom.

## 3. Tester les index avant toute extraction volumineuse

Exemples, depuis la racine du dépôt :

```powershell
.\.tools\repak\repak.exe info "D:\Games\Example\Project\Content\Paks\pakchunk0-Windows.pak"
.\.tools\repak\repak.exe list "D:\Games\Example\Project\Content\Paks\pakchunk0-Windows.pak"
.\.tools\retoc\retoc.exe info "D:\Games\Example\Project\Content\Paks\pakchunk0-Windows.utoc"
.\.tools\retoc\retoc.exe list "D:\Games\Example\Project\Content\Paks\pakchunk0-Windows.utoc" --path
```

`retoc list --path` affiche des chunks et des colonnes, pas simplement une liste de noms. Conserver stdout **et stderr**. Une erreur de lecture du ContainerHeader peut coexister avec des chemins lisibles ; elle ne valide pas le décodage des packages.

Pour REBIRTH, retoc 0.1.5 affiche `Failed to parse ContainerHeader` mais peut lire les chemins. Le scanner CUE4Parse avec le profil spécifique est utilisé pour l'inventaire consolidé.

## 4. Distinguer les deux cas de chiffrement

**Index clair, certains fichiers chiffrés** : on peut connaître les noms sans pouvoir lire les contenus. Bodycam en est un exemple : les 106 INI sont chiffrés, les descripteurs et le registre sont accessibles.

**Index chiffré** : l'outil ne peut même pas produire l'arborescence sans la clé adaptée. EMPULSE en est un exemple dans l'installation observée.

La clé n'est ni devinée ni publiée par les scripts. Si l'on possède une clé adaptée, préparer un fichier **local ignoré par Git**, par exemple `keys.local.json`, dont les clés JSON sont les GUID de chiffrement et les valeurs sont les clés AES hexadécimales. Utiliser les GUID signalés dans `raw/scan-summary.json` ; le GUID nul n'est pas une clé AES.

```powershell
$env:UE_INVENTORY_AES_FILE = (Resolve-Path .\keys.local.json).Path
python scripts/analyze.py --profile profiles/empulse.json --game-dir "D:\SteamLibrary\steamapps\common\EMPULSE"
Remove-Item Env:UE_INVENTORY_AES_FILE
```

Ne jamais ajouter les clés, les profils locaux contenant des clés ou les journaux de déchiffrement à Git. FModel utilise ses propres paramètres AES ; fournir une clé au scanner ne configure pas automatiquement FModel.

## 5. Lancer le scanner commun

```powershell
python scripts/analyze.py --profile profiles/bodycam.json --game-dir "D:\SteamLibrary\steamapps\common\Bodycam"
```

Le scanner :

1. Inventorie les fichiers présents sur disque.
2. Ouvre les lecteurs PAK / IoStore avec le profil choisi.
3. Écrit un index par archive et l'index effectif consolidé.
4. Extrait uniquement les descripteurs, manifests, INI et registres ciblés.
5. Parse les registres lisibles et conserve les tags, classes et noms de packages.
6. Produit les rapports JSON, Markdown et HTML.
7. Compare tailles et dates de modification des fichiers installés avant/après.

Chaque lancement utilise un dossier neuf. Cela évite de mélanger des métadonnées anciennes avec une nouvelle version du jeu. `--reuse-raw` est réservé à la régénération d'un rapport à partir d'un scan existant ; dans ce mode la comparaison avant/après ne couvre que la régénération, pas le scan historique.

L'extraction est binaire via l'API, sans redirection PowerShell susceptible de réencoder les données. Les chemins de sortie sont vérifiés pour rester sous le dossier des métadonnées. La limite d'un fichier de métadonnées est de 512 Mio.

## 6. Interpréter les plugins

Les descripteurs Unreal sont documentés par [Epic](https://dev.epicgames.com/documentation/unreal-engine/plugins-in-unreal-engine). Conserver séparément :

- **Descripteur présent** : fichier réellement observé dans la distribution.
- **Manifeste présent** : entrée de distribution ; peut omettre des valeurs par défaut du descripteur original.
- **Enabled=true / false** : choix explicite dans le projet.
- **EnabledByDefault** : comportement déclaré par défaut, sans observation d'exécution.
- **Modules et cibles** : Runtime, Editor, UncookedOnly, ClientOnly, restrictions de plateformes, etc.
- **Contenu / références dans le registre** : indices statiques complémentaires.

Un module `Editor` ne doit pas être présenté comme un module runtime. Un plugin absent des déclarations explicites peut être activé par défaut ou par dépendance. Un plugin explicitement activé pour une autre plateforme ne prouve pas son utilisation sous Windows.

Les versions viennent de `VersionName`, avec leur source. Un dossier nommé `DLSS v8.8.0` peut contenir un descripteur annonçant `8.7.2-NGX310.6.0` : ne pas fusionner ces deux observations.

## 7. Interpréter le contenu et le registre

Un dossier peut correspondre à du contenu interne, un ancien système, une démonstration ou un pack tiers renommé. Éviter de transformer un nom de dossier en attribution commerciale certaine.

Les fichiers `.uasset`, `.uexp`, `.ubulk` et `.uptnl` ne doivent pas être comptés comme autant d'assets indépendants. Le registre peut contenir le Blueprint et sa classe générée, donc plus d'entrées que de packages uniques.

Les `.umap` peuvent être des sous-niveaux, cellules ou niveaux de test, pas seulement des cartes jouables. Sans registre, les scripts n'inventent pas les classes et parents de Blueprints à partir des noms.

## 8. Utiliser FModel et les autres inspecteurs

[FModel — démarrage](https://github.com/4sval/FModel/wiki/Getting-Started) : charger les archives, ouvrir **Folders**, puis le dossier du projet et **Content**. Certaines prévisualisations demandent des mappings `.usmap` ou des adaptations propres au jeu. Un index lisible ne garantit pas qu'une texture, un mesh ou un Blueprint est entièrement décodable.

Le profil FModel s'ajoute avec `scripts/configure_fmodel.py`, application fermée. Le script sauvegarde la configuration existante et conserve les autres jeux. Les fichiers exportés restent sous `.tools/exports/<jeu>`.

UModel sert notamment à retrouver l'interface « Choose a package to open ». L'exécutable figé ici date de 2022 ; il n'est pas présenté comme un lecteur générique de tous les assets UE5.

UAssetGUI s'utilise sur des fichiers compatibles déjà extraits, avec leurs compagnons. UAssetAPI est une bibliothèque et non un explorateur d'archives ; UAssetGUI fournit son interface graphique.

## 9. Vérifier avant de partager

Contrôler les états de lecture, les erreurs du parseur, les doublons d'index, les comptes du registre et les fichiers absents. Tester le filtrage du rapport et un cas concret dans FModel.

Partager la méthode, les versions d'outils, les profils et une synthèse dérivée. Garder localement les assets, INI originaux, registres complets, clés, mappings et binaires. `git status`, `git diff --cached --stat` et `.gitignore` permettent de vérifier la sélection avant un commit.
