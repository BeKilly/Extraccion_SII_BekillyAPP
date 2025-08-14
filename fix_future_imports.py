#!/usr/bin/env python3
from __future__ import annotations
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
files = []
for base in (ROOT, ROOT / "src"):
    if base.exists():
        files += list(base.rglob("*.py"))

for f in files:
    text = f.read_text(encoding="utf-8")
    if "from __future__ import annotations" not in text:
        continue

    # elimina TODAS las líneas de future import existentes
    text_wo = re.sub(
        r'^[ \t]*from __future__ import annotations[ \t]*\r?\n',
        '',
        text,
        flags=re.MULTILINE,
    )

    lines = text_wo.splitlines(True)
    i = 0

    # shebang en primera línea
    if i < len(lines) and lines[i].startswith("#!"):
        i += 1
    # encoding en línea 1 o 2
    if i < len(lines) and re.search(r'coding[:=]\s*[-\w.]+', lines[i]):
        i += 1

    # saltar blancos y comentarios hasta posible docstring
    j = i
    while j < len(lines) and (lines[j].strip() == "" or lines[j].lstrip().startswith("#")):
        j += 1

    # si hay docstring de módulo, insertar después
    insert_at = j
    if j < len(lines) and (lines[j].lstrip().startswith('"""') or lines[j].lstrip().startswith("'''")):
        quote = lines[j].lstrip()[:3]
        k = j + 1
        found = False
        while k < len(lines):
            if quote in lines[k]:
                found = True
                k += 1
                break
            k += 1
        insert_at = k if found else j

    new_text = "".join(lines[:insert_at]) + "from __future__ import annotations\n" + "".join(lines[insert_at:])
    if new_text != text:
        f.write_text(new_text, encoding="utf-8")
        print(f"Fixed: {f}")
print("Done")
