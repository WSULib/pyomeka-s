# pyomeka-s
Python client for Omeka-S

## Installation and Setup

Clone repository and navigate to:
```
git clone https://github.com/WSULib/pyomeka-s
cd pyomeka-s
```

Install requirements:
```
pip install -r requirements.txt
```

Copy config template to home directory and add credentials:
```
cp pyomeka-s.json.template ~/pyomeka-s.json
```

## Reading

Import:
```
from models import *
```

Instantiate repository instance, using API endpoint and credentials from `~/pyomeka-s.json`:
```
repo = Repository()
```

Retrieve 5 Items from Repository intsance as generator:
```
for item in repo.get_items(per_page=5):
    print(item)

>> <Item: #2, "La Princesse du pays de la porcelaine (The Princess from the Land of Porcelain)">
<Item: #2734, "From Life, Christina Spartali">
<Item: #2735, "Charles Lang Freer to Rosalind Birnie Phillip, Dec. 9, 1903">
<Item: #3067, "Frame and register door for slow combustion stove.">
<Item: #3068, "Harmony in Blue and Gold: The Peacock Room">
```

Get single Item:
```
item = repo.get_item(3089) 

>> <Item: #3089, "Tea bowl">
```

Get Properties for Item, ignoring internal Omeka-S identifiers, returning list of Value instances:
```
item.get_properties()

>> {'dcterms:contributor': [<Value: "Gift of Charles Lang Freer">,
  <Value: "Yamanaka and Co.">],
 'dcterms:coverage': [<Value: "2">,
  <Value: "15">,
  <Value: "North">,
  <Value: "Edo period">,
  <Value: "Japan">,
  <Value: "United States">,
  <Value: "New York">,
  <Value: "New York">],
 'dcterms:date': [<Value: "18th-19th century">],
 'dcterms:description': [<Value: "Tea bowl">,
  <Value: "Freer purchased this Japanese tea bowl from the Ne..">],
 'dcterms:format': [<Value: "Stoneware with ash glaze">,
  <Value: "Possibly Hagi ware">,
  <Value: "HxW: 10.4 x 11.6 cm">],
 'dcterms:identifier': [<Value: "F1897.68">],
 'dcterms:title': [<Value: "Tea bowl">]}
```

Get single Property returning list of Value instances:
```
item.get_property('dcterms:format')

>> [<Value: "Stoneware with ash glaze">,
 <Value: "Possibly Hagi ware">,
 <Value: "HxW: 10.4 x 11.6 cm">]
```

Drilling to a single Value of a Property, can navigate back up through Property and Vocabulary:
```

# take first value from dcterms:format
val = item.get_property('dcterms:format')[0]

# look at Value content
val.value

>> 'Stoneware with ash glaze'

# use .property method to return instance of Property
val.property

>> <Property: #9, dcterms:format, "Format">

# use .vocbulary from property instance
val.property.vocabulary

>> <Vocabulary: #1, Dublin Core, prefix:dcterms, uri:http://purl.org/dc/terms/>

# show all properties from parent Property --> Vocabulary
list(val.property.vocabulary.get_properties())

>> [<Property: #1, dcterms:title, "Title">,
 <Property: #2, dcterms:creator, "Creator">,
 <Property: #3, dcterms:subject, "Subject">,
 <Property: #4, dcterms:description, "Description">,
 <Property: #5, dcterms:publisher, "Publisher">,
 <Property: #6, dcterms:contributor, "Contributor">,
 <Property: #7, dcterms:date, "Date">,
 <Property: #8, dcterms:type, "Type">,
 <Property: #9, dcterms:format, "Format">,
 <Property: #10, dcterms:identifier, "Identifier">,
 <Property: #11, dcterms:source, "Source">,
 <Property: #12, dcterms:language, "Language">,
 <Property: #13, dcterms:relation, "Relation">,
 <Property: #14, dcterms:coverage, "Coverage">,
 <Property: #15, dcterms:rights, "Rights">,
 <Property: #16, dcterms:audience, "Audience">,
 <Property: #17, dcterms:alternative, "Alternative Title">,
 <Property: #18, dcterms:tableOfContents, "Table Of Contents">,
 <Property: #19, dcterms:abstract, "Abstract">,
 <Property: #20, dcterms:created, "Date Created">,
 <Property: #21, dcterms:valid, "Date Valid">,
 <Property: #22, dcterms:available, "Date Available">,
 <Property: #23, dcterms:issued, "Date Issued">,
 <Property: #24, dcterms:modified, "Date Modified">,
 <Property: #25, dcterms:extent, "Extent">]
```

## Writing

Add new value for Dublin Core `format` to local Item instance (not yet writing to Omeka-S repository):
```
# add property
item.add_property('dcterms:format','very, very shiny')

# check added
item.get_property('dcterms:format')

>> [<Value: "Stoneware with ash glaze">,
 <Value: "Possibly Hagi ware">,
 <Value: "HxW: 10.4 x 11.6 cm">,
 <Value: "very, very shiny">]
```

Now, write to repository:
```
item.update()

>> True
```

To remove a Property value, provide Property instance *or* qualified term, and value:
```
# remove property
item.remove_value('dcterms:format','very, very shiny')

# update
item.update()

>> True
```

Refresh item from Omeka-S repository:
```
item.refresh()
```

## Versioning

There is extremely limited versioning occurring as Items are loaded, refreshed, and written to Omeka-S repository.

Load item from repository:
```
# load item
item = repo.get_item(10421)

# observe versions, noting initial v0
item.versions

>> {0: {'@context': 'http://example.com/api-context',
  '@id': 'http://example.com/api/items/10421',
  '@type': 'o:Item',
  'dcterms:coverage': [{'@value': 'pleated',
    'is_public': True,
    'property_id': 14,
    'property_label': 'Coverage',
    'type': 'literal'}],
  'dcterms:description': [{'@value': 'This is a test item, nothing more.',
    'is_public': True,
    'property_id': 4,
    'property_label': 'Description',
    'type': 'literal'}],
  'dcterms:extent': [{'@value': '75ft.',
    'is_public': True,
    'property_id': 25,
    'property_label': 'Extent',
    'type': 'literal'}],
  'dcterms:title': [{'@value': 'Test Item 1',
    'is_public': True,
    'property_id': 1,
    'property_label': 'Title',
    'type': 'literal'}],
  'o:created': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:id': 10421,
  'o:is_public': True,
  'o:item_set': [],
  'o:media': [],
  'o:modified': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:owner': {'@id': 'http://example.com/api/users/1', 'o:id': 1},
  'o:resource_class': None,
  'o:resource_template': None,
  'o:thumbnail': None}}
```

If we refresh, the Item is automatically versioned:
```
item.refresh()
item.versions

>> {0: {'@context': 'http://example.com/api-context',
  '@id': 'http://example.com/api/items/10421',
  '@type': 'o:Item',
  'dcterms:coverage': [{'@value': 'pleated',
    'is_public': True,
    'property_id': 14,
    'property_label': 'Coverage',
    'type': 'literal'}],
  'dcterms:description': [{'@value': 'This is a test item, nothing more.',
    'is_public': True,
    'property_id': 4,
    'property_label': 'Description',
    'type': 'literal'}],
  'dcterms:extent': [{'@value': '75ft.',
    'is_public': True,
    'property_id': 25,
    'property_label': 'Extent',
    'type': 'literal'}],
  'dcterms:title': [{'@value': 'Test Item 1',
    'is_public': True,
    'property_id': 1,
    'property_label': 'Title',
    'type': 'literal'}],
  'o:created': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:id': 10421,
  'o:is_public': True,
  'o:item_set': [],
  'o:media': [],
  'o:modified': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:owner': {'@id': 'http://example.com/api/users/1', 'o:id': 1},
  'o:resource_class': None,
  'o:resource_template': None,
  'o:thumbnail': None},
 1: {'@context': 'http://example.com/api-context',
  '@id': 'http://example.com/api/items/10421',
  '@type': 'o:Item',
  'dcterms:coverage': [{'@value': 'pleated',
    'is_public': True,
    'property_id': 14,
    'property_label': 'Coverage',
    'type': 'literal'}],
  'dcterms:description': [{'@value': 'This is a test item, nothing more.',
    'is_public': True,
    'property_id': 4,
    'property_label': 'Description',
    'type': 'literal'}],
  'dcterms:extent': [{'@value': '75ft.',
    'is_public': True,
    'property_id': 25,
    'property_label': 'Extent',
    'type': 'literal'}],
  'dcterms:title': [{'@value': 'Test Item 1',
    'is_public': True,
    'property_id': 1,
    'property_label': 'Title',
    'type': 'literal'}],
  'o:created': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:id': 10421,
  'o:is_public': True,
  'o:item_set': [],
  'o:media': [],
  'o:modified': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:owner': {'@id': 'http://example.com/api/users/1', 'o:id': 1},
  'o:resource_class': None,
  'o:resource_template': None,
  'o:thumbnail': None}}
```

If we add a new property `dcterms:source`, and remove `dcterms:extent`, then `.update()` to write to repository, we can observe there is a new version *after* the update:
```
item.add_property('dcterms:source','the void')
item.remove_value('dcterms:extent','75ft.')
item.update()

>> DEBUG:models:writing item v2

# checking versions, where post .update() created v2
item.versions

>> {0: {...},
 1: {...},
 2: {'@context': 'http://157.230.141.100/graham/api-context',
  '@id': 'http://157.230.141.100/graham/api/items/10421',
  '@type': 'o:Item',
  'dcterms:coverage': [{'@value': 'pleated',
    'is_public': True,
    'property_id': 14,
    'property_label': 'Coverage',
    'type': 'literal'}],
  'dcterms:description': [{'@value': 'This is a test item, nothing more.',
    'is_public': True,
    'property_id': 4,
    'property_label': 'Description',
    'type': 'literal'}],
  'dcterms:source': [{'@value': 'the void',
    'is_public': True,
    'property_id': 11,
    'property_label': 'Source',
    'type': 'literal'}],
  'dcterms:title': [{'@value': 'Test Item 1',
    'is_public': True,
    'property_id': 1,
    'property_label': 'Title',
    'type': 'literal'}],
  'o:created': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:41:20+00:00'},
  'o:id': 10421,
  'o:is_public': True,
  'o:item_set': [],
  'o:media': [],
  'o:modified': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
   '@value': '2019-01-18T19:45:32+00:00'},
  'o:owner': {'@id': 'http://157.230.141.100/graham/api/users/1', 'o:id': 1},
  'o:resource_class': None,
  'o:resource_template': None,
  'o:thumbnail': None}}
```



