import os, sys, hashlib, time
from xutil.database.base import make_sqlx, fwa, fwo, rows_to_dicts
from xutil.database.sqlite import SQLiteConn
from xutil.helpers import get_home_path, log, now, jdumps, jloads
from sqlalchemy import MetaData, Table, Column, String, Numeric, DateTime
from sqlalchemy.sql import func, text
from collections import namedtuple
import typing, jmespath

DBNET_FOLDER = os.getenv('DBNET_FOLDER', default=get_home_path() + '/dbnet')

# Models
'''
Things needed to track state

workers: name, hostname, status, current job, progress
editors: one per database
tabs: many per database, sql_text, data_json, state_json
metadata: shema, tables, columns store cache per database
queries: history of queries, status, text, rows_returned, limit, duration (start, end), error text, cache key
tasks: same as queries? for etl jobs for examples, history of tasks, args, kwargs, errors
state: KV store of current state (active database, active tabs, state of tabs (waiting for query or not))
cache: cache results

'''

db_path = DBNET_FOLDER + '/storage.db'
# db_path = ':memory:'  # for testing
conn = SQLiteConn({'database': db_path, 'type': 'sqlite'})
engine = conn.get_engine()
epoch_def = text("(strftime('%s', 'now'))")

tables: typing.Dict[str, Table] = {}
ntRec: typing.Dict[str, namedtuple] = {}
sql_func_map = {}
metadata = MetaData()

# Workers, unique list per machine
tables['workers'] = Table(
  'workers',
  metadata,
  Column('hostname', String, primary_key=True),
  Column('worker_name', String, primary_key=True),
  Column('worker_type', String),
  Column('worker_pid', Numeric),
  Column('status', String),  # IDLE, BUSY, OFF
  Column('task_id', String),
  Column('task_function', String),
  Column('task_start_date', DateTime),
  Column('task_args', String),
  Column('task_kwargs', String),
  Column('progress', Numeric),
  Column('queue_length', Numeric),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# Databases
tables['databases'] = Table(
  'databases',
  metadata,
  Column('db_name', String, primary_key=True),
  Column('state_json', String),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# store of column metadata, fast full text search
tables['meta_tables'] = Table(
  'meta_tables',
  metadata,
  Column('db_name', String),  #FK of databases.db_name
  Column('schema_name', String),
  Column('table_name', String),
  Column('table_type', String),
  Column('row_count', Numeric),
  Column('last_analyzed', DateTime),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# store of column metadata, fast full text search
tables['meta_columns'] = Table(
  'meta_columns',
  metadata,
  Column('db_name', String),  #FK of databases.db_name
  Column('schema_name', String),
  Column('table_name', String),
  Column('column_name', String),
  Column('column_type', String),
  Column('row_count', Numeric),
  Column('value_count', Numeric),
  Column('distinct_count', Numeric),
  Column('null_count', Numeric),
  Column('last_analyzed', DateTime),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# state of sessions per database
tables['sessions'] = Table(
  'sessions',
  metadata,
  Column('db_name', String, primary_key=True),  #FK of databases.db_name
  Column('session_name', String, primary_key=True),
  Column('editor_text', String),
  Column('active_tab_name', String),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# state of tabs per session
tables['tabs'] = Table(
  'tabs',
  metadata,
  Column('db_name', String, primary_key=True),  #FK of databases.db_name
  Column('session_name', String,
         primary_key=True),  #FK of sessions.session_name
  Column('tab_name', String, primary_key=True),
  Column('sql_text', String),
  Column('data_json', String),  # tab headers & rows
  Column('props_json', String),  # pinned, limit, duration, etc
  Column('last_updated', DateTime, server_default=epoch_def),
)

# All Tasks, queries, jobs
tables['tasks'] = Table(
  'tasks',
  metadata,
  Column('task_id', String, primary_key=True),
  Column('function', String),
  Column('queue_date', DateTime),
  Column('start_date', DateTime),
  Column('end_date', DateTime),
  Column('args', String),
  Column('kwargs', String),
  Column('error', String),
  Column('worker_name', String),
  Column('worker_pid', String),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# Query text, to enable full text search of history
tables['queries'] = Table(
  'queries',
  metadata,
  Column('task_id', String, primary_key=True),  #same as task_id
  Column('sql_text', String),
  Column('exec_date', DateTime),
  Column('duration_sec', Numeric),
  Column('row_count', Numeric),
  Column('limit_val', Numeric),
  Column('cached', String),
  Column('sql_md5', String),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# store temporary cache of query results
tables['cache'] = Table(
  'cache',
  metadata,
  Column('sql_md5', String, primary_key=True),
  Column('sql_text', String),
  Column('data_json', String),
  Column('expire_date', DateTime),
  Column('last_updated', DateTime, server_default=epoch_def),
)

# store global settings & state
tables['state'] = Table(
  'state',
  metadata,
  Column('key', String, primary_key=True),  # active_database, etc
  Column('value', String),
  Column('last_updated', DateTime, server_default=epoch_def),
)

make_rec = lambda **d: namedtuple('Rec', d.keys())(**d)

# esql = ExpressSQL(conn, schema='main', tables=tables)
sqlx = make_sqlx(conn, schema='main', tables=tables)


state_set = lambda key, value: sqlx('state').replace_rec(
  key=key, value=value,)
state_get = lambda key: sqlx('state').select_one(
  fwa(key=key), field='value',)

cache_set = lambda sql_text, data_json, expire_date: sqlx('cache').replace_rec(
  sql_md5=hashlib.md5(sql_text),
  sql_text=sql_text,
  expire_date=expire_date,
)
cache_get = lambda sql_text: sqlx('cache').select_one(
  fwa(sql_md5=hashlib.md5(sql_text)),)

worker_add = lambda **kws: sqlx('workers').replace_rec(**kws)
worker_set = lambda **kws: sqlx('workers').update_rec(**kws)
worker_get = lambda hostname, worker_name: sqlx('workers').select_one(
  fwa(hostname=hostname, worker_name=worker_name),)
worker_getall = lambda: sqlx('workers').select()
add_task = lambda **kws: sqlx('tasks').replace_rec(**kws)


def load_session(db_name, session_name):
  sess_rec = sqlx('sessions').select_one(
    fwa(db_name=db_name, session_name=session_name),
    as_dict=True,
  )
  tabs_recs = sqlx('tabs').select(
    fwa(db_name=db_name, session_name=session_name),
    as_dict=True,
  )

  if sess_rec:
    sess_rec['tabs'] = tabs_recs

  return sess_rec


def save_session(**kws):
  tabs_rec = kws['tabs']
  del kws['tabs']
  sqlx('databases').replace_rec(
    db_name=kws['db_name'], session_name=kws['session_name'])
  sqlx('sessions').replace_rec(**kws)
  sqlx('tabs').replace(tabs_rec)


def set_dbquery_state(**kws):
  dbquery_data = kws['data']
  dn_name = dbquery_data['db_name']
  sqlx('databases').replace_rec(
    db_name=dn_name,
    state_json=jdumps(dbquery_data),
  )


def get_dbquery_state(**kws):
  db_name = kws['db_name']
  rec = sqlx('databases').select_one(fwa(db_name=db_name), as_dict=True)
  return jloads(rec['state_json']) if rec else {'db_name': db_name}


# Stack wide functions to sync data from/to backend database
store_func = dict(
  create_session=save_session,
  save_session=save_session,
  load_session=load_session,
  set_dbquery_state=set_dbquery_state,
  get_dbquery_state=get_dbquery_state,
  load_database=
  lambda db_name: sqlx('databases').select_one(fwa(db_name=db_name), as_dict=True),
  get_sessions=lambda db_name: sqlx('sessions').select_one(
    fwa(db_name=db_name),
    as_dict=True,
  ),
)


def create_tables(drop_first=False):
  if drop_first:
    # ans = input('Authorize Tables Drop. Please confirm with "Y": ')
    ans = 'y'
    if ans.lower() == 'y':
      log('-Dropped tables!')
      metadata.drop_all(engine)
    else:
      sys.exit()

  metadata.create_all(engine)
  log('+DB Tables OK.')


if __name__ == '__main__':
  create_tables(drop_first=True)
  state_set('key', 1)
  print(sqlx('state').select())
  # time.sleep(2)
  state_set('key', 44)
  print(sqlx('state').select())
  print(
    conn.select(
      "select datetime(last_updated, 'unixepoch', 'localtime') as last_updated from main.state"
    ))

  # insert('cache', ntRec['cache'](key, value, now())