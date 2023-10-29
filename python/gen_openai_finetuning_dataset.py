from prompts import system

in_file_name = 'datasets/luna_training_dataset_v1.51.tsv'
out_file_name = 'datasets/luna_training_dataset_v1.51.jsonl'
system_prompt = system

# this function takes a dataset TSV, and converts it to a dataset jsonl, in a format which can be used to fine-tune gpt-3.5-turbo.
# outfile should be completely blank.
# TSV should have the following format (add question/answer pairs horizontally for same conversation, vertically for new conversation):
# 1 Question  Answer  Question  Answer ... ...
# 2 foo       bar     foo       bar    ... ...

# TSV FILE ASSUMPTIONS (your dataset must follow these rules, otherwise the jsonl output will be scuffed!)
# 1. The file cannot have any double quotes. Use only single quotes.
# 2. No cells can be empty (except for trailing cells).
# 3. Trailing whitespace inside a cell, or at the end of a row, will be stripped.
# 4. Emojis are allowed. They will be encoded as utf8.

def gen_dataset():
  with open(in_file_name, 'r', encoding="utf8") as infile, open(out_file_name, 'w', encoding="utf8") as outfile:
    total_lines = sum(1 for _ in infile)
    infile.seek(0)
    next(infile) # ignore header line
    for line_number, line in enumerate(infile, start=2):
      values = line.strip().split('\t')
      formatted_line_part_1 = f'''{{"messages":[{{"role":"system","content":"{system_prompt}"}}'''
      formatted_line_part_2 = ''
      formatted_line_part_3 = ']}\n' if line_number != total_lines else ']}' # make sure there is no empty line at the end of the file.
      for index, content in enumerate(values):
        role = 'user' if index % 2 == 0 else 'assistant'
        formatted_line_part_2 += f''',{{"role":"{role}","content":"{content.strip()}"}}'''
      outfile.write(formatted_line_part_1 + formatted_line_part_2 + formatted_line_part_3)


if __name__ == '__main__':
  gen_dataset()
