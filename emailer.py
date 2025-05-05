import requests
import base64
import time
import os

class Emailer:
  def __init__(self, config, logger):
    self.client_id = config['microsoft-graph']['client-id']
    self.client_secret = config['microsoft-graph']['client-secret']
    self.tenant_id = config['microsoft-graph']['tenant-id']
    self.token_url = 'https://login.microsoftonline.com/{0}/oauth2/v2.0/token'.format(self.tenant_id)
    self.scope = 'https://graph.microsoft.com/.default'
    self.access_token = None
    self.token_expiration = 0

    self.sender = config['microsoft-graph']['email-details']['sender']
    self.subject = config['microsoft-graph']['email-details']['subject']
    self.recipient = config['microsoft-graph']['email-details']['recipient']
    self.logger = logger
  
  def _get_access_token(self):
    if self.access_token is None or time.time() > self.token_expiration:
      payload = {
        'client_id': self.client_id,
        'scope': self.scope,
        'client_secret': self.client_secret,
        'grant_type': 'client_credentials'
      }
      self.logger.info("Fetching token info from {}".format(self.token_url))
      response = requests.post(self.token_url, data=payload)
      if response.status_code == 200:
        token_info = response.json()
        self.access_token = token_info['access_token']
        self.token_expiration = time.time() + token_info['expires_in'] - 300
      else:
        self.logger.error('Could not obtain access token: {0}'.format(response.text))
        return False

    self.logger.info('Access token obtained')
    return self.access_token

  def _fetch_message(self, body):
    email = {
      'message': {
        'subject': self.subject,
        'body': {
          'contentType': 'Text',
          'content': body
        },
        'toRecipients': [
          {
            "emailAddress": {
              "address": self.recipient
            }
          }
        ]
      }
    }

    return email
  
  def send(self, body):
    access_token = self._get_access_token()
    if (access_token):
      url = 'https://graph.microsoft.com/v1.0/users/{0}/sendMail'.format(self.sender)
      headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/json'
      }
      email = self._fetch_message(body)

      response = requests.post(url, headers=headers, json=email)
      if response.status_code == 202:
        self.logger.info('Email successfully sent.')
      else:
        self.logger.error('Could not send email', response=response.text, email=email, url=url)
    else:
      return False