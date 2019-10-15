'''
This will be the backend instance.
'''
import sys
import os, time, requests, socket
from xutil.parallelism import Pipe, Queue, Process, Worker
from xutil.helpers import (
  get_profile,
  get_databases,
  log,
  struct,
  now,
  epoch,
  jdumps,
  get_db_profile,
  register_pid,
  get_home_path,
  get_pid_path,
  cleanup_pid,
)
from xutil.database.base import fwa
from xutil.parallelism import Queue
import dbnet.worker_web as webapp_worker
import dbnet.worker_db as db_worker
import dbnet.worker_mon as mon_worker
from collections import OrderedDict
import dbnet.store as store

WORKER_PREFIX = os.getenv('DBNET_WORKER_PREFIX', default='dbnet')
WEBAPP_HOST = os.getenv('DBNET_WEBAPP_HOST', default='0.0.0.0')
WEBAPP_PORT = int(os.getenv('DBNET_WEBAPP_PORT', default=5566))
DBNET_FOLDER = os.getenv('DBNET_FOLDER', default=get_home_path() + '/dbnet')

os.makedirs(DBNET_FOLDER, exist_ok=True)

hostname = socket.gethostname()
workers = OrderedDict()
db_workers_map = OrderedDict()
conf_queue = Queue()
exit_queue = Queue()
profile = get_profile(create_if_missing=True, def_profl_path=f'{DBNET_FOLDER}/profile.yaml')
databases = get_databases(profile)
print(f'profile `{os.getenv("PROFILE_YAML")}` databases -> {list(databases)}')


def start_worker_webapp():
  """Starts the WebApp worker"""
  worker_name = '{}-webapp'.format(WORKER_PREFIX)

  worker = Worker(
    worker_name,
    'web-app',
    fn=webapp_worker.run,
    log=log,
    kill_if_running=True,
    args=(WEBAPP_HOST, WEBAPP_PORT),
    kwargs={'mon_worker': workers['mon']},
    pid_folder=DBNET_FOLDER)
  worker.start()
  workers['mon'].put_child_q(dict(name=worker_name,
                                  pid=worker.pid))  # add to monitor
  workers['webapp'] = worker
  store.sqlx('workers').replace_rec(
    hostname=worker.hostname,
    worker_name=worker.name,
    worker_type=worker.type,
    worker_pid=worker.pid,
    status='RUNNING',
    task_id=-1,
    task_function=worker.fn.__name__,
    task_start_date=now(),
    task_args=jdumps(worker.args),
    task_kwargs=jdumps(worker.kwargs),
    progress=None,
    queue_length=0,
    last_updated=epoch(),
  )
  return worker


def start_worker_mon():
  """Starts the Monitoring worker"""
  worker_name = '{}-mon'.format(WORKER_PREFIX)
  worker = Worker(
    worker_name,
    'monitor',
    fn=mon_worker.run,
    kwargs={},
    log=log,
    kill_if_running=True,
    pid_folder=DBNET_FOLDER)

  worker.start()
  log('Monitor Loop PID is {}'.format(worker.pid))

  workers['mon'] = worker
  workers['mon'].put_child_q(dict(name=worker_name,
                                  pid=worker.pid))  # add to monitor
  store.sqlx('workers').replace_rec(
    hostname=worker.hostname,
    worker_name=worker.name,
    worker_type=worker.type,
    worker_pid=worker.pid,
    status='RUNNING',
    task_id=-1,
    task_function=worker.fn.__name__,
    task_start_date=now(),
    task_args=jdumps(worker.args),
    task_kwargs=jdumps(worker.kwargs),
    progress=None,
    queue_length=0,
    last_updated=epoch(),
  )
  return worker


def start_worker_db(db_name, start=False):
  """Create and start a dabatase worker
  
  Args:
    db_name: the name of the database
    start: Whether to automatically start the worker or not
  
  Returns:
    The worker object.
  """
  db_prof = get_db_profile(db_name)
  db_workers_map[db_name] = db_workers_map.get(db_name, [])

  # multiple workers for same database
  index = 0
  worker_name = '{}-{}-{}'.format(WORKER_PREFIX, db_name, index)

  while worker_name in workers:
    # in case worker name is already in
    index += 1
    worker_name = '{}-{}-{}'.format(WORKER_PREFIX, db_name, index)

  worker = Worker(
    worker_name,
    'database-client',
    fn=db_worker.run,
    log=log,
    kill_if_running=True,
    args=(db_prof, conf_queue),
    kwargs={},
    pid_folder=DBNET_FOLDER)
  worker.status = 'IDLE'

  if start:
    worker.start()
    log('*Started worker {} with PID {}'.format(worker.name, worker.pid))

  workers['mon'].put_child_q(dict(name=worker_name,
                                  pid=worker.pid))  # add to monitor
  store.sqlx('workers').replace_rec(
    hostname=worker.hostname,
    worker_name=worker.name,
    worker_type=worker.type,
    worker_pid=worker.pid,
    queue_length=0,
    status='IDLE',
    last_updated=epoch(),
  )

  workers[worker_name] = worker
  db_workers_map[db_name].append(worker)

  return worker


def get_avail_worker(database):
  """Get the available / running worker for the specified database.

  Args:
    database: the name of the database
  
  Returns:
    the matched database worker
  """
  if database not in db_workers_map:
    db_worker = start_worker_db(database, start=True)

  # matched & available workers
  db_workers_matched = []
  db_workers_avail = []

  for wkr in db_workers_map[database]:
    wkr_rec = store.worker_get(hostname, wkr.name)
    db_workers_matched.append(wkr.name)
    if wkr_rec.status == 'IDLE':
      db_workers_avail.append(wkr.name)

  # just pick the first? need to add ability to specify in front-end
  if not db_workers_avail:
    db_workers_avail = [sorted(db_workers_matched)[0]]

  db_worker = workers[db_workers_avail[0]]

  return db_worker


def stop_worker(worker_name):
  """Stop / Kill the specified worker.
  
  Args:
    worker_name: the name of the worker to be stopped.
  """
  if worker_name in workers:
    worker_ = workers[worker_name]
    worker_.stop()
    for db in list(db_workers_map):
      for w in list(db_workers_map[db]):
        if w == worker_:
          db_workers_map[db].remove(worker_)
      if len(db_workers_map[db]) == 0:
        del db_workers_map[db]
    del workers[worker_name]
  log('+Worker "{}" stopped.'.format(worker_name))
  return True


def send_to_webapp(data, host='localhost', port=WEBAPP_PORT):
  """Send data to Web App
  
  Args:
    data: the payload data
    host: the webapp host (default to localhost)
    port: the port of the webapp  
  """
  payload_type = data['payload_type']
  headers = {'Content-type': 'application/json'}
  scheme = 'https' if os.getenv('SECURE_SSL_REDIRECT', default=False) else 'http'
  url = '{}://{}:{}/api/{}'.format(scheme, host, port, payload_type)
  requests.post(url, data=jdumps(data), headers=headers, verify=False)


def handle_worker_req(worker: Worker, data_dict):
  """A function for a unhandled worker request.
  
  Args:
    worker: the respective worker
    data_dict: the request payload dictionary
  """
  log('Received unhandled worker ({}) data: {}'.format(worker.name, data_dict))


def handle_db_worker_req(worker: Worker, data_dict):
  """Handler for for a database worker request.
  
  Args:
    worker: the respective worker
    data_dict: the request payload dictionary
  """
  data = struct(data_dict)
  if worker.type == 'monitor':
    send_to_webapp(data_dict)
  elif data.payload_type in ('task-error'):
    send_to_webapp(data_dict)
  elif data.payload_type in ('query-data'):
    send_to_webapp(data_dict)
  elif data.payload_type in ('meta-updated'):
    send_to_webapp(data_dict)
  else:
    send_to_webapp(data_dict)


def handle_web_worker_req(web_worker: Worker, data_dict):
  """Handler for a web worker request
  
  Args:
    worker: the respective worker
    data_dict: the request payload dictionary
  """
  # print('data_dict: {}'.format(data_dict))
  # return
  data = struct(data_dict)
  response_data = {}
  response_data_for_missing = {
    'completed': False,
    'payload_type': 'client-response',
    'sid': data.sid,
    'error': Exception('Request "{}" not handled!'.format(data.req_type))
  }

  if data.req_type in ('submit-sql'):
    db_worker = get_avail_worker(data.database)

    # send to worker queue
    db_worker.put_child_q(data_dict)
    response_data['worker_name'] = db_worker.name
    response_data['queued'] = True

  elif data.req_type == 'stop-worker':
    completed = stop_worker(data.worker_name)
    response_data = dict(completed=completed)

  elif data.req_type == 'add-worker':
    start_worker_db(data.database, start=True)
    response_data = dict(completed=True)

  elif data.req_type == 'set-state':
    store.state_set(data.key, data.value)
    response_data = dict(completed=True)

  elif data.req_type == 'set-database':
    store.sqlx('databases').replace_rec(**data.db_states)
    response_data = dict(completed=True)

  elif data.req_type == 'get-database':
    rec = store.sqlx('databases').select_one(fwa(db_name=data.db_name))
    response_data = dict(completed=True, data=rec._asdict())

  elif data.req_type == 'get-databases':
    databases = get_databases()
    get_rec = lambda d: dict(type=d['type'])
    response_data = dict(
      completed=True,
      data={
        k: get_rec(databases[k])
        for k in sorted(databases) if k.lower() not in ('tests', 'drivers')
      })

  elif data.req_type == 'get-analysis-sql':
    db_worker = get_avail_worker(data.database)
    db_worker.put_child_q(data_dict)
    response_data['queued'] = True

  elif data.req_type == 'get-meta-tables':
    where = "lower(db_name)=lower('{}')".format(data.database)
    if data.filter_schema:
      where = where + ''' and lower(schema_name) like lower('%{}%')'''.format(
        data.filter_schema)
    if data.filter_table:
      where = where + ''' and lower(table_name) like lower('%{}%')'''.format(
        data.filter_table)
    rows = store.sqlx('meta_tables').query(where, limit=data.limit)
    if rows:
      headers = store.sqlx('meta_tables').ntRec._fields
      rows = [list(r) for r in rows]
      response_data = dict(completed=True, headers=headers, rows=rows)
    else:
      db_worker = get_avail_worker(data.database)
      db_worker.put_child_q(data_dict)
      response_data['queued'] = True

  elif data.req_type == 'get-meta-columns':
    log(str(data))
    where = "lower(db_name)=lower('{}')".format(data.database)
    if data.filter_schema:
      where = where + ''' and lower(schema_name) like lower('%{}%')'''.format(
        data.filter_schema)
    if data.filter_table:
      where = where + ''' and lower(table_name) like lower('%{}%')'''.format(
        data.filter_table)
    if data.filter_column:
      where = where + ''' and lower(column_name) like lower('%{}%')'''.format(
        data.filter_column)
    rows = store.sqlx('meta_columns').query(where, limit=data.limit)
    if rows:
      headers = store.sqlx('meta_columns').ntRec._fields
      rows = [list(r) for r in rows]
      response_data = dict(completed=True, headers=headers, rows=rows)
    else:
      db_worker = get_avail_worker(data.database)
      db_worker.put_child_q(data_dict)
      response_data['queued'] = True

  elif data.req_type == 'set-tab':
    store.sqlx('tabs').replace_rec(**data.tab_state)
    response_data = dict(completed=True)

  elif data.req_type == 'get-tab':
    rec = store.sqlx('tabs').select_one(
      fwa(db_name=data.db_name, tab_name=data.tab_name))
    response_data = dict(completed=True, data=rec._asdict())

  elif data.req_type == 'get-tasks':
    rows = store.sqlx('tasks').query(
      where='1=1 order by end_date desc, start_date desc, queue_date desc',
      limit=100)
    recs = [row._asdict() for row in rows]
    response_data = dict(data=recs, completed=True)

  elif data.req_type == 'get-queries':
    rows = store.sqlx('queries').query(
      where="""
        lower(sql_text) like '%{}%'
        and database = '{}'
        and sql_text <> ''
        order by exec_date desc
      """.format(data.filter.lower(), data.database),
      limit=int(data.limit))
    recs = [row._asdict() for row in rows]
    response_data = dict(data=recs, completed=True)

  elif data.req_type == 'search-queries':
    where = "sql_text like '%{}%' order by exec_date desc".format(
      data.query_filter)
    rows = store.sqlx('queries').query(where=where, limit=100)
    recs = [row._asdict() for row in rows]
    response_data = dict(data=recs, completed=True)

  elif data.req_type == 'get-workers':
    make_rec = lambda wkr: dict(
      name=wkr.name,
      status=wkr.status,
      start_time=wkr.started,
      pid=wkr.pid,
    )
    workers_data = [make_rec(wkr) for wkr in workers.values()]
    response_data = dict(data=workers_data, completed=True)
  elif data.req_type == 'reset-db':
    for wkr_nm in list(workers):
      if wkr_nm in ('webapp', 'mon'): continue
      stop_worker(wkr_nm)
    store.create_tables(drop_first=True, ask=False)
    response_data = dict(completed=True)

  # In case handle is missing. Also checked for completed
  if response_data:
    response_data['orig_req'] = data_dict
    response_data['payload_type'] = 'client-response'
    response_data['sid'] = data.sid
    response_data['completed'] = response_data.get('completed', False)
    res = '+Completed' if response_data[
      'completed'] else '+Queued' if 'queued' in response_data and response_data['queued'] else '~Did not Complete'
    log('{} "{}" request "{}".'.format(res, data.req_type, data.id))
  else:
    response_data = response_data_for_missing

  # Respond to WebApp Worker
  send_to_webapp(response_data)


def main(kill_existing=False):
  """The main function
  
  Args:
    kill_existing: whether to kill an existing instance.
  """
  log('Main Loop PID is {}'.format(os.getpid()))
  register_pid(
    get_pid_path('dbnet', DBNET_FOLDER),
    exit_queue=exit_queue,
    kill_if_running=kill_existing)
  exiting = False
  start_worker_mon()
  workers['mon'].put_child_q(dict(name='main', pid=os.getpid()))

  # start web worker
  start_worker_webapp()

  while not exiting:
    try:
      # Main loop

      time.sleep(0.005)  # brings down CPU loop usage
      for wkr_key in list(workers):
        worker = workers.get(wkr_key, None)
        if not worker: continue
        if wkr_key == 'mon': continue

        recv_data = worker.get_parent_q()

        if recv_data:
          if wkr_key == 'webapp':
            handle_web_worker_req(worker, recv_data)
          elif wkr_key == 'mon':
            handle_db_worker_req(worker, recv_data)
          elif worker.type == 'database-client':
            handle_db_worker_req(worker, recv_data)
          else:
            handle_worker_req(worker, recv_data)

      if not exit_queue.empty():
        log('-Received Exit SIG')
        exiting = True

    except (KeyboardInterrupt, SystemExit):
      # Exit cleanly
      exiting = True

    except Exception as E:
      log(E)

  log('-Exiting')
  for worker in workers.values():
    worker.stop()


if __name__ == '__main__':
  store.create_tables(drop_first=False)
  main()
