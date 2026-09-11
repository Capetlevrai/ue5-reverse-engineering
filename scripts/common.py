"""Small shared helpers. No third-party Python dependencies."""
from pathlib import Path
import json
import re

REPO = Path(__file__).resolve().parents[1]

def read_json(path):
    text = Path(path).read_text(encoding='utf-8-sig')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        text = re.sub(r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\r\n]*', lambda m: m[0] if m[0].startswith('"') else '', text)
        text = re.sub(r'"(?:\\.|[^"\\])*"|,(?=\s*[}\]])', lambda m: m[0] if m[0].startswith('"') else '', text)
        return json.loads(text)

def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def safe_child(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Path escapes output directory: {relative}')
    return path
