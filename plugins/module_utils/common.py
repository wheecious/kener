""" 
This file contains common functions for the wheecious.kener collection
"""

from ansible.module_utils.urls import fetch_url
import json

def make_api_request(module, method, endpoint, data=None):
    """Make HTTP request to Kener API"""
    api_url = module.params['api_url'].rstrip('/')
    api_key = module.params['api_key']

    url = f'{api_url}{endpoint}'

    headers ={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'}
    body = None

    if data:
        body = json.dumps(data)

    response, info = fetch_url(
        module, url, data=body, headers=headers, method=method)

    if info['status'] >= 400:
        module.fail_json(msg=f'API error: {info['status']}')

    if response:
        return json.loads(response.read())
    return None

def is_changed(params, existing_params):
    for param in params:
        existing_param = existing_params[param]
        if param == 'type_data':
            # TODO parse type_data even if null
            existing_param = json.loads(existing_params['type_data'])
        if params[param] != existing_param:
            return True
    return False