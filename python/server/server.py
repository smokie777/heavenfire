from flask import Flask, request
from log_error import log_error

app = Flask(__name__)

@app.route('/receive_prompt', methods=['POST'])
def _receive_prompt():
  data = request.get_json()
  prompt = data['filename']

  try:
    True
  except Exception as e:
    log_error(e, '/receive_prompt')

  return {}


if __name__ == '__main__':
  app.run(debug=False)
