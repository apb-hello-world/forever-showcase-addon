import sys, unittest, os, json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import curseforge as cf

class CurseForgeTests(unittest.TestCase):
    def test_upload_only_runtime_archive(self):
        calls=[]
        def api(path,payload=None,content_type=None):
            if path == '/game/wow/versions':
                return [{'id':123,'name':'1.60.1','gameVersionTypeID':88568}]
            calls.append((path,payload,content_type))
            return {'id':456}
        tag='addon-v'+cf.version()
        with patch.dict(os.environ,{'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/tags/'+tag,'GITHUB_RUN_ATTEMPT':'1'},clear=True), patch.object(cf,'api',side_effect=api):
            cf.upload(tag)
        self.assertEqual(calls[0][0],'/projects/1832297/upload-file')
        self.assertIn(b'ForeverShowcase-'+cf.version().encode()+b'.zip',calls[0][1])
        self.assertNotIn(b'ForeverShowcaseExample/',calls[0][1])
        self.assertNotIn(b'companion/app.py',calls[0][1])

    def test_guardrails(self):
        with self.assertRaises(ValueError): cf.build('addon-v999.0.0')
        with patch.dict(os.environ,{'GITHUB_EVENT_NAME':'workflow_dispatch'},clear=True), self.assertRaises(ValueError): cf.upload('addon-v'+cf.version())
        tag='addon-v'+cf.version()
        with patch.dict(os.environ,{'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/tags/'+tag,'GITHUB_RUN_ATTEMPT':'2'},clear=True), self.assertRaises(ValueError): cf.upload(tag)
        with patch.object(cf,'api',return_value=[]), self.assertRaises(ValueError): cf.game_version()
