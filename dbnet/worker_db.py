from xutil.parallelism import Worker
from xutil.helpers import log, struct, now, epoch, jdumps, get_db_profile
from collections import deque
import time


def submit_sql():
  pass


def run(db_prof, worker: Worker):
  pipe = worker.pipe
  log = worker.log
  queue = deque([])

  while True:
    time.sleep(0.005)  # brings down CPU loop usage
    data_dict = pipe.recv_from_parent(timeout=0)
    if data_dict:
      log('+Received: {}'.format(data_dict))
      queue.append(data_dict)
      conf_data = dict(id=epoch(), queued=True, orig_req=data_dict)
      pipe.send_to_parent(conf_data)

    if len(queue):
      data_dict = queue.popleft()
      if data_dict['req_type'] in ('exec-sql'):
        submit_sql(data_dict)
