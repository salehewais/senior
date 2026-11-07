#!/usr/bin/env python3
import json, sys
from pathlib import Path

def find_value(obj):
    if isinstance(obj, dict):
        if 'full' in obj and 'title' in obj:
            return obj
        for v in obj.values():
            found = find_value(v)
            if found:
                return found
    return None

cdp_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
val = find_value(json.loads(cdp_path.read_text()))
if not val:
    raise SystemExit(f'no value in {cdp_path}')
meta = '\n'.join([
    '---',
    f"title: {val['title']}",
    f"url: {val['url']}",
    f"h1s: {val.get('h1s')}",
    f"len: {val['len']}",
    f"msgCount: {val.get('msgCount')}",
    '---',
    '',
    '',
])
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(meta + val['full'] + '\n', encoding='utf-8')
print(val['title'], 'len=', val['len'], 'msgs=', val.get('msgCount'), '->', out_path)
print('H1s:')
for h in val.get('h1s') or []:
    print(' -', h)
