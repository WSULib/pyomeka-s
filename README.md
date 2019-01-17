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

Retrieve 5 items as generator
```
for item in repo.get_items(per_page=5):
    print(item.id)

1
2
3
4
5
```

Get item:
```
```

Get item property `dcterms:title`:
```
```

