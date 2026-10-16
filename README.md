# Benchmark de modèles d'IA sur OpenTDB
## Méthodologie
## Installation
## Reproduire
python3 src/collect_opentdb.py && python3 src/clean.py
python3 src/run_models.py llama3.2:3b 200 && python3 src/evaluate.py
cd dbt_project && dbt build --profiles-dir . && cd ..
streamlit run app/streamlit_app.py
## Limites
