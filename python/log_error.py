def log_error(ex, source):
  template = '😡 an exception of type {0} occurred! Arguments:\n{1!r}'
  message = template.format(type(ex).__name__, ex.args)
  print(f'[ERROR] {source} {message}')
