import sys
sys.path.insert(1, '/Users/larco/__/Git/xutil')

from xutil.web import WebApp
from xutil.web import process_request

app = WebApp('dbnet')


@app.route('/')
def index():
  """Serve the client-side application."""
  (val_dict, form_dict, data_dict) = app.proc_request()
  app.log('Requested "/"')
  app.log('val_dict = {}'.format(val_dict))
  app.log('form_dict = {}'.format(form_dict))
  app.log('data_dict = {}'.format(data_dict))
  resp_data = {}
  resp_data = app.pipe.emit_to_parent(val_dict)
  return 'Hi! {}'.format(resp_data)


@app.on('connect')
def connect(sid, environ):
  app.log('connect ' + sid)
  app.pipe.send_to_parent(sid)


@app.on('message')
def message(sid, data):
  app.log('message ' + str(data))
  app.pipe.send_to_parent(data)


@app.on('disconnect')
def disconnect(sid):
  app.log('disconnect ' + sid)


def run(port, worker):
  app.run(port, log=worker.log, pipe=worker.pipe)