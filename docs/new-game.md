# Ajouter un autre jeu

1. Repérer le dossier contenant les PAK / UTOC.
2. Créer un profil JSON, par exemple `profiles/example.json` :

```json
{
  "id": "example",
  "name": "Example Game",
  "project": "InternalProjectName",
  "paks": "InternalProjectName/Content/Paks",
  "cue4parse_game": "GAME_UE5_5",
  "version_evidence": "Remplacer par la source de la version choisie ; ne pas supposer UE5.5."
}
```

3. Choisir `cue4parse_game` d'après les sources du jeu et la liste de profils de CUE4Parse. Un profil propre au jeu est préférable lorsqu'il existe.
4. Lancer :

```powershell
python scripts/analyze.py --profile profiles/example.json --game-dir "D:\Games\Example Game"
```

5. Consulter `raw/parser.log`, `raw/archives.json` et `summary.json`. Si l'index est chiffré, documenter cette limite et poursuivre l'inventaire hors archives ; une clé adaptée est nécessaire pour les noms internes.
6. Ajouter le profil à FModel :

```powershell
python scripts/configure_fmodel.py --profile profiles/example.json --game-dir "D:\Games\Example Game" --activate
```

7. Ajouter un retour d'expérience dans `docs/games/` avec date, format, profil, compteurs, preuves et limites. Ne pas copier les sorties brutes dans les documents versionnés.

Les chemins d'installation ne sont pas codés dans les scripts. Le dossier de sortie est neuf à chaque lancement ; on peut le choisir avec `--out`, à condition qu'il soit vide et hors de l'installation du jeu.
