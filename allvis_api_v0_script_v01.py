import pathlib
import json
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
SAVE_TO_JSON = False

JSON_OUTPUT_FILENAME = 'allvis-results.json'

# Save to Azure Cosmos MongoDB-API (True/False)
SAVE_TO_AZURE_COSMOS_MONGODB = False

COSMOS_USER_NAME = "username"
COSMOS_PASSWORD = "pass"
COSMOS_URL = "URL:10255/?ssl=true&replicaSet=globaldb&retrywrites=false"

###################################
##### CODE ########################
###################################

# Functions

def getTime():
  tz = pytz.timezone(TIMEZONE)
  dateTimeObj = datetime.now(tz)
  return dateTimeObj.isoformat()

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

def check_server_status(client):
  db = client.admin
  server_status = db.command('serverStatus')
  print('Checking database server status:')
  print(json.dumps(server_status, sort_keys=False, indent=2, separators=(',', ': ')))

def outputToMongoDb(results, dbClient):
  print('Storing results to Azure Cosmos DB MongoDB API')
  for org, data in results['results'].items():
    myDb = dbClient[org]
    for ep, content in data.items():
      myCol = myDb[ep]
      myCol.insert_one(content)

# main

print('NSM Allvis API script started. (' + getTime() + ')')

if PRINT_TO_CONSOLE or SAVE_TO_JSON or SAVE_TO_AZURE_COSMOS_MONGODB: 
  results = dict()

  results['timeStamp'] = getTime()
  results['results'] = {}

  orgs = getOrgs(API_ID, API_KEY)

  print('Number of organisations found: ' + str(len(orgs)))

  for o in orgs:
    results['results'][o['id']] = dict(org=o)
   
    print('Fetching results for organiasation with id \'' + o['id'] + '\'')

    for ep in API_ENDPOINTS:
      res = fetchResultsFromApi(o['id'], API_ID, API_KEY, API_ENDPOINTS[ep])
      jsonRes = json.loads(res.text)
      results['results'][o['id']][ep] = jsonRes

  if PRINT_TO_CONSOLE:
    print('Outputting to console...')
    pprint.pprint(results)
    
  if SAVE_TO_JSON:
    writeToFile(results, JSON_OUTPUT_FILENAME)

  if SAVE_TO_AZURE_COSMOS_MONGODB:
        
    uri = f'mongodb://{cosmos_user_name}:{cosmos_password}@{cosmos_url}'
    mongo_client = MongoClient(uri)

    check_server_status(mongo_client)
    
    outputToMongoDb(results, mongo_client)
    
  print('Mission complete!')

else:
  print('Error: No outputs are enabled! Check settings in code.')
