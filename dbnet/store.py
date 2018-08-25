import os, sys, hashlib
from xutil.database.base import SQLx, fwa, fwo
from xutil.database.sqlite import SQLiteConn
from xutil.helpers import get_home_path, log, now
from sqlalchemy import MetaData, Table, Column, String, Numeric, DateTime
from sqlalchemy.sql import func
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
  Column('worker_pid', Numeric),
  Column('status', String),  # IDLE, BUSY, OFF
  Column('task_id', Numeric),
  Column('task_function', String),
  Column('task_start_date', DateTime),
  Column('task_args', String),
  Column('task_kwargs', String),
  Column('progress', Numeric),
  Column('last_update', DateTime),
)

# Databases
tables['databases'] = Table(
  'databases',
  metadata,
  Column('db_name', String, primary_key=True),
  Column('editor_text', String),
  Column('active_tab_name', String),
  Column('state_json', String),
  Column('last_update', DateTime),
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
  Column('last_update', DateTime),
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
  Column('last_update', DateTime),
)

# state of tabs per database
tables['tabs'] = Table(
  'tabs',
  metadata,
  Column('db_name', String, primary_key=True),  #FK of databases.db_name
  Column('tab_name', String, primary_key=True),
  Column('sql_text', String),
  Column('data_json', String),  # tab headers & rows
  Column('state_json', String),  # pinned, limit, duration, etc
  Column('last_update', DateTime),
)

# All Tasks, queries, jobs
tables['tasks'] = Table(
  'tasks',
  metadata,
  Column('task_id', Numeric, primary_key=True),
  Column('function', String),
  Column('queue_date', DateTime),
  Column('start_date', DateTime),
  Column('end_date', DateTime),
  Column('args', String),
  Column('kwargs', String),
  Column('error', String),
  Column('worker_name', String),
  Column('worker_pid', String),
  Column('last_update', DateTime),
)

# Query text, to enable full text search of history
tables['queries'] = Table(
  'queries',
  metadata,
  Column('task_id', Numeric, primary_key=True),  #same as task_id
  Column('sql_text', String),
  Column('exec_date', DateTime),
  Column('duration_sec', Numeric),
  Column('row_count', Numeric),
  Column('limit', Numeric),
  Column('cached', String),
  Column('sql_md5', String),
  Column('last_update', DateTime),
)

# store temporary cache of query results
tables['cache'] = Table(
  'cache',
  metadata,
  Column('sql_md5', String, primary_key=True),
  Column('sql_text', String),
  Column('data_json', String),
  Column('expire_date', DateTime),
  Column('last_update', DateTime),
)

# store global settings & state
tables['state'] = Table(
  'state',
  metadata,
  Column('key', String, primary_key=True),  # active_database, etc
  Column('value', String),
  Column('last_update', DateTime),
)

make_rec = lambda **d: namedtuple('R', d.keys())(**d)

sqlx = SQLx(conn, schema='main', tables=tables)

state_set = lambda key, value: sqlx.replace_rec(
  'state', key=key, value=value, last_update=now(),)
state_get = lambda key: sqlx.select_one(
  'state', fwa(key=key), field='value',)

cache_set = lambda sql_text, data_json, expire_date: sqlx.replace_rec(
  'cache',
  sql_md5=hashlib.md5(sql_text),
  sql_text=sql_text,
  expire_date=expire_date,
  last_update=now(),
)
cache_get = lambda sql_text: sqlx.select_one(
  'cache', fwa(sql_md5=hashlib.md5(sql_text)),)


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
  state_set('key', 44)
  print(state_get('key'))

  # insert('cache', ntRec['cache'](key, value, now())