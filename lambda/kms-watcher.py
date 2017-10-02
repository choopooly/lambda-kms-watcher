from __future__ import print_function

import json
import re
from botocore.vendored import requests


url = 'https://salt-api:8000'
user = 'USER'
password = 'PASS'

# Regex to filter the dynamo ID you want to watch
filter = 'dynamodb_id'


def lambda_handler(event, context):
    """Initialize lambda main function."""
    print('Loading function')
    print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        keys = record['dynamodb']['Keys']
        print(keys)
        if 'name' in keys:
            print('received keys:' + json.dumps(keys['name'], indent=2))
            if 'S' in keys['name']:
                print('Received S: ' + json.dumps(keys['name']['S'], indent=2))
                if re.match(filter, keys['name']['S']):
                    print('we found occurence for: ' + filter)
                else:
                    print('No match for: ' + filter)
            else:
                print('No match for S in: ' + json.dumps(keys['name'], indent=2))
        else:
            print('No match for name in: Keys')

        print('Successfully processed {} records.'.format(len(event['Records'])))
        return trigger()


def get_token():
    """Get salt-api authentication token."""
    print('fetching token...')
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})

    payload = {
        "username": user,
        "password": password,
        "eauth": "pam"
    }

    try:
        response = s.post(url + "/login", data=payload, timeout=5)
    except requests.ConnectionError:
        raise ValueError("salt-api is unreachable: {}".format(url))

    print('response code: %s' % response.status_code)

    if response.status_code == 401:
        msg = "Could not authenticate salt-api."
        raise ValueError(msg)

    result = json.loads(response.text)
    if result:
        print('Got token.')
        token = result['return'][0]['token']
        return token


def request(uri='', method='POST', data=None):
    """Request salt-api webhook."""
    token = get_token()

    print('sending request...')
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    s.headers.update({"X-Auth-Token": token})

    try:
        if method == 'POST':
            res = s.post(url + uri, data=data)
        elif method == 'GET':
            res = s.get(url + uri)
    except requests.ConnectionError:
        raise ValueError("salt-api is unreachable: {}".format(url))

    print(res.status_code)
    try:
        return json.loads(res.text)
    except ValueError:
        msg = "Get non-json result from salt-api: %s" % res.text
        raise RuntimeError(msg)


def trigger():
    """Trigger salt-api call."""
    data = {'foo': 'bar'}
    return request('/hook/trigger', data=data)
