import os, sys, copy, requests, json, random, string
from io import StringIO, BytesIO

from xutil.web import WebApp, process_request
from xutil.helpers import jdumps, jtrans, log, get_error_str, get_script_path, get_dir_path, get_home_path, load_profile, file_exists
from xutil.diskio import read_file, write_file, read_csv
from dbnet.store import store_func
from flask import render_template
import yaml, apprise

DBNET_FOLDER = os.getenv('DBNET_FOLDER', default=get_home_path() + '/dbnet')
CSV_FOLDER = DBNET_FOLDER + '/csv'
AUTH_PATH = DBNET_FOLDER + '/.authorized'
app = WebApp('dbnet', root_path=get_dir_path(__file__))
SID = None
last_perf_data = {}

get_authorized = lambda: read_file(AUTH_PATH).splitlines() if file_exists(AUTH_PATH) else []
add_authorized = lambda new_id: write_file(AUTH_PATH, new_id + '\n', append=True)
app_password = os.getenv('DBNET_PASSWD', default=None)
app_token = ''.join(
    random.SystemRandom().choice(string.ascii_uppercase + string.digits +
                                string.ascii_lowercase) for _ in range(16))
valid_SIDs = set()
cookie_to_sid = {}
sid_to_sid = {}

@app.route('/logo.ico')
def favicon():
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'templates'),
    'logo.ico',
    mimetype='image/vnd.microsoft.icon')


@app.route('/css/<file_name>')
def get_css_file(file_name):
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'static', 'css'), file_name)


@app.route('/js/<file_name>')
def get_js_file(file_name):
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'static', 'js'), file_name)


@app.route('/app.js')
def get_app_js():
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'static'), 'app.js')


@app.route('/img/<file_name>')
def get_img_file(file_name):
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'static', 'img'), file_name)


@app.route('/fonts/<file_name>')
def get_fonts_file(file_name):
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'static', 'fonts'), file_name)


@app.route('/favicon.ico')
def get_favicon():
  return app.send_from_directory(
    os.path.join(app.flask_app.root_path, 'static'), 'favicon.ico')


@app.route('/')
def index():
  """Serve the client-side application."""
  (val_dict, form_dict, data_dict) = app.proc_request()
  session_id = app.get_cookie_session_id()
  in_token = val_dict.get('token', None)
  if in_token and in_token in (app_token, app_password):
    add_authorized(session_id)
    resp = app.make_response(app.redirect(app.url_for('index'))) # remove token from URL
  elif session_id in get_authorized():
    resp = app.make_response(render_template('index.html'))
  else:
    resp = app.make_response(app.redirect(app.url_for('login')))

  resp.set_cookie(app.cookie_session_key, session_id)
  resp.headers['Cache-Control'] = 'no-cache'

  return resp


@app.route('/login', methods=['GET'])
def login():
  (val_dict, form_dict, data_dict) = app.proc_request()
  resp = app.make_response(render_template('login.html'))
  log('+Web-App Token: ' + app_token)
  return resp


@app.route('/csv/<file_name>')
def get_csv_file(file_name):
  """Create virtual CSV file"""
  (val_dict, form_dict, data_dict) = app.proc_request()
  session_id = app.get_cookie_session_id()

  fpath = '{}/{}'.format(CSV_FOLDER, file_name)
  byte_io = BytesIO(read_file(fpath, mode='rb'))
  resp = app.make_response(byte_io.getvalue())
  resp.headers["Content-Disposition"] = "attachment;filename={}".format(
    file_name)
  # resp.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  resp.headers["Content-type"] = "text/csv"

  return resp


@app.route('/api/<payload_type>', methods=['POST'])
def transmit_payload(payload_type):
  (val_dict, form_dict, data_dict) = app.proc_request()
  if data_dict['payload_type'] == 'monitor':
    data_dict['sid'] = data_dict.get('sid', SID)
  elif data_dict['payload_type'] != 'client-response':
    _data_dict = copy.deepcopy(data_dict)
    if 'rows' in data_dict:
      nrows = len(data_dict['rows'])
      ncols = len(data_dict['rows'][0]) if nrows else 0
      _data_dict['rows'] = '{} cols X {} rows'.format(ncols, nrows)
    app.log('-Response -> {}'.format(_data_dict))
  else:
    _data_dict = copy.deepcopy(data_dict)
    if 'data' in _data_dict:
      _data_dict['data'] = '{} chars'.format(len(_data_dict['data']))
    app.log('Confirmation -> {}'.format(_data_dict))
  if data_dict['sid'] in sid_to_sid:
    data_dict['sid'] = sid_to_sid[data_dict['sid']]
  app.emit(payload_type, data_dict, namespace='/', room=data_dict['sid'])
  return 'OK'


@app.on('get-perf')
def get_perf_mon(sid, data):
  """
  Get Monitoring Performance
  """
  global last_perf_data
  data2 = _mon_worker.get_parent_q()
  if not data2:
    data2 = last_perf_data
  else:
    last_perf_data = data2

  return data2

@app.on('apprise')
def apprise_notify(sid, data):
  """
  Send Notification on Apprise
  """
  url = os.getenv("NOTIFY_APPRISE_URL")
  apobj = apprise.Apprise()
  apobj.add(url)
  apobj.notify(
    title=data['title'],
    body=data['body'],
  )
  log(f'''Sent notification: "{data['title']}"''')
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
    resp = requests.get(api_applications, headers=headers, verify=False)
    if not resp.text:
      return data2

    resp1 = json.loads(resp.text)

    app_id = resp1[0]['id']
    api_jobs = '{}/api/v1/applications/{}/jobs'.format(url, app_id)
    resp = requests.get(api_jobs, headers=headers, verify=False)
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
  cookies = app.parse_sio_cookies(sio_environ=environ)
  session_id = cookies.get(app.cookie_session_key, None)
  if session_id in get_authorized():
    valid_SIDs.add(sid)
  else:
    log('~~Session ID {} is not authorized'.format(session_id))

  app.log('connect ' + sid)

  # if client loses connection, this will map the old SID to the new SID
  if session_id in cookie_to_sid:
    sid_to_sid[cookie_to_sid[session_id]] = sid

  cookie_to_sid[session_id] = sid
  SID = sid


@app.on('message')
def message(sid, data):
  app.log('message from "{}" => {}'.format(sid, data))
  # app.pipe.send_to_parent(data)
  return 'OK'


@app.on('store')
def store_request(sid, data, *args, **kwargs):
  """
  Operation on Store. Returns Data as needed
  """
  if sid not in valid_SIDs: return {'error': 'Invalid SID'}

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


@app.on('profile-request')
def profile_request(sid, data, *args, **kwargs):
  if sid not in valid_SIDs: return {'error': 'Invalid SID'}

  data2 = dict(completed=False)
  try:
    if data['type'] == 'load':
      data2['text'] = load_profile(raw_text=True)
      data2['completed'] = True
    elif data['type'] == 'save':
      yaml.load(data['text'])  # validate
      path = os.getenv('PROFILE_YAML')
      write_file(path, data['text'], echo=True)
      data2['completed'] = True
  except Exception as E:
    log(E)
    data2['error'] = get_error_str(E)
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
  if sid not in valid_SIDs: return {'error': 'Invalid SID'}

  data['sid'] = sid
  SID = sid

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
  SID = sid


def run(host, port, worker, mon_worker):
  global _mon_worker
  _mon_worker = mon_worker
  url_suffix = '/?token=' + app_token
  app.run(port, host=host, url_suffix=url_suffix, log=worker.log, worker=worker)