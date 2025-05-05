import os
import re
from pathlib import Path


def get_rancid_logs(log_path):
  log_files = os.listdir(log_path)
  pattern = re.compile(r'^([^.]+)\.(\d{8})\.(\d+)$')
  logs = {}

  for file in log_files:
    match = pattern.match(file)
    if not match:
      continue

    client_id, date_str, time_str = match.groups()
    dt_key = f"{date_str}{time_str.zfill(4)}"
    if client_id not in logs or dt_key > logs[client_id][0]:
      logs[client_id] = (dt_key, file)
    
  return {client_id: str(Path(log_path) / file) for client_id, (dt_key, file) in logs.items()}

def fetch_failed_logins(log_file):
  with open(log_file, 'r') as f:
    lines = f.readlines()

  devices = []

  for line in lines:
    if "error" in line:
      device = line.split()[0]
      print(device)
      if device not in devices:
        devices.append(device)

  return devices

def build_topdesk_ticket(failed_logins):
  body = "Rancid has been unable to log into the following devices in the past 24 hours:\n"
  for client_id, devices in failed_logins.items():
    if devices:
      device_list = ", ".join(devices)
      body += f"{client_id}: {device_list}\n"
    
  return body
