from pathlib import Path
import duckdb, streamlit as st

st.set_page_config(page_title="Benchmark IA - OpenTDB", layout="wide")
DB = Path(__file__).resolve().parents[1] / "data/gold/benchmark.duckdb"
df = duckdb.connect(str(DB), read_only=True).execute("select * from mart_benchmark").df()

st.title("Benchmark de modèles d'IA sur OpenTDB")
sb = st.sidebar
f = df[
    df.model_name.isin(sb.multiselect("Modèle", sorted(df.model_name.unique()), sorted(df.model_name.unique())))
    & df.prompt_version.isin(sb.multiselect("Prompt", sorted(df.prompt_version.unique()), sorted(df.prompt_version.unique())))
    & df.category.isin(sb.multiselect("Catégorie", sorted(df.category.unique()), sorted(df.category.unique())))
    & df.difficulty.isin(sb.multiselect("Difficulté", ["easy", "medium", "hard"], ["easy", "medium", "hard"]))
]

SUMS = ["n_calls", "n_errors", "n_ambiguous", "n_evaluated", "n_correct", "sum_response_time", "sum_answer_length"]

def agg(d, by):
    g = d.groupby(by, as_index=False)[SUMS].sum()
    g["accuracy"] = g.n_correct / g.n_evaluated
    g["avg_response_time"] = g.sum_response_time / g.n_calls
    g["ambiguous_rate"] = g.n_ambiguous / g.n_calls
    g["avg_answer_length"] = g.sum_answer_length / g.n_calls
    return g

tot = f[SUMS].sum()
c = st.columns(4)
c[0].metric("Précision globale", f"{tot.n_correct / max(tot.n_evaluated, 1):.1%}")
c[1].metric("Réponses évaluées", int(tot.n_evaluated))
c[2].metric("Ambiguës", int(tot.n_ambiguous))
c[3].metric("Erreurs d'appel", int(tot.n_errors))
st.caption("Précision = bonnes réponses / réponses évaluées. Erreurs et réponses ambiguës exclues du dénominateur.")

l, r = st.columns(2)
l.subheader("Précision par modèle et prompt")
l.bar_chart(agg(f, ["model_name", "prompt_version"]).pivot(index="model_name", columns="prompt_version", values="accuracy"))
r.subheader("Temps de réponse moyen (s)")
r.bar_chart(agg(f, ["model_name", "prompt_version"]).pivot(index="model_name", columns="prompt_version", values="avg_response_time"))
l.subheader("Précision par difficulté")
l.bar_chart(agg(f, ["difficulty", "model_name"]).pivot(index="difficulty", columns="model_name", values="accuracy"))
r.subheader("Précision par catégorie")
r.bar_chart(agg(f, ["category", "model_name"]).pivot(index="category", columns="model_name", values="accuracy"))

st.subheader("Effet du prompt")
st.dataframe(agg(f, ["model_name", "prompt_version"])[["model_name", "prompt_version", "n_evaluated",
             "accuracy", "ambiguous_rate", "avg_answer_length", "avg_response_time"]])
