from xutil.parallelism import Worker
from xutil.diskio import write_csv
from xutil.helpers import log, struct, now, epoch, jdumps, get_db_profile, get_exception_message
from xutil import get_conn
from xutil.database.base import fwa, fwo
from collections import deque
import time, socket
import os, store, hashlib

worker_db_prof = {}
worker_hostname = socket.gethostname()
worker_name = None
worker_status = 'IDLE'
worker_queue = deque([])
worker_pid = os.getpid()

sync_queue = lambda: store.worker_set(
  hostname=worker_hostname, worker_name=worker_name,
  queue_length=len(worker_queue))


def execute_sql(worker: Worker, data_dict):
  "Execute SQL operation"
  log = worker.log

  database = data_dict['database']
  sid = data_dict['sid']
  pid = worker_pid

  conn = get_conn(database)

  def start_sql(sql, id, limit, options, sid):
    rows = fields = []
    get_fields = lambda r: r.__fields__ if hasattr(r, '__fields__') else r._fields

    task_id = redb9.hget(id, hkey='cli-web_app-id_map')

    try:
      s_t = now()

      def exec_sql(sql):
        log(
          '\n------------SQL-START------------\n{}\n------------SQL-END------------ \n'.
          format(sql),
          color='blue')
        log('LIMIT: ' + str(limit), color='blue')
        for field, rows in conn.execute_multi(
            sql, dtype='tuple', limit=int(limit)):
          yield fields, rows

      if 'special' in options:
        pass
      #   if options['special'] == 'join-analyze':
      #     rows = conn.join_analyze(sql)
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'get_schemas':
      #     db = options['special_values']['database']
      #     rows = conn.get_schemas()
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'get_objects':
      #     schema = options['special_values']['schema']
      #     object_type = options['special_values']['object_type']
      #     rows = conn.get_objects(schema, object_type)
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'get_columns':
      #     obj = options['special_values']['object']
      #     object_type = options['special_values']['object_type']
      #     rows = conn.get_columns(obj, object_type)
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'get_ddl':
      #     obj = options['special_values']['object']
      #     object_type = options['special_values']['object_type']
      #     rows = conn.get_ddl(obj, object_type)
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'analyze-chars':
      #     obj = options['special_values']['object']
      #     sp_fields = options['special_values']['fields']
      #     sql = conn.analyze_chars(obj, sp_fields, as_sql=True)
      #     send_to_web_server('sql-text', dict(id=id, sql=sql, sid=sid))
      #     fields, rows = exec_sql(sql)

      #   elif options['special'] == 'analyze-fields':
      #     obj = options['special_values']['object']
      #     sp_fields = options['special_values']['fields']
      #     sql = conn.analyze_fields(obj, sp_fields, as_sql=True)
      #     send_to_web_server('sql-text', dict(id=id, sql=sql, sid=sid))
      #     fields, rows = exec_sql(sql)

      #   elif options['special'] == 'analyze-fields-group':
      #     obj = options['special_values']['object']
      #     sp_fields = options['special_values']['fields']
      #     group_exp = options['special_values']['group_exp']
      #     rows = conn.analyze_fields_group(obj, sp_fields, group_exp)
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'analyze-fields-distro':
      #     obj = options['special_values']['object']
      #     sp_fields = options['special_values']['fields']
      #     limit = options['special_values']['limit']
      #     sql = conn.analyze_fields_distro(obj, sp_fields, limit, as_sql=True)
      #     send_to_web_server('sql-text', dict(id=id, sql=sql, sid=sid))
      #     fields, rows = exec_sql(sql)

      #   elif options['special'] == 'analyze-fields-distro-group':
      #     obj = options['special_values']['object']
      #     sp_fields = options['special_values']['fields']
      #     limit = options['special_values']['limit']
      #     group_exp = options['special_values']['group_exp']
      #     rows = conn.analyze_fields_distro_group(obj, sp_fields, group_exp,
      #                                             limit)
      #     fields = get_fields(rows[0]) if rows else []

      #   elif options['special'] == 'analyze-fields-date-distro':
      #     obj = options['special_values']['object']
      #     sp_fields = options['special_values']['fields']
      #     # where_clause = options['special_values']['where_clause']
      #     sql = conn.analyze_fields_date_distro(obj, sp_fields, as_sql=True)
      #     send_to_web_server('sql-text', dict(id=id, sql=sql, sid=sid))
      #     fields, rows = exec_sql(sql)

      #   elif options['special'] == 'analyze-fields-date-distro-wide':
      #     obj = options['special_values']['object']
      #     sp_date_field = options['special_values']['date_field']
      #     sp_fields = options['special_values']['fields']
      #     # where_clause = options['special_values']['where_clause']
      #     sql = conn.analyze_fields_date_distro_wide(
      #       obj, sp_date_field, sp_fields, as_sql=True)
      #     send_to_web_server('sql-text', dict(id=id, sql=sql, sid=sid))
      #     fields, rows = exec_sql(sql)

      #   elif options['special'] == 'analyze-match-rate':
      #     src_table = options['special_values']['src_table']
      #     src_field = options['special_values']['src_field']
      #     tgt_table = options['special_values']['tgt_table']
      #     tgt_field = options['special_values']['tgt_field']
      #     rows = conn.analyze_match_rate(src_table, src_field, tgt_table,
      #                                    tgt_field)
      #     fields = get_fields(rows[0]) if rows else []

      else:
        for fields, rows in exec_sql(sql):
          fields, rows = fields, rows

      if rows == None: rows = []

      # if 'email' in options:
      #   file_name = '{}-{}-{}.csv'.format(
      #     os.getenv('USER'), options['name'], id)
      #   file_path = '{}/{}'.format(public_folder, file_name)
      #   write_csv(file_path, fields, rows)
      #   if os.path.getsize(file_path) > 20 * (1024**2):
      #     rc = os.system('gzip -f ' + file_path)
      #     file_name = file_name + '.gz' if rc == 0 else file_name
      #     file_path = '{}/{}'.format(public_folder, file_name)

      #   os.system('chmod 770 ' + file_path)

      #   url = 'http://' + socket.gethostname(
      #   ) + ':29999/spark_results/' + file_name

      #   subj = 'Db-Server Result for Query {}'.format(id)
      #   body_text = 'URL: {url}\n\nROWS: {rows}\n\nSQL:\n{sql}'.format(
      #     url=url, rows=len(rows), sql=sql)
      #   send_email_exchange(options['email'], subj, body_text)

      #   if len(rows) > 100:
      #     rows = rows[:100]

      secs = (now() - s_t).total_seconds()

      # Add query
      store.sqlx('queries').add(
        task_id=data_dict['id'],
        sql_text=sql,
        exec_date=s_t,
        duration_sec=secs,
        row_count=len(rows),
        limit=limt,
        cached=False,
        sql_md5=hashlib.md5(sql),
        last_updated=epoch(),
      )

      data = dict(
        id=data_dict['id'],
        payload_type='query-data',
        database=database,
        rows=rows,
        headers=fields,
        execute_time=round(secs, 2),
        status='COMPLETED',
        options=options,
        pid=worker_pid,
        error='',
        sid=sid,
      )

    except Exception as e:
      secs = (now() - s_t).total_seconds()
      err_msg_long = get_exception_message()
      err_msg = get_exception_message(raw=True)

      log(err_msg_long, color='red')
      data = dict(
        id=id,
        payload_type='query-data',
        database=database,
        rows=[],
        headers=[],
        execute_time=round(secs, 2),
        status='FAILED',
        error='ERROR:\n' + err_msg,
        options=options,
        pid=worker_pid,
        sid=sid)

    finally:
      with worker.lock:
        worker.pipe.send_to_parent(data)

  data_dict['limit'] = int(data_dict.get('limit', 500))
  data_dict['options'] = data_dict.get('options', {})

  start_sql(
    data_dict['sql'],
    data_dict['id'],
    data_dict['limit'],
    data_dict['options'],
    data_dict['sid'],
  )


func_map = {'submit-sql': execute_sql}


def run(db_prof, worker: Worker):
  log = worker.log
  worker_name = worker.name
  worker_status = store.sqlx('workers').select_one(
    fwa(hostname=worker_hostname, worker_name=worker_name), field='status')
  worker_db_prof = db_prof

  while True:
    try:
      time.sleep(0.005)  # brings down CPU loop usage
    except (KeyboardInterrupt, SystemExit):
      return
    data_dict = worker.pipe.recv_from_parent(timeout=0)
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

        log('+Queued task: {}'.format(data_dict))

      # Send receipt confirmation
      with worker.lock:
        worker.pipe.send_to_parent(conf_data)

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
          task_id=data_dict['id'],
          sid=data_dict['sid'],
          payload_type='task-error',
          error=E,
        )
        with worker.lock:
          worker.pipe.send_to_parent(error_data)
      finally:
        worker_status = 'IDLE'

        # Sync worker
        store.sqlx('workers').update_rec(
          hostname=worker.hostname,
          worker_name=worker.name,
          status=worker_status,
          task_id=None,
          task_function=None,
          task_start_date=None,
          task_args=None,
          task_kwargs=None,
          last_updated=epoch(),
        )

        # Sync task
        store.sqlx('tasks').update_rec(
          task_id=data_dict['id'],
          end_date=now(),
          error=jdumps(error_data) if error_data else None,
          last_updated=epoch(),
        )
