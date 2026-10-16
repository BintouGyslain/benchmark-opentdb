select model_name, prompt_version, category, difficulty, question_type,
       count(*) as n_calls,
       count(*) filter (where call_status = 'error') as n_errors,
       count(*) filter (where eval_status = 'ambiguous') as n_ambiguous,
       count(*) filter (where eval_status = 'evaluated') as n_evaluated,
       count(*) filter (where ai_correct) as n_correct,
       sum(response_time) as sum_response_time,
       sum(answer_length) as sum_answer_length,
       median(response_time) as median_response_time
from {{ ref('int_runs_enriched') }}
group by all
