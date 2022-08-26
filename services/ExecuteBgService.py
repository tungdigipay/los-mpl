from multiprocessing.dummy import Pool
import requests, configparser

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['EXE-BG']
base_url = config['base_url']

def prescore(uniqueID):
    pool = Pool(1)
    pool.apply_async(requests.get, [f'{base_url}/applications/prescore?uniqueID={uniqueID}'])

def score(uniqueID):
    pool = Pool(1)
    pool.apply_async(requests.get, [f'{base_url}/applications/score?uniqueID={uniqueID}'])

def scoring_log(uniqueID):
    pass

def postback(uniqueID):
    pool = Pool(1)
    pool.apply_async(requests.get, [f'{base_url}/postback/status?uniqueID={uniqueID}'])

def delivery(uniqueID, action):
    pool = Pool(1)
    pool.apply_async(requests.get, [f'{base_url}/delivery/{action}?uniqueID={uniqueID}'])

def activition(uniqueID):
    pool = Pool(1)
    pool.apply_async(requests.get, [f'{base_url}/activition/process/?uniqueID={uniqueID}'])