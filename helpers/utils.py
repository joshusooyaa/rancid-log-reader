import os
import re
from pathlib import Path
import subprocess
from logger.logger import logger

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
      if device not in devices:
        devices.append(device)

  return devices

def fetch_git_changes(base_path, client_ids):
  changed_devices = {}
  for client_id in client_ids:
    changed_devices[client_id] = []
    client_id = client_id.upper()
    client_path = base_path + "/" + client_id    
    if os.path.isdir(client_path):
      try:
        result = subprocess.run(["git", "diff", "--name-only", "@{24 hours ago}", "HEAD"], cwd=client_path, capture_output=True, text=True)
        changed_devices[client_id] = process_git_diff(result.stdout)
      except:
        logger.error(f"Error fetching git changes for {client_id}")

  return changed_devices

def process_git_diff(diff):
  changed_devices = []
  for line in diff.splitlines():
    line = line.strip()
    if "/" in line:
      device = line.split("/")[-1]
      if device not in changed_devices:
        changed_devices.append(device)
  
  return changed_devices

def build_topdesk_ticket_logins(failed_logins):
  body = "Rancid has been unable to log into the following devices in the past 24 hours:\n"
  for client_id, devices in failed_logins.items():
    if devices:
      device_list = ", ".join(devices)
      body += f"{client_id}: {device_list}\n"
    
  return body

def build_topdesk_ticket_changes(changed_devices):
  body = "The following devices have been changed in the past 24 hours:\n"
  for client_id, devices in changed_devices.items():
    if devices:
      device_list = ", ".join(devices)
      body += f"{client_id}: {device_list}\n"
    
  return body