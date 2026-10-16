import ast, hashlib
from urllib.parse import unquote
import pandas as pd

df = pd.read_csv("data/bronze/questions_raw.csv")
n_raw = len(df)
for c in ["type", "difficulty", "category", "question", "correct_answer"]:
    df[c] = df[c].map(unquote)
df["incorrect_answers"] = df["incorrect_answers"].map(lambda s: [unquote(x) for x in ast.literal_eval(s)])
df["question_id"] = df["question"].map(lambda s: hashlib.md5(s.encode()).hexdigest()[:12])
df = df.drop_duplicates("question_id")
df = df.rename(columns={"type": "question_type"})
df.to_parquet("data/silver/questions.parquet", index=False)
print(f"{n_raw} lignes brutes -> {len(df)} questions uniques")
