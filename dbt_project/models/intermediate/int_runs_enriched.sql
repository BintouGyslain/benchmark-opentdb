select r.*, q.category, q.difficulty, q.question_type, length(r.ai_answer) as answer_length
from {{ ref('stg_ai_runs') }} r
left join {{ ref('stg_questions') }} q on r.question_id = q.question_id
