from xutil.parallelism import Worker, Queue
from xutil.diskio import write_csv, write_file
from xutil.helpers import (
  log,
  struct,
  now,
  now_minus,
  epoch,
  jdumps,
  get_db_profile,
  load_profile,
  get_exception_message,
  get_error_str,
  get_home_path,
  now_str,
)
from xutil import get_conn
from xutil.database.base import fwa, fwo
from xutil.web import send_email_exchange, send_from_outlook, send_from_gmail
from collections import deque
import time, socket
import os, hashlib
import dbnet.store as store

worker_db_prof = {}
worker_hostname = socket.gethostname()
worker_name = None
worker_status = 'IDLE'
worker_queue = deque([])
worker_pid = os.getpid()
worker_sql_cache = {}
load_profile(create_if_missing=True)  # load profile environments

WEBAPP_PORT = int(os.getenv('DBNET_WEBAPP_PORT', default=5566))
DBNET_FOLDER = os.getenv('DBNET_FOLDER', default=get_home_path() + '/dbnet')
SQL_FOLDER = DBNET_FOLDER + '/sql'
os.makedirs(SQL_FOLDER, exist_ok=True)
CSV_FOLDER = DBNET_FOLDER + '/csv'
os.makedirs(CSV_FOLDER, exist_ok=True)

sync_queue = lambda: store.worker_set(
  hostname=worker_hostname, worker_name=worker_name,
  queue_length=len(worker_queue))

set_worker_idle = lambda: store.sqlx('workers').update_rec(
    hostname=worker_hostname,
    worker_name=worker_name,
    status='IDLE',
    task_id=None,
    task_function=None,
    task_start_date=None,
    task_args=None,
    task_kwargs=None,
    last_updated=epoch()
)


def execute_sql(worker: Worker, data_dict):
  "Execute SQL operation"
  log = worker.log

  database = data_dict['database']
  sid = data_dict['sid']
  pid = worker_pid

  conn = get_conn(database)
  if conn.type.lower() == 'spark':
    worker.put_parent_q(
      dict(
        payload_type='spark-url',
        database=database,
        url=conn.sparko.uiWebUrl,
        sid=data_dict['sid'],
      ))

  def start_sql(sql, id, limit, options, sid):
    rows = fields = []
    get_fields = lambda r: r.__fields__ if hasattr(r, '__fields__') else r._fields
    s_t = epoch()
    cache_used = False
    limit = int(options['limit']) if 'limit' in options else limit

    try:

      def exec_sql(sql, limit_def=5000):
        log(
          '\n------------SQL-START------------\n{}\n------------SQL-END------------ \n'.
          format(sql),
          color='blue')
        log('LIMIT: ' + str(limit), color='blue')
        cache_used = False
        if sql in worker_sql_cache:
          for fields, rows in list(worker_sql_cache[sql]['results']):
            # if limit above limit_def, then refresh
            if limit > limit_def: break

            # if limit is same and not a csv call, then refresh
            if limit == worker_sql_cache[sql]['limit'] and 'csv' not in options:
              break

            # if ran more than 10 minutes ago, then refresh
            if now_minus(minutes=10) > worker_sql_cache[sql]['timestamp']:
              del worker_sql_cache[sql]
              break

            if len(fields) > 0:
              cache_used = True  # must return data/fields
              worker_sql_cache[sql]['limit'] = limit
              log('+Cache Used')

            yield fields, rows, cache_used

        if not cache_used:
          worker_sql_cache[sql] = dict(
            timestamp=now(), results=[], limit=limit)
          rows = conn.query(
            sql.replace('%', '%%'),
            dtype='tuple',
            limit=limit if limit > limit_def else limit_def)
          fields = conn._fields
          worker_sql_cache[sql]['results'].append((fields, rows))
          yield fields, rows, cache_used

      if 'meta' in options:
        # get_schemas or
        meta_func = options['meta']
        rows = getattr(conn, meta_func)(**options['kwargs'])
        rows = [tuple(r) for r in rows]
        fields = conn._fields

      elif 'special' in options:
        pass

      else:
        for fields, rows, cache_used in exec_sql(sql):
          fields, rows = fields, rows
          rows = rows[:limit] if len(rows) > limit else rows

      if rows == None: rows = []

      if 'email_address' in options or 'csv' in options:
        file_name = '{}-{}-{}.csv'.format(database, options['name'],
                                          data_dict['id'])
        file_path = '{}/{}'.format(CSV_FOLDER, file_name)
        write_csv(file_path, fields, rows)
        if os.path.getsize(file_path) > 20 * (1024**2):
          rc = os.system('gzip -f ' + file_path)
          file_name = file_name + '.gz' if rc == 0 else file_name
          file_path = '{}/{}'.format(CSV_FOLDER, file_name)

        url = 'http://{base_url}:{port}/csv/{name}'.format(
          base_url=socket.gethostname(),
          port=WEBAPP_PORT,
          name=file_name,
        )
        options['url'] = url

      if 'email_address' in options:
        subj = 'DbNet -- Result for Query {}'.format(data_dict['id'])
        body_text = 'URL: {url}\n\nROWS: {rows}\n\nSQL:\n{sql}'.format(
          url=url, rows=len(rows), sql=sql)
        to_address = options['email_address']
        email_template = os.getenv("SMTP_TEMPLATE")
        if 'exchange_server' == email_template:
          email_func = send_email_exchange
        elif 'outlook' == email_template:
          email_func = send_from_outlook
        elif 'gmail' == email_template:
          email_func = send_from_gmail
        else:
          raise Exception('Email method not implemented!')

        email_func(to_address, subj, body_text)

        if len(rows) > 100:
          rows = rows[:100]

      e_t = epoch()
      secs = e_t - s_t

      # Add query
      store.sqlx('queries').add(
        task_id=data_dict['id'],
        database=database,
        sql_text=sql,
        exec_date=s_t,
        duration_sec=secs,
        row_count=len(rows),
        limit_val=limit,
        cached=cache_used,
        sql_md5=hashlib.md5(sql.encode('utf-8')).hexdigest(),
        last_updated=epoch(),
      )

      if sql.strip():
        sql_fpath = '{}/{}.{}.sql'.format(SQL_FOLDER, database,
                                          data_dict['id'])
        sql_text = '-- Completed @ {} in {} seconds.\n\n{}'.format(
          now_str(), secs, sql)
        write_file(sql_fpath, sql_text)

      # time.sleep(0.5)
      data = dict(
        id=data_dict['id'],
        payload_type='query-data',
        database=database,
        rows=rows,
        headers=fields,
        start_ts=s_t,
        end_ts=e_t,
        execute_time=round(secs, 2),
        completed=True,
        cache_used=cache_used,
        options=options,
        pid=worker_pid,
        orig_req=data_dict,
        sid=sid,
      )

    except Exception as E:
      secs = epoch() - s_t
      err_msg_long = get_exception_message()
      err_msg = get_error_str(E)

      worker.log(E)
      data = dict(
        id=id,
        payload_type='query-data',
        database=database,
        rows=[],
        headers=[],
        execute_time=round(secs, 2),
        completed=False,
        error='ERROR:\n' + err_msg,
        options=options,
        pid=worker_pid,
        orig_req=data_dict,
        sid=sid)

    finally:
      # worker.pipe.send_to_parent(data)
      worker.put_parent_q(data)

  data_dict['limit'] = int(data_dict.get('limit', 500))
  data_dict['options'] = data_dict.get('options', {})
  data_dict['sql'] = data_dict.get('sql', '')

  start_sql(
    data_dict['sql'],
    data_dict['id'],
    data_dict['limit'],
    data_dict['options'],
    data_dict['sid'],
  )


def get_analysis_sql(worker: Worker, data_dict):
  """Run the specified analysis and send results to frontend.

  Args:
    worker: the respective worker
    data_dict: the request payload dictionary
  """
  database = data_dict['database']

  try:
    conn = get_conn(database)
    if data_dict['analysis'] == 'join-match':
      sql = conn.analyze_join_match(as_sql=True, **data_dict['kwargs'])
    else:
      sql = conn.analyze_fields(
        analysis=data_dict['analysis'],
        table_name=data_dict['table_name'],
        fields=data_dict['fields'],
        as_sql=True,
        **data_dict['kwargs'])

    data = dict(
      id=data_dict['id'],
      payload_type='template-sql',
      sql=sql,
      completed=True,
      orig_req=data_dict,
      sid=data_dict['sid'],
    )

  except Exception as E:
    worker.log(E)
    err_msg = get_error_str(E)

    data = dict(
      id=data_dict['id'],
      payload_type='template-sql',
      sql=None,
      completed=False,
      error=err_msg,
      orig_req=data_dict,
      sid=data_dict['sid'],
    )

  finally:
    worker.put_parent_q(data)


def update_meta(worker: Worker, data_dict):
  """Update the worker's metadata and send results to frontend.

  Args:
    worker: the respective worker
    data_dict: the request payload dictionary
  """
  database = data_dict['database']

  try:
    conn = get_conn(database)
    make_rec = lambda name, rec: store.sqlx(name).ntRec(**dict(
      db_name=database,
      last_updated=int(time.time()),
      **rec
    ))

    # meta_tables
    table_data = [
      make_rec('meta_tables', row._asdict()) for row in conn.get_all_tables()
    ]
    store.sqlx('meta_tables').replace(table_data)

    # meta_columns
    column_data = [
      make_rec('meta_columns', row._asdict())
      for row in conn.get_all_columns()
    ]
    store.sqlx('meta_columns').replace(column_data)

    data = dict(
      id=data_dict['id'],
      payload_type='meta-updated',
      completed=True,
      orig_req=data_dict,
      sid=data_dict['sid'],
    )

  except Exception as E:
    worker.log(E)
    err_msg = get_error_str(E)

    data = dict(
      id=data_dict['id'],
      payload_type='meta-updated',
      completed=False,
      error=err_msg,
      orig_req=data_dict,
      sid=data_dict['sid'],
    )
  finally:
    worker.put_parent_q(data)


func_map = {
  'submit-sql': execute_sql,
  'get-meta-tables': update_meta,
  'get-meta-columns': update_meta,
  'get-analysis-sql': get_analysis_sql
}


def run(db_prof, conf_queue: Queue, worker: Worker):
  """Launch the database worker and await requests.
  
  Args:
    db_prof: the db profile
    conf_queue: a multiprocessing Queue
    worker: the respective worker.
  """

  global worker_name, worker_status
  log = worker.log
  worker_name = worker.name
  worker_status = 'IDLE'
  set_worker_idle()
  worker_db_prof = db_prof

  while True:
    try:
      time.sleep(0.005)  # brings down CPU loop usage
    except (KeyboardInterrupt, SystemExit):
      return
    # data_dict = worker.pipe.recv_from_parent(timeout=0)
    data_dict = worker.get_child_q()
    if data_dict:
      conf_data = {'payload_type': 'confirmation'}
      if data_dict['req_type'] in func_map:
        worker_queue.append(data_dict)
        sync_queue()
        conf_data['queued'] = True

        # Add task
        store.sqlx('tasks').add(
          task_id=data_dict['id'],
          function=func_map[data_dict['req_type']].__name__,
          queue_date=now(),
          start_date=None,
          end_date=None,
          args=jdumps([]),
          kwargs=jdumps(data_dict),
          error=None,
          worker_name=worker_name,
          worker_pid=worker_pid,
          last_updated=epoch(),
        )

        log('+({}) Queued task: {}'.format(len(worker_queue), data_dict))

      # Send receipt confirmation?
      # with worker.lock:
      #   worker.pipe.send_to_parent(conf_data)

    if len(worker_queue) and worker_status == 'IDLE':
      data_dict = worker_queue.popleft()
      sync_queue()
      worker_status = 'BUSY'
      func = func_map[data_dict['req_type']]

      # Sync worker
      store.sqlx('workers').update_rec(
        hostname=worker.hostname,
        worker_name=worker.name,
        status=worker_status,
        task_id=data_dict['id'],
        task_function=func.__name__,
        task_start_date=now(),
        task_args=jdumps([]),
        task_kwargs=jdumps(data_dict),
        last_updated=epoch(),
      )

      # Sync task
      store.sqlx('tasks').update_rec(
        task_id=data_dict['id'],
        start_date=now(),
        last_updated=epoch(),
      )

      try:
        error_data = None
        func(worker, data_dict)
      except Exception as E:
        log(E)
        error_data = dict(
          id=data_dict['id'],
          sid=data_dict['sid'],
          payload_type='task-error',
          error=get_error_str(E),
        )
        # worker.pipe.send_to_parent(error_data)
        worker.put_parent_q(error_data)
      finally:

        # Sync worker
        worker_status = 'IDLE'
        set_worker_idle()

        # Sync task
        store.sqlx('tasks').update_rec(
          task_id=data_dict['id'],
          end_date=now(),
          error=jdumps(error_data) if error_data else None,
          last_updated=epoch(),
        )
