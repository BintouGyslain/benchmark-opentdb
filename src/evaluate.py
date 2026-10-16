import re, glob, unicodedata
import pandas as pd

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(the|a|an)\b", " ", s)
    return " ".join(s.split())

def contains(text, ans):
    a = norm(ans)
    return bool(a) and f" {a} " in f" {text} "

def judge(r):
    if r.call_status != "ok" or not r.ai_answer:
        return None, "error"
    if not norm(r.correct_answer):
        return None, "unevaluable"
    t = norm(r.ai_answer)
    ok = contains(t, r.correct_answer)
    bad = any(contains(t, x) for x in r.incorrect_answers)
    if ok and not bad:
        return True, "evaluated"
    if ok and bad:
        return None, "ambiguous"
    return False, "evaluated"

runs = pd.concat([pd.read_parquet(f) for f in glob.glob("data/silver/runs_*.parquet")])
qs = pd.read_parquet("data/silver/questions.parquet")[["question_id", "correct_answer", "incorrect_answers"]]
df = runs.merge(qs, on="question_id", how="left")
res = [judge(r) for r in df.itertuples()]
df["ai_correct"] = [x[0] for x in res]
df["eval_status"] = [x[1] for x in res]
df.drop(columns=["correct_answer", "incorrect_answers"]).to_parquet("data/silver/ai_runs.parquet", index=False)
print(df.eval_status.value_counts())
