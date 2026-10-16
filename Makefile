PYTHON ?= python3

.PHONY: run

run:
	@test -f data/processed/index/embeddings.npy || { echo "Manca embeddings.npy"; exit 1; }
	@test -f data/processed/index/metadata.jsonl || { echo "Manca metadata.jsonl"; exit 1; }
	@test -f data/processed/index/manifest.json || { echo "Manca manifest.json"; exit 1; }
	$(PYTHON) -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.fileWatcherType none
