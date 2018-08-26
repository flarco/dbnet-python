import os, time
from xutil.web import create_sio_client
from xutil.helpers import epoch_mil, log

WEBAPP_PORT = int(os.getenv('DBNET_WEBAPP_PORT', default=5566))

sio_client = create_sio_client('localhost', WEBAPP_PORT)


def on_response(data):
  log('client-request_response')
  print(data)
  res = '+OK' if data['completed'] else '~NOT OK'
  log('{} for {}'.format(res, data['orig_req']['req_type']))


def on_taskerror(data):
  log('>> task-error response: {}'.format(data))


def on_querydata(data):
  log('>> query-data response: {}'.format(data))


sio_client.on('task-error', on_taskerror)
sio_client.on('query-data', on_querydata)

########### Test get-workers

data = dict(
  id=epoch_mil(),
  req_type='get-workers',
)
sio_client.emit('client-request', data, on_response)
sio_client.wait(seconds=3)

########### Test stop-worker

data = dict(
  id=epoch_mil(),
  req_type='stop-worker',
  worker_name="dbnet-PG_XENIAL-0",
)
sio_client.emit('client-request', data, on_response)
sio_client.wait(seconds=3)

########### Test submit-sql

data = dict(
  id=epoch_mil(),
  req_type='submit-sql',
  database='PG_XENIAL',
  sql='select 1 as a',
)
sio_client.emit('client-request', data, on_response)
sio_client.wait(seconds=6)
