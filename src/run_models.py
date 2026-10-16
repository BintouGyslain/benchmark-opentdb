import sys, time, datetime as dt
import pandas as pd, requests

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:3b"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
URL = "http://localhost:11434/api/generate"
OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 256}
PROMPTS = {
    "v1_free": "Answer this general knowledge question: {question}",
    "v2_concise": "Answer with ONLY the answer (max 5 words, no explanation). Question: {question}",
}

q = pd.read_parquet("data/silver/questions.parquet").sample(N, random_state=42)
rows = []
for r in q.itertuples():
    for version, tpl in PROMPTS.items():
        prompt = tpl.format(question=r.question)
        t0 = time.perf_counter()
        try:
            resp = requests.post(URL, json={"model": MODEL, "prompt": prompt, "stream": False,
                                            "options": OPTIONS}, timeout=120)
            resp.raise_for_status()
            answer, status, err = resp.json()["response"].strip(), "ok", None
        except Exception as e:
            answer, status, err = None, "error", str(e)[:200]
        rows.append(dict(question_id=r.question_id, model_name=MODEL, prompt_version=version,
                         prompt_text=prompt, model_options=str(OPTIONS), ai_answer=answer,
                         response_time=round(time.perf_counter() - t0, 3), call_status=status,
                         error_message=err, run_date=dt.datetime.now(dt.timezone.utc).isoformat()))
    if len(rows) % 20 == 0:
        print(len(rows), "appels")

safe = MODEL.replace(":", "_").replace("/", "_")
pd.DataFrame(rows).to_parquet(f"data/silver/runs_{safe}.parquet", index=False)
