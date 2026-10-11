"""Integra fragmentos semánticos revisados; no sustituye la lectura por agentes."""
import argparse
import json
from pathlib import Path
from graphify.build import build_merge, _is_ast_tier
from graphify.cache import save_semantic_cache
from networkx.readwrite import json_graph

ROOT = Path(__file__).resolve().parents[2]


def semantic_only(chunks, ast_ids, aliases=None):
    aliases = aliases or {}
    for chunk in chunks:
        for edge in chunk['edges']:
            for key in ('source', 'target'):
                edge[key] = aliases.get(edge[key], edge[key])
        for hyper in chunk.get('hyperedges', []):
            hyper['nodes'] = [aliases.get(n, n) for n in hyper['nodes']]
        chunk['nodes'] = [n for n in chunk['nodes'] if n['id'] not in ast_ids and n['id'] not in aliases]
        for item in chunk['nodes'] + chunk['edges']:
            item['_origin'] = 'semantic'


def validate(chunks, existing):
    nodes = [n for chunk in chunks for n in chunk['nodes']]
    known = existing | {n['id'] for n in nodes}
    for chunk in chunks:
        for edge in chunk['edges']:
            if edge['source'] not in known or edge['target'] not in known:
                raise ValueError('Relación sin nodo de procedencia: ' + str(edge))
            if edge['confidence'] == 'EXTRACTED' and edge['confidence_score'] != 1:
                raise ValueError('Confianza extraída inválida')
    return nodes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fragments', nargs='*', type=Path)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        chunk = {'nodes': [{'id': 'a'}], 'edges': [{'source': 'a', 'target': 'b', 'confidence': 'EXTRACTED', 'confidence_score': 1}]}
        assert len(validate([chunk], {'b'})) == 1
        try:
            validate([chunk], set())
        except ValueError:
            pass
        else:
            raise AssertionError('Se aceptó relación sin nodo')
        semantic_only([chunk], {'a'})
        assert not chunk['nodes'] and chunk['edges'][0]['_origin'] == 'semantic'
        alias_chunk = {'nodes': [{'id': 'document'}], 'edges': [{'source': 'document', 'target': 'concept'}], 'hyperedges': [{'nodes': ['document', 'concept']}]}
        semantic_only([alias_chunk], {'page'}, {'document': 'page'})
        assert not alias_chunk['nodes'] and alias_chunk['edges'][0]['source'] == 'page' and alias_chunk['hyperedges'][0]['nodes'][0] == 'page'
        print('PASS validación de fragmentos; no se modificó el grafo')
        return
    if not args.fragments:
        parser.error('Indica fragmentos actuales revisados y sus manifiestos de fuentes')
    graph = ROOT / 'graphify-out/graph.json'
    chunks = [json.loads(p.read_text()) for p in args.fragments]
    old_nodes = json.loads(graph.read_text())['nodes']
    existing = {n['id'] for n in old_nodes}
    ast_ids = {n['id'] for n in old_nodes if _is_ast_tier(n)}
    # Referenciar un método AST existente no autoriza reemplazar todo el AST de su archivo.
    # Graphify reutiliza la página AST para documentos idénticos; conservar esa ancla.
    pages = {(str((ROOT / n['source_file']).resolve()), n.get('label')): n['id']
             for n in old_nodes if n['id'] in ast_ids and n.get('node_kind') == 'page' and n.get('source_file')}
    aliases = {n['id']: pages[(str((ROOT / n['source_file']).resolve()), n.get('label'))]
               for chunk in chunks for n in chunk['nodes']
               if n.get('file_type') == 'document' and n.get('source_file')
               and (str((ROOT / n['source_file']).resolve()), n.get('label')) in pages}
    semantic_only(chunks, ast_ids, aliases)
    nodes = validate(chunks, existing)
    sources = {item['source_file'] for chunk in chunks for item in chunk['nodes'] + chunk['edges'] if item.get('source_file')}
    for source in sources:
        path = Path(source)
        if not path.is_absolute():
            path = ROOT / path
        if not path.resolve().is_relative_to(ROOT) or not path.is_file():
            raise ValueError('Fuente ausente o fuera del proyecto: ' + source)
    # La frescura semántica exige comparar previamente los manifiestos, no renovar hashes a ciegas.
    merged = build_merge(chunks, graph_path=graph, root=ROOT, dedup=False, dedup_llm_backend=None)
    referenced = {e[key] for chunk in chunks for e in chunk['edges'] for key in ('source', 'target')}
    missing = referenced - set(merged)
    if missing:
        raise ValueError('La fusión podó nodos referenciados; declarar sus anclas en el fragmento: ' + str(sorted(missing)))
    graph.write_text(json.dumps(json_graph.node_link_data(merged, edges='links'), ensure_ascii=False, indent=2))
    cached = save_semantic_cache(nodes, [e for c in chunks for e in c['edges']],
        [h for c in chunks for h in c.get('hyperedges', [])], root=ROOT,
        allowed_source_files=sources,
        prompt_file=Path.home() / '.codex/skills/graphify/references/extraction-spec.md')
    print(json.dumps({'nodes': merged.number_of_nodes(), 'edges': merged.number_of_edges(), 'cached_sources': cached}))


if __name__ == '__main__':
    main()
