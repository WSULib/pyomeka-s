# pyomeka-s


import json
import os
import requests


# look for config.json at ~/pyomeka-s.json
config_json_path = os.path.join(os.path.expanduser("~"),'pyomeka-s.json')
if os.path.exists(config_json_path):
	print('pyomeka-s.json located, using...')
	with open(config_json_path,'r') as f:
		config = json.loads(f.read())
else:
	config = None


class Repository(object):

	'''
	Class to represent Omeka-S instance
	'''

	def __init__(self):

		# if config loaded, use
		if config:
			self.api_endpoint = config['repository']['api_endpoint']
			self.api_key_identity = config['repository']['api_key_identity']
			self.api_key_credential = config['repository']['api_key_credential']

		# API instance
		self.api = API(
			api_endpoint=self.api_endpoint,
			api_key_identity=self.api_key_identity,
			api_key_credential=self.api_key_credential)


	def get_items(self, per_page=4):

		'''
		Method to list items in Repository

		Returns:
			generator
		'''

		response = self.api.get('items', params={'per_page':per_page})
		return response.json()



class API(object):

	'''
	Class to handle API requests/responses
	'''

	def __init__(self, api_endpoint=None, api_key_identity=None, api_key_credential=None):

		self.api_endpoint = api_endpoint
		self.api_key_identity = api_key_identity
		self.api_key_credential = api_key_credential


	def _merge_credentials(self, params):

		params.update({
			'api_key_identity':self.api_key_identity,
			'api_key_credential':self.api_key_credential
		})
		return params


	def get(self,
		path,
		params = {}):

		# credential
		params = self._merge_credentials(params)

		# issue GET request
		return requests.get('%s/%s' % (self.api_endpoint, path.lstrip('/')), params=params)



class Item(object):

	'''
	Class to represent an Omeka-S Item
	'''

	def __init__(self):
		pass




