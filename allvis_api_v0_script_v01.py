import pathlib
import json
import copy
import pprint
import requests
from datetime import datetime
import pytz
from pymongo import MongoClient

###################################
#### Global settings ##############
###################################

TIMEZONE = 'Europe/Oslo'


###################################
#### Allvis API settings ##########
###################################

# Credentials provided by NSM Allvis
API_ID = 'id'
API_KEY = 'key'

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
SAVE_TO_JSON = False
JSON_OUTPUT_FILENAME = 'allvis-results.json'

# Save to Azure Cosmos MongoDB-API
SAVE_TO_AZURE_COSMOS_MONGODB = False
COSMOS_USER_NAME = 'user'
COSMOS_PASSWORD = 'pass'
COSMOS_URL = 'url:10255/?ssl=true&replicaSet=globaldb&retrywrites=false'

###################################
##### CODE ########################
###################################

### Functions

def getTime():
  tz = pytz.timezone(TIMEZONE)
  dateTimeObj = datetime.now(tz)
  return dateTimeObj.isoformat()

def checkIfOutputIsSet():
  if PRINT_TO_CONSOLE or SAVE_TO_JSON or SAVE_TO_AZURE_COSMOS_MONGODB:
    return True
  else:
    return False

def getOrgs(apiid, apikey):
  fullUrl = API_URL + '/' + API_BASEPATH + '/org'
  print('Requesting organisations at endpoint ' + fullUrl)
  
  try:
    res = requests.get(fullUrl, auth=(apiid, apikey))
  except requests.exceptions.RequestException as e:  # This is the correct syntax
    raise SystemExit(e)
  
  dictRes = json.loads(res.text)
  return dictRes

def getResults():
  results = dict()
  
  # Create timestamp
  results['timestamp'] = getTime()
    
  # Get organisations
  orgs = getOrgs(API_ID, API_KEY)
  print('Number of organisations found: ' + str(len(orgs)))

  if "error" in orgs:
    if orgs['error'] == "Unauthorized":
      errorMsg = {"component": "Allvis API", "issue": "Authentication failure. Is API ID and key configured and valid?", "errorMessage": orgs['error'],}
      results['error'] = errorMsg
      return results
    else:
      results['error'] = orgs
      return results

  results['results'] = {}
  
  for o in orgs:
    results['results'][o['id']] = dict(org=o)
    print('Fetching results for organiasation with id \'' + o['id'] + '\'')

    for ep in API_ENDPOINTS:
      res = fetchEndpointFromApi(o['id'], API_ID, API_KEY, API_ENDPOINTS[ep])
      jsonRes = json.loads(res.text)
      results['results'][o['id']][ep] = jsonRes
  
  return results

def fetchEndpointFromApi(orgid, apiid, apikey, ep):
  fullUrl = API_URL + '/' + API_BASEPATH + '/org/'+ orgid + '/' + ep
  print('Requesting endpoint: ' + fullUrl)
  
  try:
    res = requests.get(fullUrl, auth=(apiid, apikey))
  except requests.exceptions.RequestException as e:  # This is the correct syntax
    raise SystemExit(e)

  return res
  
def writeToFile(res, fname):
  with open(fname, 'w') as outfile:
    print('Storing JSON file to ' + str(pathlib.Path(fname).absolute()))
    json.dump(res, outfile)

def checkServerStatus(client):
  db = client.admin
  
  try:
    server_status = db.command('serverStatus')
  except Exception as e:
    raise SystemExit(e)
  print('Outputting to Azure Cosmos DB (MongoDB API)')
  print('Checking database server status:')
  print(json.dumps(server_status, sort_keys=False, indent=2, separators=(',', ': ')))

def outputToMongoDb(results, dbClient):
  print('Storing to database...')
  for org, data in results['results'].items():
    myDb = dbClient[org]
    for ep, content in data.items():
      contentCopy = copy.deepcopy(content)
      contentCopy['timestamp'] = results['timestamp']
      myCol = myDb[ep]
      try: 
        myCol.insert(contentCopy)
      except Exception as e:
        raise SystemExit(e)

def outputResults(results):
  if PRINT_TO_CONSOLE or 'error' in results:
    if 'error' in results:
      print('ERROR!')
    else:
      print('Outputting to console...')
    
    pprint.pprint(results)

  if 'error' not in results:
    if SAVE_TO_JSON:
      writeToFile(results, JSON_OUTPUT_FILENAME)

    if SAVE_TO_AZURE_COSMOS_MONGODB:
      uri = f'mongodb://{COSMOS_USER_NAME}:{COSMOS_PASSWORD}@{COSMOS_URL}'
      mongo_client = MongoClient(uri)
      checkServerStatus(mongo_client)
      outputToMongoDb(results, mongo_client)

### Main

print('NSM Allvis API script started (' + getTime() + ')')

if checkIfOutputIsSet(): 
  outputResults(getResults())
  print('Mission complete!')
else:
  print('Error: No outputs are enabled! Check settings in code.')
