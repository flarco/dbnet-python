'''
This will be the backend instance.
'''
import sys
sys.path.insert(1, '/Users/larco/__/Git/xutil')
import os, time, requests
from xutil.parallelism import Pipe, Queue, Process, Worker
from xutil.helpers import (get_profile, get_databases, log, struct, now, epoch,
                           jdumps, get_db_profile, register_pid, get_home_path,
                           get_pid_path, cleanup_pid)
import xutil.database.base as xutil_db
import worker_web as webapp_worker
import worker_db as db_worker
import store

WORKER_PREFIX = os.getenv('DBNET_WORKER_PREFIX', default='dbnet')
WEBAPP_PORT = int(os.getenv('DBNET_WEBAPP_PORT', default=5566))
DBNET_FOLDER = os.getenv('DBNET_FOLDER', default=get_home_path() + '/dbnet')

os.makedirs(DBNET_FOLDER, exist_ok=True)

workers = {}
db_workers_map = {}


def start_worker_webapp():
  worker_name = '{}-webapp'.format(WORKER_PREFIX)
  worker = Worker(
    worker_name,
    fn=webapp_worker.run,
    log=log,
    args=(WEBAPP_PORT, ),
    pid_folder=DBNET_FOLDER)
  worker.start()
  workers['webapp'] = worker
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
    fn=db_worker.run,
    log=log,
    args=(db_prof, ),
    kwargs={},
    pid_folder=DBNET_FOLDER)
  worker.status = 'IDLE'

  if start:
    worker.start()
    log('*Started worker {} with PID {}'.format(worker.name, worker.pid))

  workers[worker_name] = worker
  db_workers_map[db_name].append(worker)

  return worker


def send_to_webapp(data, host='localhost', port=WEBAPP_PORT):
  "Send data to Web App"
  resp_type = data['resp_type']
  headers = {'Content-type': 'application/json'}
  url = 'http://{}:{}/api/{}'.format(host, port, resp_type)
  requests.post(url, data=jdumps(data), headers=headers)


def handle_worker_data(worker, data_dict):
  data = struct(data_dict)
  if data_dict.get('queue_length', 0) == 0:
    workers[data.worker_name].status = 'IDLE'

  send_to_webapp(data_dict)


def handle_web_data(worker, data_dict):
  data = struct(data_dict)
  confirm_data = {'completed': False}

  if data.req_type in ('exec-sql'):
    if data.database not in db_workers_map:
      db_worker = start_worker_db(data.database, start=True)

    # matched & available workers
    db_workers_matched = db_workers_map[data.database]
    db_workers_avail = [w for w in db_workers_matched if w.status == 'IDLE']
    if not db_workers_avail:
      db_workers_avail = db_workers_matched[0]

    db_worker = db_workers_avail[0]

    # send to worker queue
    workers[db_worker.name].status = 'BUSY'
    confirm_data = db_worker.pipe.emit_to_child(data_dict)

  elif data.req_type == 'stop-worker':
    if data.worker_name in workers:
      worker = workers[data.worker_name]
      worker.stop()
      db_workers_map[data.database].remove(worker)
      del workers[data.worker_name]
      confirm_data = dict(orig_req=data_dict, completed=True)

  worker.pipe.send_to_child(confirm_data)


def main():
  log('Main Loop PID is {}'.format(os.getpid()))
  register_pid(get_pid_path('dbnet', DBNET_FOLDER))
  exiting = False
  profile = get_profile()
  databases = get_databases(profile)

  # start web worker
  start_worker_webapp()

  while not exiting:
    try:
      # Main loop

      time.sleep(0.005)  # brings down CPU loop usage
      for wkr_key in list(workers):
        worker = workers[wkr_key]
        recv_data = worker.pipe.recv_from_child(timeout=0)

        if recv_data:
          if wkr_key == 'webapp':
            handle_web_data(worker, recv_data)
          else:
            handle_worker_data(worker, recv_data)

    except (KeyboardInterrupt, SystemExit):
      # Exit cleanly

      exiting = True
      log('-Exiting')

      for worker in workers.values():
        worker.stop()


if __name__ == '__main__':
  store.create_tables()
  # main()
