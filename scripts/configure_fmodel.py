"""Add a game profile to FModel without deleting other game profiles."""
import argparse
import datetime
import os
from pathlib import Path
import shutil
from common import REPO, read_json, save_json

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',required=True,type=Path)
    parser.add_argument('--game-dir',required=True,type=Path)
    parser.add_argument('--activate',action='store_true',help='Select this game at the next FModel launch')
    args=parser.parse_args()
    profile=read_json(args.profile); game=args.game_dir.resolve(strict=True)
    paks=(game/profile['paks']).resolve(strict=True)
    if not paks.is_relative_to(game):parser.error('PAK directory escapes installation')
    config=Path(os.environ['APPDATA'])/'FModel/AppSettings.json'
    config.parent.mkdir(parents=True,exist_ok=True)
    data=read_json(config) if config.exists() else {}
    if config.exists():
        backup=REPO/'.tools/settings-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S%f.json')
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(config,backup)
    key=str(paks)
    old=data.setdefault('PerDirectory',{}).get(key,{})
    data['PerDirectory'][key]={
        **old,'GameName':profile['name'],'GameDirectory':key,'IsManual':True,
        'UeVersion':profile['cue4parse_game'],'TexturePlatform':old.get('TexturePlatform','DesktopMobile'),
        'Versioning':old.get('Versioning',{}),'Endpoints':old.get('Endpoints',[{},{}]),'Directories':old.get('Directories',[]),
        'AesKeys':old.get('AesKeys',{'MainKey':'','DynamicKeys':[]}),
        'LastAesReload':old.get('LastAesReload',datetime.datetime.now().isoformat()),
        'CriwareDecryptionKey':old.get('CriwareDecryptionKey',0),'UnluacOpCodeMap':old.get('UnluacOpCodeMap','')
    }
    if args.activate or not data.get('GameDirectory'):
        data['GameDirectory']=key
        output=REPO/'.tools/exports'/profile['id']
        output.mkdir(parents=True,exist_ok=True);data['OutputDirectory']=str(output)
        for field,folder in [('RawDataDirectory','Raw'),('PropertiesDirectory','Properties'),('TextureDirectory','Textures'),('AudioDirectory','Audio'),('CodeDirectory','Code'),('ModelDirectory','Models')]:
            path=output/folder;path.mkdir(parents=True,exist_ok=True);data[field]=str(path)
    # Keep initial setup deterministic; normal update checks resume tomorrow.
    data['LastUpdateCheck']=datetime.datetime.now().isoformat()
    data['NextUpdateCheck']=(datetime.datetime.now()+datetime.timedelta(days=1)).isoformat()
    save_json(config,data)
    print(f'FModel profile added: {profile["name"]} / {profile["cue4parse_game"]}')

if __name__=='__main__':main()
