
import json, pathlib
def read_json_file(p:str)->dict: return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
def write_json_file(p, payload): path=pathlib.Path(p); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
