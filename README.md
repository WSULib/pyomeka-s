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

## Use

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

<Item: #2, "La Princesse du pays de la porcelaine (The Princess from the Land of Porcelain)">
<Item: #2734, "From Life, Christina Spartali">
<Item: #2735, "Charles Lang Freer to Rosalind Birnie Phillip, Dec. 9, 1903">
<Item: #3067, "Frame and register door for slow combustion stove.">
<Item: #3068, "Harmony in Blue and Gold: The Peacock Room">
```

Get single Item:
```
item = repo.get_item(3089) 

<Item: #3089, "Tea bowl">
```

Get Properties for Item, ignoring internal Omeka-S identifiers, returning list of Value instances:
```
item.get_properties()

{'dcterms:contributor': [<Value: "Gift of Charles Lang Freer">,
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

[<Value: "Stoneware with ash glaze">,
 <Value: "Possibly Hagi ware">,
 <Value: "HxW: 10.4 x 11.6 cm">]
```

Drilling to a single Value of a Property, can navigate back up through Property and Vocabulary:
```

# take first value from dcterms:format
val = item.get_property('dcterms:format')[0]

# look at Value content
val.value

'Stoneware with ash glaze'

# use .property method to return instance of Property
val.property

<Property: #9, dcterms:format, "Format">

# use .vocbulary from property instance
val.property.vocabulary

<Vocabulary: #1, Dublin Core, prefix:dcterms, uri:http://purl.org/dc/terms/>

# show all properties from parent Property --> Vocabulary
list(val.property.vocabulary.get_properties())

[<Property: #1, dcterms:title, "Title">,
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













