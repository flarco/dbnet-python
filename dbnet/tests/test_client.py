import os, time, unittest
from xutil.web import create_sio_client
from xutil.helpers import epoch_mil, log
import uuid
WEBAPP_PORT = int(os.getenv('DBNET_WEBAPP_PORT', default=5566))

sio_client = create_sio_client('localhost', WEBAPP_PORT)


def on_response(data):
  if data == 'OK': return
  res = '+OK' if data['completed'] else '~NOT OK'
  res = '+Queued' if 'queued' in data and data['queued'] else res
  log('{} for {}: {}'.format(
    res,
    data['orig_req']['req_type'],
    # data['req_type'],
    data,
  ))


def on_taskerror(data):
  log('~>> task-error response: {}'.format(data))


def on_querydata(data):
  log('->> query-data response: {}'.format(data))


sio_client.on('task-error', on_taskerror)
sio_client.on('query-data', on_querydata)
sio_client.on('client-response', on_response)


# https://docs.python.org/3/library/unittest.html
class TestSIOClient(unittest.TestCase):
  def test_get_workers(self):
    """ Test get-workers"""
    data = dict(
      id=epoch_mil(),
      req_type='get-workers',
    )

    def on_response(data):
      self.assertTrue(data['completed'])

    sio_client.on('client-response', on_response)
    sio_client.emit('client-request', data)
    sio_client.wait(seconds=1)
    self.assertEqual('foo'.upper(), 'FOO')

  def test_stop_worker(self):
    """ Test stop-worker"""
    data = dict(
      id=epoch_mil(),
      req_type='stop-worker',
      worker_name="dbnet-PG_XENIAL-0",
    )

    def on_response(data):
      self.assertTrue(data['completed'])

    sio_client.on('client-response', on_response)
    sio_client.emit('client-request', data)
    sio_client.wait(seconds=1)

  def test_submit_sql(self):
    """ Test submit-sql"""
    data = dict(
      id=epoch_mil(),
      req_type='stop-worker',
      worker_name="dbnet-PG_XENIAL-0",
    )

    def on_response(data):
      self.assertTrue(data['queued'])

    def on_querydata(data):
      self.assertEqual(data['status'], 'COMPLETED')

    sio_client.on('client-response', on_response)
    sio_client.on('query-data', on_querydata)

    for i in range(2):
      data = dict(
        id=str(uuid.uuid4()),
        req_type='submit-sql',
        database='PG_XENIAL',
        sql='''select count(*) cnt from bank.mint_transactions''',
      )
      sio_client.emit('client-request', data)

    sio_client.wait(seconds=3)


if __name__ == '__main__':
  unittest.main()
