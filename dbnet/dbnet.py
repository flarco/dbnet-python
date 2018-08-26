'''
This will be the backend instance.
'''
import sys
sys.path.insert(1, '/Users/larco/__/Git/xutil')
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
import xutil.database.base as xutil_db
import worker_web as webapp_worker
import worker_db as db_worker
from collections import OrderedDict
import store

WORKER_PREFIX = os.getenv('DBNET_WORKER_PREFIX', default='dbnet')
WEBAPP_PORT = int(os.getenv('DBNET_WEBAPP_PORT', default=5566))
DBNET_FOLDER = os.getenv('DBNET_FOLDER', default=get_home_path() + '/dbnet')

os.makedirs(DBNET_FOLDER, exist_ok=True)

hostname = socket.gethostname()
workers = OrderedDict()
db_workers_map = OrderedDict()


def start_worker_webapp():
  worker_name = '{}-webapp'.format(WORKER_PREFIX)
  worker = Worker(
    worker_name,
    'web-app',
    fn=webapp_worker.run,
    log=log,
    args=(WEBAPP_PORT, ),
    pid_folder=DBNET_FOLDER)
  worker.start()
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


def start_worker_db(db_name, start=False):
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
    args=(db_prof, ),
    kwargs={},
    pid_folder=DBNET_FOLDER)
  worker.status = 'IDLE'

  if start:
    worker.start()
    log('*Started worker {} with PID {}'.format(worker.name, worker.pid))

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


def send_to_webapp(data, host='localhost', port=WEBAPP_PORT):
  "Send data to Web App"
  payload_type = data['payload_type']
  headers = {'Content-type': 'application/json'}
  url = 'http://{}:{}/api/{}'.format(host, port, payload_type)
  requests.post(url, data=jdumps(data), headers=headers)


def handle_worker_req(worker: Worker, data_dict):
  log('Received unhandled worker ({}) data: {}'.format(worker.name, data_dict))


def handle_db_worker_req(worker: Worker, data_dict):
  data = struct(data_dict)
  if data.payload_type in ('task-error'):
    send_to_webapp(data_dict)
  elif data.payload_type in ('query-data'):
    send_to_webapp(data_dict)


def handle_web_worker_req(worker: Worker, data_dict):
  # print('data_dict: {}'.format(data_dict))
  data = struct(data_dict)
  confirm_data = {}
  confirm_data_for_missing = {
    'completed': False,
    'error': Exception('Request "{}" not handled!'.format(data.req_type))
  }

  if data.req_type in ('submit-sql'):
    if data.database not in db_workers_map:
      db_worker = start_worker_db(data.database, start=True)

    # matched & available workers
    db_workers_matched = []
    db_workers_avail = []

    for wkr in db_workers_map[data.database]:
      wkr_rec = store.worker_get(hostname, wkr.name)
      db_workers_matched.append(wkr.name)
      if wkr_rec.status == 'IDLE':
        db_workers_avail.append(wkr.name)

    # just pick the first? need to add ability to specify in front-end
    if not db_workers_avail:
      db_workers_avail = [sorted(db_workers_matched)[0]]

    db_worker = workers[db_workers_avail[0]]

    # send to worker queue
    confirm_data = db_worker.pipe.emit_to_child(data_dict)

  elif data.req_type == 'stop-worker':
    if data.worker_name in workers:
      worker_ = workers[data.worker_name]
      worker_.stop()
      for db in list(db_workers_map):
        for w in list(db_workers_map[db]):
          if w == worker_:
            db_workers_map[db].remove(worker_)
        if len(db_workers_map[db]) == 0:
          del db_workers_map[db]
      del workers[data.worker_name]
      confirm_data = dict(completed=True)

  elif data.req_type == 'get-workers':
    make_rec = lambda wkr: dict(
      name=wkr.name,
      status=wkr.status,
      start_time=wkr.started,
      pid=wkr.pid,
    )
    workers_data = [make_rec(wkr) for wkr in workers.values()]
    confirm_data = dict(data=workers_data, completed=True)

  # In case handle is missing. Also checked for completed
  if confirm_data:
    confirm_data['orig_req'] = data_dict
    confirm_data['completed'] = confirm_data.get('completed', False)
    res = '+Completed' if confirm_data['completed'] else '~Did not Complete'
    log('{} "{}" request "{}".'.format(res, data.req_type, data.id))
  else:
    confirm_data = confirm_data_for_missing

  # Confirm receipt to WebApp Worker
  # log('confirm_data: {}'.format(confirm_data))
  worker.pipe.send_to_child(confirm_data)


def main():
  log('Main Loop PID is {}'.format(os.getpid()))
  register_pid(get_pid_path('dbnet', DBNET_FOLDER))
  exiting = False
  profile = get_profile()
  databases = get_databases(profile)

  # start web worker
  start_worker_webapp()
  start_worker_db('PG_XENIAL', start=True)

  while not exiting:
    try:
      # Main loop

      time.sleep(0.005)  # brings down CPU loop usage
      for wkr_key in list(workers):
        worker = workers.get(wkr_key, None)
        if not worker: continue

        recv_data = worker.pipe.recv_from_child(timeout=0)

        if recv_data:
          if wkr_key == 'webapp':
            handle_web_worker_req(worker, recv_data)
          elif worker.type == 'database-client':
            handle_db_worker_req(worker, recv_data)
          else:
            handle_worker_req(worker, recv_data)

    except (KeyboardInterrupt, SystemExit):
      # Exit cleanly

      exiting = True
      log('-Exiting')

      for worker in workers.values():
        worker.stop()


if __name__ == '__main__':
  store.create_tables(drop_first=True)
  main()
