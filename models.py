# pyomeka-s

import json
import logging
import hashlib
import os
import pdb
import requests


# setup logger
logging.basicConfig(level=logging.DEBUG)
# parso shims
logging.getLogger('parso.python.diff').disabled = True
logging.getLogger('parso.cache').disabled = True
logger = logging.getLogger(__name__)


# look for config.json at ~/pyomeka-s.json
config_json_path = os.path.join(os.path.expanduser("~"),'pyomeka-s.json')
if os.path.exists(config_json_path):
	logger.debug('pyomeka-s.json located, using...')
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


	def get_items(self, per_page=25, use_cache=False):

		'''
		Method to list items in Repository

		Returns:
			generator
		'''

		# api GET request
		response = self.api.get('items', params={'per_page':per_page}, use_cache=use_cache)

		# return
		if response.status_code == 200:

			# parse JSON
			response = response.json()

			# yield
			for item_json in response:
				yield Item(self, item_json)


	def get_item(self, item_id, use_cache=False):

		'''
		Method to return single item
		'''

		# api GET request
		response = self.api.get('items/%s' % item_id, params={}, use_cache=use_cache)

		# return
		if response.status_code == 200:

			# return Item
			return Item(self, response.json())

		else:

			return None


	def get_vocabularies(self, per_page=100):

		'''
		Method to return info about vocabularies
		'''

		# api GET request
		response = self.api.get('vocabularies', params={'per_page':per_page})

		# return
		if response.status_code == 200:

			# return as Vocabulary instances
			return [ Vocabulary(self, vocab) for vocab in response.json() ]


	def get_vocabulary(self, prefix=None, uri=None):

		'''
		Retrieve Vocabulary by prefix or URI
		'''

		# api GET request
		if prefix != None:
			response = self.api.get('vocabularies', params={'prefix':prefix})
		elif uri != None:
			response = self.api.get('vocabularies', params={'namespace_uri':uri})

		if response.status_code == 200:

			# parse for length
			vocabs = response.json()

			if len(vocabs) == 1:
				return Vocabulary(self, vocabs[0])

			else:
				logger.debug('multiple vocabularies found, returning as list')
				return [ Vocabulary(self, vocab) for vocab in vocabs ]


	def get_property(self, term):

		'''
		Method to return Property based on term
			- assume full prefix:local_name as this level
		'''

		# api GET request
		response = self.api.get('properties', params={'term':term})

		# parse
		if response.status_code == 200:

			properties = response.json()

			# if one, return as single Property
			if len(properties) == 1:
				return Property(self, properties[0])

			elif len(properties) == 0:
				raise Exception('property not found: %s' % term)

			else:
				raise Exception('expecting 1 but found %s properties for qualified term: %s' % (len(properties), term))



class API(object):

	'''
	Class to handle API requests/responses
	'''

	def __init__(self,
		api_endpoint=None,
		api_key_identity=None,
		api_key_credential=None,
		authenticate_all_requests=True):

		self.api_endpoint = api_endpoint
		self.api_key_identity = api_key_identity
		self.api_key_credential = api_key_credential
		self.authenticate_all_requests = authenticate_all_requests

		# init cache
		self.cache = APICache()
		self.use_cache = True


	def _merge_credentials(self, params):

		params.update({
			'key_identity':self.api_key_identity,
			'key_credential':self.api_key_credential
		})
		return params


	def get(self,
		path,
		params = {},
		use_cache=None):

		'''
		GET requsts to API
		'''

		# handle caching flag
		if use_cache == None:
			use_cache = self.use_cache

		# credential
		if self.authenticate_all_requests:
			params = self._merge_credentials(params)

		# check cache
		if use_cache:
			cache_hit = self.cache.cache_check('get', {'path':path,'params':params})
			if cache_hit != None:
				return cache_hit

		# issue GET request
		response = requests.get('%s/%s' % (self.api_endpoint, path.lstrip('/')), params=params)

		# store cache
		if response.status_code == 200:

			if use_cache and cache_hit == None:
				self.cache.cache_store('get', {'path':path,'params':params}, response)

		# return
		return response


	def patch(self,
		path,
		json_body,
		params = {}):

		'''
		PATCH requsts to API
			- for PATCH requests, credentials are needed
		'''

		# credential
		params = self._merge_credentials(params)
		logger.debug(params)

		# issue GET request
		response = requests.patch('%s/%s' % (self.api_endpoint, path.lstrip('/')), params=params, json=json_body)
		return response



class APICache(object):

	'''
	Class for API Cache
		- naive, lightweight
		- only cache Property and Vocabulary queries
			- unlikely to change
	'''

	def __init__(self):

		self.store = {
			'get':{},
			'patch':{}
		}


	def _calc_cache_hash(self, dict):

		'''
		Calcuate MD5 hash based on dictionary
		'''

		return hashlib.md5(json.dumps(dict, sort_keys=True).encode('utf-8')).hexdigest()


	def cache_check(self, http_verb, dict):

		'''
		Check cache based on dict
		'''

		cache_hit = self.store.get(http_verb).get(self._calc_cache_hash(dict), None)
		return cache_hit


	def cache_store(self, http_verb, dict, response):

		'''
		Store response
		'''

		self.store[http_verb][self._calc_cache_hash(dict)] = response


class Item(object):

	'''
	Class to represent an Omeka-S Item
	'''

	def __init__(self, repo, item_json):

		# store repository instance
		self.repo = repo

		# store json
		self.json = item_json

		# init rollback versions with 0th version
		self.versions = {
			0:self.json.copy()
		}


	@property
	def id(self):
		return self.json.get('o:id')


	@property
	def uri(self):
		return self.json.get('@id')


	def __repr__(self):
		return '<Item: #%s, "%s">' % (self.id, self.title)


	def _calc_last_version_id(self):

		'''
		Method to return most recent version id

		Returns:
			(int): integer key of self.versions
		'''

		vkeys = list(self.versions.keys())
		vkeys.sort()
		return vkeys[-1]


	@property
	def title(self):

		'''
		Return title based on Omeka-S default to dcterms:title
		'''

		title = self.get_property('dcterms:title')

		if title != []:
			return title[0].value
		else:
			return '[Untitled]'


	def get_properties(self):

		'''
		Return metadata properties
		'''

		_omeka_internal = ['@context','@id','@type']

		# loop and create subset
		props = {}
		for property_name in self.json.keys():
			if property_name not in _omeka_internal and not property_name.startswith('o:'):
				props[property_name] = [ Value(self.repo, value_json) for value_json in self.json.get(property_name) ]

		# return
		return props


	def get_property(self, property_input, default=[]):

		'''
		Return instance of single Property
		'''

		# handle property_input
		prop = self._handle_property_arg(property_input)

		value_instances = self.json.get(prop.term, default)

		return [ Value(self.repo, value_json) for value_json in value_instances ]


	def _handle_property_arg(self, property_input):

		'''
		Method to return Property instance given equivocal input
		'''

		# handle property_input
		if type(property_input) == Property:
			prop = property_input
		elif type(property_input) == str:
			# query for property_input id
			prop = self.repo.get_property(property_input)
		else:
			raise Exception('expecting str or Property instance as property')

		# return
		return prop


	def add_property(self,
		property_input,
		value,
		is_public=True,
		property_type='literal'):

		'''
		Method to add Property
			- literal values may repeat

		Args:
			term (str|Property): if string, assume prefix:local_name, else use Property
			value: value to set for @value

		Value instance:
		{
			'@value': '...',
			'is_public': True,
			'property_id': 1,
			'property_label': 'Title',
			'type': 'literal'
	 	}
		'''

		# handle property_input
		prop = self._handle_property_arg(property_input)

		# build value dictionary
		val_dict = {
			'@value': value,
			'is_public': True,
			'property_id': prop.id,
			'property_label': prop.label,
			'type': property_type
		}

		# append if term exists, else create
		if prop.term in self.get_properties().keys():
			self.json[prop.term].append(val_dict)
		else:
			self.json[prop.term] = [val_dict]


	def remove_value(self,
		property_input,
		value):

		'''
		Method to remove property from Item
		'''

		# handle property_input
		prop = self._handle_property_arg(property_input)

		# check self for property AND value
		e_values = self.get_property(prop)

		# comprehend values sans matches
		values_keep = [ e_value for e_value in e_values if e_value.value != value ]

		# update property
		self.json[prop.term] = [ value.json for value in values_keep ]


	def update(self):

		'''
		Method to update Item in Repository
		'''

		# PATCH with self.json
		response = self.repo.api.patch('items/%s' % self.id, self.json)

		if response.status_code == 200:

			# write version
			self.write_version(response.json())

			# return
			return True


	def write_version(self, item_version_json):

		'''
		Method to write version
		'''

		# get new version to write
		last_version_id = self._calc_last_version_id() + 1

		# write
		logger.debug('writing item v%s' % last_version_id)
		self.versions[last_version_id] = item_version_json


	def refresh(self):

		'''
		Methdo to refresh Item
		'''

		# get self from repository
		_item = self.repo.get_item(self.id, use_cache=False)

		# write version
		self.write_version(_item.json.copy())

		# set
		self.json = _item.json.copy()



class Property(object):

	'''
	Class to represent Property

	Property Model example:
		{
	    "@context": "http://example.com/api-context",
	    "@id": "http://example.com/api/properties/1",
	    "@type": "o:Property",
	    "o:id": 1,
	    "o:local_name": "title",
	    "o:label": "Title",
	    "o:comment": "A name given to the resource.",
	    "o:term": "dcterms:title",
	    "o:vocabulary": {
	        "@id": "http://example.com/api/vocabularies/1",
	        "o:id": 1
	    }
	}
	'''

	def __init__(self, repo, property_json):

		# store repository instance
		self.repo = repo

		# store json
		self.json = property_json


	@property
	def id(self):
		return self.json.get('o:id')


	@property
	def term(self):
		return self.json.get('o:term')


	@property
	def label(self):
		return self.json.get('o:label')


	@property
	def comment(self):
		return self.json.get('o:comment')


	@property
	def vocabulary_id(self):
		return self.json.get('o:vocabulary').get('o:id')


	def __repr__(self):

		return '<Property: #%s, %s, "%s">' % (self.id, self.term, self.label)


	@property
	def vocabulary(self):

		'''
		Return instance of associated Vocabulary
		'''

		# query
		response = self.repo.api.get('vocabularies', params={'id':self.vocabulary_id})

		if response.status_code == 200:

			return Vocabulary(self.repo, response.json())



class Value(object):

	'''
	Class to represent value of property

	Value Instance:
	{
		'@value': '...',
		'is_public': True,
		'property_id': 1,
		'property_label': 'Title',
		'type': 'literal'
 	}
	'''

	def __init__(self, repo, value_json):

		# store repo
		self.repo = repo

		# store json
		self.json = value_json


	def __repr__(self, tlen=50):

		if self.value != None:
			value_repr = self.value[:tlen] + '..' if len(self.value) > tlen else self.value
		else:
			value_repr = None

		return '<Value: "%s">' % (value_repr)


	@property
	def value(self):
		return self.json.get('@value', None)


	@property
	def property_label(self):
		return self.json.get('property_label')


	@property
	def property_id(self):
		return self.json.get('property_id', None)


	@property
	def property(self):

		'''
		Property to return Property instance associated with Value
		'''

		# query
		response = self.repo.api.get('properties', params={'id':self.property_id})

		if response.status_code == 200:

			return Property(self.repo, response.json())



class Vocabulary(object):

	'''
	Class to represent Omeka-S Vocabulary
	'''

	def __init__(self, repo, vocab_json):

		# store repository instance
		self.repo = repo

		# store json
		self.json = vocab_json


	@property
	def id(self):
		return self.json.get('o:id')


	@property
	def uri(self):
		return self.json.get('@id')


	@property
	def uri(self):
		return self.json.get('o:namespace_uri')


	@property
	def prefix(self):
		return self.json.get('o:prefix')


	@property
	def label(self):
		return self.json.get('o:label')


	@property
	def comment(self):
		return self.json.get('o:comment')


	def __repr__(self):

		return '<Vocabulary: #%s, %s, prefix:%s, uri:%s>' % (self.id, self.label, self.prefix, self.uri)


	def get_properties(self):

		'''
		Method to return all associated Properties
			- query /properties endpoint, searching by vocab id

		Returns:
			generator
		'''

		# api GET request
		response = self.repo.api.get('properties', params={'vocabulary_id':self.id})

		# return
		if response.status_code == 200:

			# parse JSON
			response = response.json()

			# yield
			for property_json in response:
				yield Property(self.repo, property_json)


	def get_property(self, term):

		'''
		Method to return property

		Args:
			term (str): term, with or without Vocabulary namespace prefex
		'''

		# remove prefix if added
		if self.prefix in term:
			term = term.split('%s:')[-1]

		# api GET request
		response = self.repo.api.get('properties', params={'vocabulary_id':self.id, 'local_name':term})

		# return
		if response.status_code == 200:

			# should only be one, confirm and return
			properties = response.json()

			if len(properties) == 1:
				return Property(self.repo, properties[0])

			else:
				raise Exception('only expecting on property for this vocabulary for term: %s' % term)























