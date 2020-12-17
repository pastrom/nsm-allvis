import pathlib
import json
import pprint
import requests

###################################
#### Allvis API config ############
###################################

# Credentials provided by NSM Allvis
API_ID = 'apiid'
API_KEY = 'apikey'

# URL
API_URL = 'https://api.allvis.no'

# API basePath
API_BASEPATH = 'v0'

# API endpoints 
API_ENDPOINTS = dict(orgInfo='', nets='groups', services='services', contacts='contacts')


###################################
##### Output settings #############
###################################

# Pretty print results to console? (True/False)
PRINT_TO_CONSOLE = False 

# Save results to JSON-file (True/False)
SAVE_TO_JSON = True
JSON_OUTPUT_FILENAME = 'allvis-results.json'


###################################
##### CODE ########################
###################################

# Functions

def getOrgs(id, key):
  fullUrl = API_URL + '/' + API_BASEPATH + '/org'
  print('Requesting organisations at endpoint ' + fullUrl)
  res = requests.get(fullUrl, auth=(id, key))
  dictRes = json.loads(res.text)
  return dictRes

def fetchResultsFromApi(orgid, apiid, apikey, ep):
  fullUrl = API_URL + '/' + API_BASEPATH + '/org/'+ orgid + '/' + ep
  print('Requesting endpoint: ' + fullUrl)
  return requests.get(fullUrl, auth=(apiid, apikey))
  
def writeToFile(res, fname):
  with open(fname, 'w') as outfile:
    print('Storing JSON file to ' + str(pathlib.Path(fname).absolute()))
    json.dump(res, outfile)

# main

print('NSM Allvis API script started.')

if PRINT_TO_CONSOLE or SAVE_TO_JSON: 

  allData = dict()

  orgs = getOrgs(API_ID, API_KEY)
  print('Number of organisations found: ' + str(len(orgs)))

  for o in orgs:
    allData[o['id']] = dict(org=o)
   
    print('Fetching results for organiasation with id \'' + o['id'] + '\'')

    for ep in API_ENDPOINTS:
      res = fetchResultsFromApi(o['id'], API_ID, API_KEY, API_ENDPOINTS[ep])
      jsonRes = json.loads(res.text)
      allData[o['id']][ep] = jsonRes
    
  if PRINT_TO_CONSOLE:
    print('Outputting to console...')
    pprint.pprint(allData)
    
  if SAVE_TO_JSON:
    writeToFile(allData, JSON_OUTPUT_FILENAME)

  print('Mission complete!')
  
else:
  print('Error: No outputs are enabled! Check settings in code.')
  