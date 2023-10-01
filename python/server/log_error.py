def log_error(ex, route):
  template = 'an exception of type {0} occurred. Arguments:\n{1!r}'
  message = template.format(type(ex).__name__, ex.args)
  print(route + ': ' + message)
  