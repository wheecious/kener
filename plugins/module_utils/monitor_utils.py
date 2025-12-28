""" 
This file contains functions for the wheecious.kener.monitor module
"""

required_fields = {
    'API': ['url', 'method', 'timeout'],
    'SSL': ['host', 'port', 'degradedRemainingHours', 'downRemainingHours'],
    'DNS': ['lookupRecord', 'nameServer', 'matchType', 'values']
}

def build_payload(module):
    params = module.params
    monitor_type = params['monitor_type']
    payload = {
        'name': params['name'],
        'tag': params['tag'],
        'status': params['status'],
        'cron': params['cron'],
        'category_name': params['category_name'],
        'monitor_type': params['monitor_type'],
    }
    if params['monitor_type'] == 'TCP' or params['monitor_type'] == 'PING':
        payload['type_data'] = {
            'hosts': params['hosts']
        }
    elif monitor_type in required_fields:
        for field in required_fields[monitor_type]:
            if not params['monitor'].get(field):
                module.fail_json(msg=f'{field} is required for {monitor_type}')
        payload['type_data'] = params['monitor']
    return payload