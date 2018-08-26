import sys
sys.path.insert(1, '/Users/larco/__/Git/xutil')

from xutil.web import WebApp
from xutil.web import process_request
from xutil.helpers import jdumps, jtrans

app = WebApp('dbnet')


@app.route('/')
def index():
  """Serve the client-side application."""
  (val_dict, form_dict, data_dict) = app.proc_request()
  app.log('Requested "/"')
  app.log('val_dict = {}'.format(val_dict))
  app.log('form_dict = {}'.format(form_dict))
  app.log('data_dict = {}'.format(data_dict))
  # resp_data = app.pipe.emit_to_parent(val_dict)
  return 'Hi!'


@app.route('/api/<payload_type>', methods=['POST'])
def transmit_payload(payload_type):
  (val_dict, form_dict, data_dict) = app.proc_request()
  app.emit(payload_type, data_dict, namespace='/', room=data_dict['sid'])
  return 'OK'


@app.on('connect')
def connect(sid, environ):
  app.log('connect ' + sid)


@app.on('message')
def message(sid, data):
  app.log('message ' + str(data))
  # app.pipe.send_to_parent(data)


@app.on('client-request')
def client_request(sid, data, *args, **kwargs):
  """
  General Action requested by client
  data should have key 'req_type' with values such as:
   * submit-sql
   * stop-worker
   * get-workers
  """
  # print('args: {}'.format(args))
  # print('kwargs: {}'.format(kwargs))
  data['sid'] = sid
  resp_data = app.pipe.emit_to_parent(data)
  return jtrans(resp_data)


@app.on('disconnect')
def disconnect(sid):
  app.log('disconnect ' + sid)


def run(port, worker):
  app.run(port, log=worker.log, pipe=worker.pipe)