import requests

url = 'https://bankid-services.statuspage.io/'
header = {'Accept': 'application/json'}
response = {'Error': 'Couldnt retrieve data from statuspages.'}

r = requests.get(url, headers=header)
print(r)



