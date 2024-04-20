from requests import get
from pprint import pprint

pprint(get('http://localhost:5000/api/users').json())

pprint(get('http://localhost:5000/api/users/1').json())

pprint(get('http://localhost:5000/api/users/999').json())



pprint(get('http://localhost:5000/api/products').json())

pprint(get('http://localhost:5000/api/products/1').json())

pprint(get('http://localhost:5000/api/products/999').json())