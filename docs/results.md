# Sorties et limites

Chaque dossier `runs/<jeu>/<horodatage>/` est un instantané indépendant et ignoré par Git.

| Fichier | Contenu |
|---|---|
| `explorer.html` | Rapport autonome avec recherche ; 500 lignes maximum affichées à la fois |
| `RAPPORT.md`, `summary.json` | Synthèse, compteurs et limites |
| `profile.json` | Profil utilisé et justification de version |
| `installation-files.json` | Fichiers livrés, chemins relatifs, tailles et dates |
| `verification.json` | Comparaison avant/après ; indique si le scan brut a été réutilisé |
| `plugins.json` | Descripteurs complets, versions, modules, dépendances et déclarations |
| `project-plugin-declarations.json` | Déclarations explicites, y compris désactivations et plateformes |
| `content-folders.json` | Dossiers racines, fichiers et packages `.uasset/.umap` |
| `maps.json` | Chemins `.umap` et archives sources |
| `blueprints.json`, `classes.json` | Informations issues d'un registre effectivement parsé |
| `module-references.json` | Références `/Script/...` trouvées dans les tags du registre |
| `loose-binaries.json`, `loose-components.json` | Fichiers présents hors archives ; indices de composants |
| `loose-scripts.json`, `loose-script-folders.json` | Chemins, tailles et regroupement des fichiers `.as` livrés ; aucun contenu source copié |
| `indexed-plugin-content.json` | Racines `/Plugins/.../Content/` visibles dans les index ; ne remplace pas les descripteurs |
| `raw/scan-diagnostics.json` | Archives non enregistrées, erreur de montage global et échecs du repli indépendant |
| `raw/archives.json` | Lecteurs, montages, chiffrement, compression, GUID |
| `raw/indexes/*.jsonl` | Un index par archive, conservant les chemins en doublon entre archives |
| `raw/files.jsonl`, `raw/all-paths.txt` | Index effectif consolidé selon la priorité du fournisseur |
| `raw/metadata-manifest.json` | Succès/échecs, provenance, tailles et SHA256 des métadonnées |
| `raw/metadata/` | Métadonnées originales extraites |
| `raw/registries.json`, `raw/registry-*.jsonl` | Résultat de chaque registre et tags de toutes les entrées |
| `raw/parser.log`, `scan-console.log`, `build.log` | Diagnostics |

## États

- `indexed` : index et métadonnées ciblées accessibles dans cette passe. Cela ne signifie pas que tous les assets du jeu ont été décodés, ni qu'un registre existe.
- `partial` : données obtenues, mais une lecture, un montage ou une analyse ciblée a échoué.
- `blocked-format` : aucun chemin accessible et erreurs de lecture/enregistrement observées. Le format ou la protection reste à déterminer.
- `blocked-encrypted-indexes` : aucun chemin accessible par le scanner et index chiffrés observés. Un compteur nul signifie « indisponible », pas « absent ».

`registryStatus=not-found-in-readable-indexes` signifie seulement qu'aucun registre portant le nom attendu n'est visible dans les index lus. Avec des index bloqués, aucune conclusion d'absence n'est possible.

## Recherche en ligne de commande

```powershell
python scripts/query.py runs/ff7-rebirth/20260911T000000000000Z Bonamik --limit 20
```

Remplacer l'exemple de dossier par celui affiché après l'analyse. La recherche lit l'index ligne par ligne pour éviter de charger plusieurs centaines de milliers de chemins en mémoire.

## Limites connues

- Le parseur est figé à CUE4Parse 1.2.2.202609 ; de nouveaux jeux peuvent nécessiter une nouvelle version et un nouveau profil.
- Le code conserve les erreurs de registre mais ne reconstruit pas un registre absent.
- Les modules réellement chargés en jeu ne sont pas observés.
- Les versions des DLL ne sont pas inférées depuis leurs dossiers. L'inventaire hors archives conserve les noms et tailles, pas une validation fonctionnelle de chaque bibliothèque.
- Oodle peut être initialisé/téléchargé par CUE4Parse dans le dossier de travail `.tools`. Une DLL Oodle déjà disponible peut être indiquée via `UE_INVENTORY_OODLE`. Elle reste locale.
- Les INI lisibles peuvent contenir des paramètres sensibles ou internes ; les sorties brutes ne sont pas prévues pour une publication automatique.
- Les valeurs d'un `.uproject` décrivent le projet livré : elles ne constituent pas une annonce commerciale de plateformes ou fonctionnalités futures.

## Montage indépendant des index

Si le montage global CUE4Parse lève une exception, le scanner conserve cette erreur puis tente de monter séparément chaque index de répertoires admissible. Les montages réussis sont comptés dans `mountedReaders`, même si la collection interne du fournisseur ne les comptabilise pas. Cela permet de cataloguer des chemins sans pouvoir lire les objets globaux, comme pour ARC Raiders. Une archive non enregistrée est également signalée : elle ne disparaît pas silencieusement des contrôles de couverture.

Le champ `containerFiles` compte uniquement les conteneurs du dossier PAK ciblé par le profil. Les éventuelles archives du CrashReportClient restent dans `installation-files.json`. Le scan vise les index et métadonnées : des chemins lisibles ne prouvent pas que les données des assets sont décodables.
