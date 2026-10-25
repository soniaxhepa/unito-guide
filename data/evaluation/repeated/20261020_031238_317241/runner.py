"""Three repetitions of the current RAG/No-RAG configuration; old data untouched."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
import urllib.request


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def api(url, payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        url, data=data, headers={'Content-Type': 'application/json'},
        method='GET' if payload is None else 'POST',
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def append_json(path, value):
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.home() / 'HCI-STAGE')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--resume', type=Path)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    sys.path.insert(0, str(root))
    from src.rag.generate import build_context, build_prompt, LLM_MODEL, OLLAMA_URL
    from src.retrieval.search import search
    from src.evaluation.compare_generation import NO_RAG_PROMPT

    questions_path = root / 'data/evaluation/final_test_questions_FROZEN.csv'
    with questions_path.open(encoding='utf-8-sig', newline='') as handle:
        questions = list(csv.DictReader(handle))
    ids = [q['query_id'] for q in questions]
    if len(questions) != 40 or len(set(ids)) != 40:
        raise RuntimeError('Sono richieste 40 domande con identificativi distinti.')
    if LLM_MODEL != 'llama3.2:3b':
        raise RuntimeError('Il modello configurato non è llama3.2:3b.')

    base = OLLAMA_URL.rsplit('/api/', 1)[0]
    tags = api(base + '/api/tags')
    installed = next((m for m in tags.get('models', [])
                      if m.get('name') == LLM_MODEL), None)
    if installed is None:
        raise RuntimeError('Modello non installato in Ollama: ' + LLM_MODEL)
    tracked = [questions_path]
    tracked += sorted((root / 'src').rglob('*.py'))
    tracked += sorted((root / 'data/processed').rglob('*'))
    tracked += sorted((root / 'data/sources').rglob('*'))
    tracked += [root / 'data/evaluation/chunk_exclusions.csv']
    tracked = sorted(set(p for p in tracked if p.is_file()))
    hashes = {str(p.relative_to(root)): digest(p) for p in tracked}
    for name in ('embeddings.npy', 'metadata.jsonl', 'manifest.json'):
        if not (root / 'data/processed/index' / name).is_file():
            raise RuntimeError('File dell’indice mancante: ' + name)

    print('Domande congelate: 40', flush=True)
    print('Ripetizioni: 3; modalità: RAG e No-RAG; risposte previste: 240', flush=True)
    print('Modello: ' + LLM_MODEL + '; temperatura: 0.2; top-k RAG: 5', flush=True)
    print('Ollama disponibile; indice presente.', flush=True)
    if args.check:
        print('Controllo completato. Nessuna generazione avviata e nessun risultato modificato.')
        return

    if args.resume:
        folder = args.resume.expanduser().resolve()
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        if manifest['file_sha256'] != hashes or manifest['model_digest'] != installed.get('digest'):
            raise RuntimeError('Codice, dati o modello cambiati: impossibile riprendere questa esecuzione.')
    else:
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        folder = root / 'data/evaluation/repeated' / stamp
        folder.mkdir(parents=True, exist_ok=False)
        for path in tracked:
            target = folder / 'snapshot' / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        shutil.copy2(Path(__file__), folder / 'runner.py')
        packages = sorted((d.metadata['Name'] or '', d.version)
                          for d in importlib.metadata.distributions())
        write_json(folder / 'environment.json', {
            'python': sys.version, 'executable': sys.executable,
            'platform': platform.platform(), 'packages': packages,
            'ollama_version': api(base + '/api/version'),
            'ollama_model': installed,
            'ollama_show': api(base + '/api/show', {'model': LLM_MODEL}),
        })
        try:
            revision = subprocess.check_output(
                ['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        except Exception:
            revision = None
        manifest = {
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'protocol': 'Three repetitions of the current configuration; not historical reruns.',
            'repetitions': 3, 'questions': 40, 'expected_answers': 240,
            'model': LLM_MODEL, 'model_digest': installed.get('digest'),
            'temperature': 0.2, 'rag_top_k': 5,
            'mode_order': ['rag', 'no_rag'], 'question_order': ids,
            'seed': 'not explicitly set', 'num_ctx': 'Ollama/model default',
            'num_predict': 'Ollama/model default', 'git_revision': revision,
            'file_sha256': hashes,
            'latency_scope': 'RAG: retrieval, prompt and generation; No-RAG: prompt and generation; excludes serialization to disk.',
            'timing_note': 'Includes loading and cache effects during ordinary execution; not a controlled cold/warm benchmark.',
            'evaluation_note': 'Manual ratings still required; old test and exploratory reuse prevent treating these questions as an untouched holdout.',
        }
        write_json(folder / 'manifest.json', manifest)
        write_json(folder / 'prompts.json', {'no_rag_template': NO_RAG_PROMPT})

    print('CARTELLA RISULTATI: ' + str(folder), flush=True)
    result_path = folder / 'responses.jsonl'
    completed = set()
    if result_path.exists():
        raw = result_path.read_bytes()
        if raw and not raw.endswith(b'\n'):
            raise RuntimeError('Ultima riga incompleta: conservare il file e verificarlo prima di riprendere.')
        for line in raw.decode('utf-8').splitlines():
            row = json.loads(line)
            key = (row['run_id'], row['query_id'], row['mode'])
            if key in completed:
                raise RuntimeError('Risposta duplicata: ' + str(key))
            completed.add(key)

    for run in range(1, 4):
        for question in questions:
            for mode in ('rag', 'no_rag'):
                key = (run, question['query_id'], mode)
                if key in completed:
                    continue
                # Refuse to mix changed source files or data into an existing experiment.
                if any(digest(root / name) != value for name, value in hashes.items()):
                    raise RuntimeError('Codice o dati modificati durante l’esperimento.')
                print(f'[{len(completed)+1}/240] Ripetizione {run} | {question["query_id"]} | {mode}', flush=True)
                start = time.perf_counter()
                results = search(question['question'], 5) if mode == 'rag' else []
                context = build_context(results) if mode == 'rag' else ''
                prompt = (build_prompt(question['question'], context) if mode == 'rag'
                          else NO_RAG_PROMPT.format(question=question['question']))
                payload = {'model': LLM_MODEL, 'prompt': prompt, 'stream': False,
                           'options': {'temperature': 0.2}}
                request_id = f'{run}_{question["query_id"]}_{mode}'
                preparation_seconds = time.perf_counter() - start
                append_json(folder / 'requests.jsonl', {
                    'request_id': request_id, 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                    'request': payload, 'retrieved_results': results,
                })
                try:
                    generation_start = time.perf_counter()
                    response = api(OLLAMA_URL, payload)
                    if response.get('error') or 'response' not in response or not response.get('done'):
                        raise RuntimeError('Risposta Ollama incompleta o con errore: ' + str(response.get('error')))
                    elapsed = preparation_seconds + time.perf_counter() - generation_start
                    row = {
                        **question, 'run_id': run, 'mode': mode,
                        'answer': response['response'].strip(), 'prompt': prompt,
                        'retrieved_chunks': [r['chunk_id'] for r in results],
                        'latency_seconds': elapsed, 'model': LLM_MODEL,
                        'temperature': 0.2, 'top_k': 5 if mode == 'rag' else 0,
                        'ollama_result': response,
                    }
                    append_json(result_path, row)
                    completed.add(key)
                    print(f'Salvata; tempo {elapsed:.1f} s; arresto: {response.get("done_reason")}', flush=True)
                except Exception as exc:
                    append_json(folder / 'errors.jsonl', {'request_id': request_id, 'error': repr(exc)})
                    raise

    rows = [json.loads(line) for line in result_path.read_text(encoding='utf-8').splitlines()]
    fields = ['run_id', 'query_id', 'mode', 'question', 'expected_behavior',
              'expected_answer', 'supporting_chunk_ids', 'answer', 'retrieved_chunks',
              'latency_seconds', 'model', 'temperature', 'top_k', 'correctness',
              'completeness', 'grounding', 'citations', 'unsupported_claims',
              'abstention', 'error_type', 'notes']
    with (folder / 'manual_evaluation.csv').open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            copy = dict(row)
            copy['retrieved_chunks'] = json.dumps(copy['retrieved_chunks'])
            writer.writerow(copy)
    write_json(folder / 'completion.json', {'answers': len(rows), 'expected': 240,
                                           'completed_utc': datetime.now(timezone.utc).isoformat()})
    print('Generazione completata: 240 risposte. Valutazione manuale ancora da svolgere.', flush=True)
    print('RISULTATI: ' + str(folder), flush=True)


if __name__ == '__main__':
    main()
