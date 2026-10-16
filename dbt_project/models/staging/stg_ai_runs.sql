select question_id, model_name, prompt_version, ai_answer, ai_correct, eval_status,
       call_status, response_time, run_date
from read_parquet('../data/silver/ai_runs.parquet')
