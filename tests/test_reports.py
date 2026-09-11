import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import read_json, safe_child, save_json
from report import build_report

class ReportTests(unittest.TestCase):
    def test_unreal_json_comments_preserve_urls_and_strings(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'plugin.json'
            p.write_text('{"url":"https://example.test/a//b",/* comment */"text":"comma,}","list":[1,],}',encoding='utf-8')
            self.assertEqual(read_json(p),{'url':'https://example.test/a//b','text':'comma,}','list':[1]})

    def test_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(safe_child(d,'metadata/Game/a.ini'),Path(d).resolve()/'metadata/Game/a.ini')
            with self.assertRaises(ValueError):safe_child(d,'../outside')

    def test_encrypted_empty_index_is_not_reported_as_absence(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);raw=out/'raw';raw.mkdir()
            save_json(raw/'scan-summary.json',{'profile':'GAME_UE5_LATEST','archiveReaders':1,'mountedReaders':0,'encryptedIndexedFiles':0})
            save_json(raw/'archives.json',[{'name':'a.pak','mounted':False,'encryptedIndex':True,'hasDirectoryIndex':True,'entries':0}])
            save_json(raw/'metadata-manifest.json',[]);save_json(raw/'registries.json',[])
            save_json(out/'installation-files.json',[{'path':'Project/Plugins/Audio/Binaries/a.dll','bytes':10,'mtime_ns':1}])
            (raw/'files.jsonl').write_text('',encoding='utf-8')
            result=build_report(out,{'name':'Example','project':'Project','version_evidence':'unknown'})
            self.assertEqual(result['status'],'blocked-encrypted-indexes')
            self.assertEqual(result['looseBinaryFiles'],1)
            self.assertEqual(result['registryStatus'],'not-found-in-readable-indexes')
            self.assertIn('ne signifient pas', (out/'RAPPORT.md').read_text(encoding='utf-8'))

    def test_failed_registration_and_independent_index_remain_partial(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);raw=out/'raw';raw.mkdir()
            save_json(raw/'scan-summary.json',{'profile':'GAME_ArcRaiders','archiveReaders':1,'mountedReaders':1,'encryptedIndexedFiles':0})
            save_json(raw/'archives.json',[{'name':'a.utoc','mounted':True,'encryptedIndex':False,'hasDirectoryIndex':True,'entries':1}])
            save_json(raw/'scan-diagnostics.json',[{'stage':'registration','archive':'a.pak','error':'unknown format'}])
            save_json(raw/'metadata-manifest.json',[]);save_json(raw/'registries.json',[])
            save_json(out/'installation-files.json',[
                {'path':'Project/Content/Paks/a.pak','bytes':100},
                {'path':'Engine/Programs/CrashReportClient/Content/Paks/a.pak','bytes':10},
                {'path':'Project/Script/Gameplay/Test.as','bytes':42}])
            (raw/'files.jsonl').write_text('',encoding='utf-8')
            profile={'name':'Example','project':'Project','version_evidence':'unknown'}
            self.assertEqual(build_report(out,profile)['status'],'blocked-format')
            (raw/'files.jsonl').write_text(json.dumps({'path':'Engine/Plugins/FX/Niagara/Content/Test.uasset','archive':'a.utoc'})+'\n',encoding='utf-8')
            result=build_report(out,profile)
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['containerFiles'],{'.pak':1})
            self.assertEqual(result['indexedPluginContentRoots'],1)
            self.assertEqual(result['pluginDescriptors'],0)
            self.assertEqual(result['looseScriptFiles'],1)
            self.assertEqual(result['looseScriptBytes'],42)

if __name__=='__main__':unittest.main()
