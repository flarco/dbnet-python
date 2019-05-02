import os, sys, argparse
from xutil import log
from xutil.helpers import set_nice 


def dbnet_cli():
  """The main CLI launcher"""
  set_nice(1)
  parser = argparse.ArgumentParser(description='DbNet Application')
  parser.add_argument(
    '--serve', help='Start the DbNet server', action='store_true')
  parser.add_argument(
    '--init_db',
    help='Initiatlize the backend SQLite database',
    action='store_true')
  parser.add_argument(
    '--reset_db',
    help='Reset the backend SQLite database',
    action='store_true')
  parser.add_argument(
    '--force', help='Kill any running instance.', action='store_true')
  parser.add_argument('--port', help='The web application port')
  parser.add_argument('--host', help='The web application host. Default is 0.0.0.0')

  args = parser.parse_args()

  if args.port:
    os.environ['DBNET_WEBAPP_PORT'] = args.port

  if args.host:
    os.environ['DBNET_WEBAPP_HOST'] = args.host

  # import after setting port
  from dbnet import server, store

  if args.init_db:
    store.create_tables()
  elif args.reset_db:
    store.create_tables(drop_first=True)
  elif args.serve:
    store.create_tables()
    server.main(kill_existing=args.force)
  else:
    parser.print_help()
