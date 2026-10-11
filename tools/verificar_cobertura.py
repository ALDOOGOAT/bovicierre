#!/usr/bin/env python3
"""Verifica que los IDs y archivos exigidos por docs/spec/megaprompt.md existen en el repo (fuera de la spec)."""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs/spec/megaprompt.md"
spec = SPEC.read_text(encoding="utf-8")
corpus = "\n".join(
    p.read_text(encoding="utf-8", errors="ignore")
    for p in ROOT.rglob("*")
    if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".sql", ".java", ".ts", ".tsx"}
    and p != SPEC and ".git" not in p.parts and "graphify-out" not in p.parts
)

patrones = {
    "AC": r"AC-\d{2}", "RN": r"RN-\d{3}", "ENT": r"ENT-\d{2}", "REL": r"REL-\d{2}",
    "GOLD": r"GOLD-\d{2}", "TEST": r"TEST-\d{2}", "TASK": r"TASK-[AJ]-\d{3}",
    "ADR": r"ADR-\d{3}", "F": r"\bF\d{2}\b", "RNF": r"RNF-\d{2}",
}
fallas = 0
for nombre, pat in patrones.items():
    ids = sorted(set(re.findall(pat, spec)))
    faltan = [i for i in ids if not re.search(re.escape(i) + r"\b", corpus)]
    fallas += len(faltan)
    print(f"{nombre:5} {len(ids)-len(faltan):3}/{len(ids):<3} " + ("OK" if not faltan else "FALTAN: " + ", ".join(faltan)))

# Archivos obligatorios de §14.2 (tabla "Archivo | Contenido mínimo")
seccion = spec.split("## 14.2")[1].split("## 14.3")[0]
for ruta in re.findall(r"^\| (README\.md|CLAUDE\.md|docs/[^ |]+) \|", seccion, re.M):
    p = ROOT / ruta
    ok = p.is_dir() and any(p.iterdir()) if ruta.endswith("/") else p.is_file() and p.stat().st_size > 200
    fallas += not ok
    print(f"{'OK ' if ok else 'FALTA'} {ruta}")

sys.exit(1 if fallas else 0)
