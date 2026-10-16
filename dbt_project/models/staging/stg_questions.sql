select question_id, category, difficulty, question_type, question, correct_answer
from read_parquet('../data/silver/questions.parquet')
