# Benchmark de modèles d’IA sur OpenTDB

Ce projet compare les réponses de modèles de langage à des questions de culture générale issues de [Open Trivia Database (OpenTDB)](https://opentdb.com/). Il enregistre les réponses, les évalue automatiquement et expose des indicateurs dans un tableau de bord Streamlit.

## Objectif

Comparer, sur un même échantillon de questions, l’effet du modèle et de la formulation du prompt sur :

- la précision des réponses évaluables ;
- le temps de réponse ;
- la longueur des réponses ;
- les erreurs d’appel et les réponses ambiguës.

Les prompts fournis sont `v1_free` (réponse libre) et `v2_concise` (réponse courte, sans explication). Les options du modèle sont fixées dans `src/run_models.py` (`temperature=0`, `seed=42`, `num_predict=256`).

## Architecture et données

Le traitement suit les étapes suivantes :

1. **Bronze** — questions récupérées depuis l’API OpenTDB dans `data/bronze/questions_raw.csv`.
2. **Silver** — questions décodées, dédupliquées et enregistrées dans `data/silver/questions.parquet` ; réponses des modèles et résultats d’évaluation dans les autres fichiers Parquet du même dossier.
3. **Gold** — modèles dbt qui joignent les questions et les réponses, puis agrègent les métriques dans `data/gold/benchmark.duckdb`.
4. **Dashboard** — `app/streamlit_app.py` lit la table `mart_benchmark` de la base DuckDB.

## Prérequis

- Python 3.10 ou une version ultérieure ;
- Ollama installé et démarré localement ;
- le modèle Ollama utilisé téléchargé (par défaut `llama3.2:3b`) ;
- une connexion Internet pour récupérer les questions OpenTDB.

Le serveur Ollama doit répondre à l’adresse `http://localhost:11434`. Le nom de modèle est configurable lors de l’exécution de `src/run_models.py`.

## Installation

Depuis la racine du dépôt :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Vérifiez qu’Ollama fonctionne et récupérez le modèle souhaité, par exemple :

```bash
ollama pull llama3.2:3b
```

## Reproduire le benchmark

Exécutez les étapes depuis la racine du dépôt, dans cet ordre :

```bash
# 1. Récupérer puis nettoyer les questions OpenTDB
python src/collect_opentdb.py
python src/clean.py

# 2. Interroger Ollama sur 200 questions (modèle et nombre configurables)
python src/run_models.py llama3.2:3b 200

# 3. Évaluer les réponses des modèles
python src/evaluate.py

# 4. Construire les modèles dbt et la base DuckDB
cd dbt_project
dbt build --profiles-dir .
cd ..

# 5. Lancer le tableau de bord
streamlit run app/streamlit_app.py
```

Ouvrez l’adresse locale indiquée par Streamlit. Le tableau de bord permet de filtrer par modèle, prompt, catégorie et difficulté. Pour tester un autre modèle, assurez-vous d’abord qu’il est disponible dans Ollama, puis relancez `run_models.py` avec son nom. Les fichiers `runs_*.parquet` sont lus ensemble lors de l’évaluation.

## Méthodologie d’évaluation

Les réponses sont normalisées (minuscules, accents et ponctuation retirés, articles anglais courants ignorés). Une réponse est considérée correcte si elle contient la réponse attendue normalisée et ne contient pas une réponse incorrecte normalisée. Si elle contient à la fois la réponse attendue et une réponse incorrecte, elle est marquée **ambiguë**. Les erreurs d’appel sont conservées avec leur statut.

La précision affichée est `nombre de réponses correctes / nombre de réponses évaluées`. Les réponses ambiguës et les erreurs d’appel sont exclues de ce dénominateur. Le tableau de bord présente également les temps moyens, longueurs de réponse, erreurs et ambiguïtés.

## Limites

- La détection automatique par présence de texte est approximative : elle peut manquer une bonne réponse formulée autrement ou accepter une réponse qui ne répond pas réellement à la question.
- L’évaluation dépend des réponses attendues fournies par OpenTDB et traite mal certaines variantes, synonymes, nombres ou réponses multilingues.
- Les résultats dépendent du modèle, de sa version, des options d’inférence, de l’échantillon choisi et de l’état de la machine locale. Le tirage des questions utilise une graine fixe (`42`) pour faciliter la comparaison lorsque le jeu de données ne change pas.
- L’échantillon est limité au nombre de questions disponibles dans les données nettoyées ; la collecte OpenTDB peut être soumise à des limites de débit ou de disponibilité.
- Les mesures de temps sont faites localement et ne sont pas directement comparables entre machines.

## Structure du dépôt

```text
src/                 Collecte, nettoyage, exécution et évaluation
data/bronze/         Données brutes OpenTDB
data/silver/         Fichiers Parquet nettoyés et résultats
dbt_project/         Modèles staging, intermediate et mart
app/                 Tableau de bord Streamlit
```
