import os, psutil, time, socket, platform
from xutil.parallelism import Worker, Queue
from xutil.helpers import get_process_data, log

pids = {}


def collect_perf():
  perf_summary = dict(tot_cpu_prct=0.0, tot_ram_prct=0.0, tot_threads=0)
  for pid in list(pids):
    try:
      proc = pids[pid]
      for child in proc.children():
        pids[child.pid] = psutil.Process(child.pid)
      perf_rec = get_process_data(proc)
      perf_summary['tot_cpu_prct'] += perf_rec['cpu_percent']
      perf_summary['tot_ram_prct'] += perf_rec['memory_percent']
      perf_summary['tot_threads'] += perf_rec['num_threads']

    except psutil.NoSuchProcess:
      del pids[pid]
      continue

  return perf_summary


def run(worker: Worker):
  uname = platform.uname()
  on_wsl = uname[0] == 'Linux' and "microsoft" in uname[3].lower()
  if on_wsl:
    log('-Cannot run Monitor on Linux WSL')
    return
  
  while True:
    try:
      time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
      return

    data_dict = worker.get_child_q()
    if data_dict:
      pids[data_dict['pid']] = psutil.Process(data_dict['pid'])

    perf_summary = collect_perf()
    perf_summary['payload_type'] = 'monitor'
    perf_summary['tot_ram_prct'] = round(perf_summary['tot_ram_prct'], 1)
    perf_summary['tot_cpu_prct'] = round(perf_summary['tot_cpu_prct'], 2)
    worker.get_parent_q()  # clear queue
    worker.put_parent_q(perf_summary)
