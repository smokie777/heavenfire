import os
import openai
from dotenv import load_dotenv; load_dotenv()

dataset_filename = '../datasets/luna_training_dataset_v1.51.jsonl'

openai.api_key = os.environ['OPENAI_KEY']

# STEP 1 - UPLOAD FILE
# res = openai.File.create(
#   file=open(dataset_filename, encoding='utf8'),
#   purpose='fine-tune'
# )
# print(res)


# STEP 2 - CHECK FILE STATUS
# res = openai.File.retrieve("file-rnBBNJgvcfae3EupiWSZXu23")
# print(res)


# STEP 3 - INITIATE FINE TUNING JOB
# res = openai.FineTuningJob.create(
#   training_file="file-rnBBNJgvcfae3EupiWSZXu23",
#   model="gpt-3.5-turbo"
# )
# print(res)
# print(res["id"])


# STEP FOUR - GET THE FINISHED MODEL
# res = openai.FineTuningJob.retrieve("ftjob-zNv5brsaWgGRUFcWWEZDOVrK")
# print(res)
