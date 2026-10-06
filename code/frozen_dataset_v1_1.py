"""Public derived v1.1 loader: verified input, pinned SHA and manifest verification."""
from pathlib import Path
import hashlib,json,csv,io
BASE=Path(__file__).resolve().parent
DATASET=BASE.parent/'data/final_analysis_dataset_public.csv'
MANIFEST=BASE.parent/'data/dataset_manifest.json'
EXPECTED_SHA256='8bd4009cd2c2f6136e2b99ebb21cd496399b9b899a553f2acec0b78aeba9f963'
def _verified_bytes():
 m=json.loads(MANIFEST.read_text(encoding='utf-8'))
 entry=next((r for r in m['files'] if r['path']=='final_analysis_dataset_public.csv'),None)
 if m.get('dataset_sha256')!=EXPECTED_SHA256 or not entry or entry['sha256']!=EXPECTED_SHA256:
  raise RuntimeError('v1.1 frozen manifest hash mismatch')
 b=DATASET.read_bytes()
 if hashlib.sha256(b).hexdigest()!=EXPECTED_SHA256:raise RuntimeError('v1.1 frozen dataset SHA-256 mismatch')
 return b
def load_rows():return list(csv.DictReader(io.StringIO(_verified_bytes().decode('utf-8'))))
def verified_path():
 _verified_bytes()
 return DATASET
