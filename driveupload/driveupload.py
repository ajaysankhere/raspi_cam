from __future__ import print_function
import os
import datetime
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

def upload_to_drive():
	SCOPES = 'https://www.googleapis.com/auth/drive'
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

	FILES = (
	    ('output.avi', 'application/video'),
	)

	for filename, mimeType in FILES:
	    metadata = {'name': datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S_")+filename}
	    if mimeType:
	        metadata['mimeType'] = mimeType
	        res = DRIVE.files().create(body=metadata, media_body=filename).execute()
	    if res:
	        print('Uploaded "%s" (%s)' % (filename, res['mimeType']))
	
