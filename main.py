from helpers.config_loader import ConfigLoader
from logger.logger import logger
from helpers.utils import *
from emailer import Emailer

config = ConfigLoader()
emailer = Emailer(config, logger)

failed_logins = {}
log_files = get_rancid_logs(config['rancid-log-path'])
for client_id, file_path in log_files.items():
  failed_logins[client_id] = fetch_failed_logins(file_path)

body = ""
if any(failed_logins.values()):
  body = build_topdesk_ticket_logins(failed_logins)

git_changes = fetch_git_changes(config['rancid-config-path'], failed_logins.keys())

if any(git_changes.values()):
  body += build_topdesk_ticket_changes(git_changes)

if body:
  body += "\n\nNote: Microsoft Graph expires on {0}".format(config['microsoft-graph']['expires'])

#emailer.send(body) 