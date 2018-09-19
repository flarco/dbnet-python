import os, sys, copy, requests, json

from xutil.web import WebApp, process_request
from xutil.helpers import jdumps, jtrans, log, get_error_str, get_script_path, get_dir_path
from dbnet.store import store_func
from flask import render_template

app = WebApp('dbnet', root_path=get_dir_path(__file__))


@app.route('/logo.ico')
def favicon():
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'templates'),
    'logo.ico',
    mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
  """Serve the client-side application."""
  (val_dict, form_dict, data_dict) = app.proc_request()
  session_id = app.get_cookie_session_id()

  resp = app.make_response(render_template('index.html'))
  resp.set_cookie(app.cookie_session_key, session_id)
  resp.headers['Cache-Control'] = 'no-cache'

  return resp


@app.route('/csv/<name>')
def get_csv(name):
  """Serve the client-side application."""
  (val_dict, form_dict, data_dict) = app.proc_request()
  session_id = app.get_cookie_session_id()

  resp = app.make_response(render_template('index.html'))
  resp.set_cookie(app.cookie_session_key, session_id)
  resp.headers['Cache-Control'] = 'no-cache'

  return resp


@app.route('/api/<payload_type>', methods=['POST'])
def transmit_payload(payload_type):
  (val_dict, form_dict, data_dict) = app.proc_request()
  if data_dict['payload_type'] != 'client-response':
    _data_dict = copy.deepcopy(data_dict)
    if 'rows' in data_dict:
      nrows = len(data_dict['rows'])
      ncols = len(data_dict['rows'][0]) if nrows else 0
      _data_dict['rows'] = '{} cols X {} rows'.format(ncols, nrows)
    app.log('-Response -> {}'.format(_data_dict))
  else:
    app.log('Confirmation -> {}'.format(data_dict))
  app.emit(payload_type, data_dict, namespace='/', room=data_dict['sid'])
  return 'OK'


@app.on('spark-progress')
def spark_progess(sid, data):
  """
  Get Spark-Progress
  """

  data2 = dict(query_progress_prct=None)

  try:
    data['sid'] = sid
    url = data['url']
    api_applications = '{}/api/v1/applications'.format(url)
    headers = {'Content-type': 'application/json'}
    resp = requests.get(api_applications, headers=headers)
    resp1 = json.loads(resp.text)

    app_id = resp1[0]['id']
    api_jobs = '{}/api/v1/applications/{}/jobs'.format(url, app_id)
    resp = requests.get(api_jobs, headers=headers)
    resp2 = json.loads(resp.text)
    if resp2:
      job = resp2[0]
      data2['query_progress_prct'] = int(
        100.0 * job['numCompletedTasks'] / job['numTasks'])
  except Exception as E:
    app.log(data)
    app.log(E)

  return data2


@app.on('connect')
def connect(sid, environ):
  app.log('connect ' + sid)


@app.on('message')
def message(sid, data):
  app.log('message from "{}" => {}'.format(sid, data))
  # app.pipe.send_to_parent(data)
  return 'OK'


@app.on('store')
def client_request(sid, data, *args, **kwargs):
  """
  Operation on Store. Returns Data as needed
  """
  data['sid'] = sid
  _data = copy.deepcopy(data)
  if _data['store_func'] == 'set_dbquery_state':
    _data['kwargs'] = '{} bytes'.format(len(jdumps(_data['kwargs'])))
  app.log('+Got Store Req => {}'.format(_data))
  try:
    data2 = dict(
      payload=store_func[data['store_func']](**data['kwargs']),
      completed=True,
    )
  except Exception as err:
    app.log(err)
    data2 = dict(
      payload={},
      completed=False,
      error=get_error_str(err),
      orig_req=data,
    )
  _data2 = copy.deepcopy(data2)
  _data2['payload'] = '{} bytes'.format(len(jdumps(_data2['payload'])))
  app.log('-Resp Data => {}'.format(_data2))
  return data2


@app.on('client-request')
def client_request(sid, data, *args, **kwargs):
  """
  General Action requested by client
  data should have key 'req_type' with values such as:
   * submit-sql
   * stop-worker
   * get-workers
  """
  data['sid'] = sid

  # with app.worker.lock:
  #   resp_data = app.pipe.emit_to_parent(data)
  # app.pipe.send_to_parent(data)
  # print('resp_data: {}'.format(resp_data))
  # return jtrans(resp_data)

  app.worker.put_parent_q(data)
  return 'OK'


@app.on('disconnect')
def disconnect(sid):
  app.log('disconnect ' + sid)


def run(port, worker):
  app.run(port, log=worker.log, worker=worker)