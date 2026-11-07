import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

path=Path(__file__).resolve().parents[1]/"scripts"/"prepare_benchmarks.py"
spec=importlib.util.spec_from_file_location("adapter",path)
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class BenchmarkBoundaryTests(unittest.TestCase):
    def test_drugqa_input_uses_whitelist(self):
        row={"id":"x","question":"Which?","choices":["a","b","c","d"],"language":"EN",
             "marked_answer":"B","explanation":"SECRET_GOLD","source":"ANSWER_B","future_gold_field":"SECRET"}
        public=adapter.drugqa_input(row)
        self.assertEqual(set(public),{"id","question","choices","language"})
        self.assertNotIn("SECRET",json.dumps(public))
        public["choices"].append("e")
        self.assertEqual(len(row["choices"]),4)

    def test_invalid_answer_is_not_silently_normalized(self):
        row={"id":"x","question":"Which?","choices":["a","b","c","d"],"language":"EN","marked_answer":"unknown"}
        with self.assertRaises(ValueError):adapter.drugqa_input(row)

    def test_nli_preserves_native_labels_and_hides_annotations(self):
        data={"labels":{"h1":{"hypothesis":"Synthetic claim"}},
              "documents":[{"id":1,"text":"Synthetic text","spans":[[0,9]],"annotation_sets":[
                  {"annotations":{"h1":{"choice":"NotMentioned","spans":[]}}}]}]}
        docs,tasks,gold=adapter.contract_records(data)
        self.assertEqual(gold[0]["label"],"NotMentioned")
        self.assertEqual(gold[0]["evidence_span_ids"],[])
        self.assertNotIn("NotMentioned",json.dumps(docs+tasks))
        self.assertNotIn("annotations",json.dumps(docs+tasks))
        self.assertEqual(tasks[0]["document_id"],docs[0]["id"])

    def test_manifest_rejects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"x").write_bytes(b"changed")
            (root/"SOURCE_MANIFEST.json").write_text(json.dumps({"files":[{"path":"x","bytes":7,"sha256":"not-the-hash"}]}))
            with self.assertRaises(ValueError):adapter.verify_manifest(root)

    def test_manifest_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"SOURCE_MANIFEST.json").write_text(json.dumps({"files":[{"path":"../secret","bytes":0,"sha256":""}]}))
            with self.assertRaises(ValueError):adapter.verify_manifest(root)

if __name__=="__main__":unittest.main()
