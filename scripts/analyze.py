"""Inventory an installed Unreal game. All output stays outside its installation."""
import argparse
from collections import Counter
import datetime
from pathlib import Path
import subprocess
import sys

from common import REPO, read_json, save_json

def snapshot(game):
    return [{'path':p.relative_to(game).as_posix(),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in sorted(game.rglob('*')) if p.is_file()]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',required=True,type=Path)
    parser.add_argument('--game-dir',required=True,type=Path)
    parser.add_argument('--out',type=Path,help='New/empty run directory; defaults to runs/<id>/<UTC timestamp>')
    parser.add_argument('--reuse-raw',action='store_true',help='Build a report from an existing raw/ scan; do not scan again')
    args=parser.parse_args()
    profile=read_json(args.profile)
    game=args.game_dir.resolve(strict=True)
    paks=(game/profile['paks']).resolve(strict=True)
    if not paks.is_relative_to(game): parser.error('PAK path escapes the game directory')
    out=(args.out or REPO/'runs'/profile['id']/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')).resolve()
    if out==game or out.is_relative_to(game): parser.error('Output must be outside the game installation')
    if out.exists() and any(out.iterdir()) and not args.reuse_raw: parser.error('Output must be new/empty; use a new run directory')
    if args.reuse_raw and not (out/'raw/scan-summary.json').is_file(): parser.error('--reuse-raw requires raw/scan-summary.json')
    before=snapshot(game)
    out.mkdir(parents=True,exist_ok=True)
    save_json(out/'profile.json',profile)
    save_json(out/'installation-files.json',before)
    if not args.reuse_raw:
        csproj=REPO/'src/UnrealInventory/UnrealInventory.csproj'
        build=subprocess.run(['dotnet','build',str(csproj),'-c','Release','--nologo','-p:RestoreLockedMode=true'],capture_output=True,text=True)
        (out/'build.log').write_text(build.stdout+build.stderr,encoding='utf-8')
        if build.returncode: raise RuntimeError(f'Build failed; see {out / "build.log"}')
        exe=csproj.parent/'bin/Release/net10.0/UnrealInventory.dll'
        tools=REPO/'.tools'
        tools.mkdir(exist_ok=True)
        with (out/'scan-console.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(['dotnet',str(exe),str(paks),str(out/'raw'),profile['cue4parse_game']],cwd=tools,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode: raise RuntimeError(f'Scan failed; see {out / "scan-console.log"}')
    from report import build_report
    summary=build_report(out,profile)
    after=snapshot(game)
    save_json(out/'verification.json',{'installation_size_mtime_unchanged':before==after,'verification':'Size + mtime snapshot; not a full content hash','reused_raw':args.reuse_raw})
    print(f"{profile['name']}: {summary['effectiveFiles']:,} indexed paths; {summary['pluginDescriptors']} plugin descriptors; {summary['registryEntries']} registry entries")
    print(f"Report: {out/'explorer.html'}")
    print(f"Status: {summary['status']}")

if __name__=='__main__':
    main()
