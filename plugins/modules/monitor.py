#!/usr/bin/python

DOCUMENTATION = r'''
---
module: monitor
short_description: Manage Kener status page monitors
description:
    - Create, update, or delete monitors in Kener
    - Supports API, TCP, PING, DNS, and SSL monitor types
version_added: "0.0.1"
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
    idempotent:
        support: full
        details:
            - Before making any changes, the module checks if there's already a monitor with the tag we specified in our playbook. If yes, it gathers the monitor's values via an API request to Kener, and then compares the values we pass to the existing ones. If they differ, new values apply.
options:
    api_url:
        description:
            - Kener API URL
            - Should include protocol (http:// or https://)
        required: true
        type: str
    api_key:
        description:
            - API key for authentication
            - Can be generated in Kener admin panel
        required: true
        type: str
    tag:
        description:
            - Unique identifier for the monitor
            - Used for idempotent operations
        required: true
        type: str
    name:
        description: Display name of the monitor
        type: str
        default: 'Kener Monitor'
    state:
        description:
            - Desired state of the monitor
            - C(present) creates or updates the monitor
            - C(absent) deletes the monitor
        type: str
        choices: [ present, absent ]
        default: present
    status:
        description:
            - Monitor status
            - C(ACTIVE) enables monitoring
            - C(PAUSED) disables monitoring without deletion
        type: str
        choices: [ ACTIVE, PAUSED ]
        default: ACTIVE
    cron:
        description:
            - Cron expression for monitor execution schedule
            - Minimum interval is one minute
        type: str
        default: "* * * * *"
    category_name:
        description:
            - Category for grouping monitors in UI
            - Category must exist in Kener
        type: str
        default: Home
    monitor_type:
        description: Type of monitor to create
        type: str
        choices: [ API, TCP, PING, SSL, DNS ]
        default: PING
        required: true
    validate_certs:
        description: Validate SSL certificates for API requests
        type: bool
        default: true
    hosts:
        description:
            - List of hosts to monitor
            - Required for TCP and PING monitor types
        type: list
        elements: dict
        suboptions:
            host:
                description: Hostname, IP address, or domain name
                type: str
                required: true
            port:
                description:
                    - Port number to check
                    - Required for TCP monitors
                type: int
            type:
                description: Type of host address
                type: str
                choices: [ IP4, IP6, DOMAIN ]
                default: IP4
            timeout:
                description: Timeout in milliseconds
                type: int
                default: 3000
            count:
                description:
                    - Number of ping attempts
                    - Required for PING monitors
                type: int
    monitor:
        description:
            - Monitor configuration dictionary
            - Required for API, SSL, and DNS monitor types
            - Fields required depend on I(monitor_type)
        type: dict
        suboptions:
            url:
                description:
                    - URL to monitor
                    - Required for API monitors
                type: str
            method:
                description:
                    - HTTP method for API requests
                    - Required for API monitors
                type: str
            timeout:
                description:
                    - Request timeout in milliseconds
                    - Required for API monitors
                type: int
            host:
                description:
                    - Hostname or IP address
                    - Required for SSL and DNS monitors
                type: str
            port:
                description:
                    - Port number for SSL connection
                    - Required for SSL monitors
                type: int
            degradedRemainingHours:
                description:
                    - Hours before certificate expiry to mark as DEGRADED
                    - Required for SSL monitors
                type: int
            downRemainingHours:
                description:
                    - Hours before certificate expiry to mark as DOWN
                    - Required for SSL monitors
                type: int
            lookupRecord:
                description:
                    - DNS record type to query
                    - Required for DNS monitors
                type: str
                choices: [ A, AAAA, CNAME, MX, TXT, NS, SOA, PTR ]
            nameServer:
                description:
                    - DNS server to query
                    - Required for DNS monitors
                type: str
            matchType:
                description:
                    - How to match expected values
                    - C(ANY) passes if any value matches
                    - C(ALL) requires all values to match
                    - C(NONE) passes if no values match
                    - Required for DNS monitors
                type: str
                choices: [ ANY, ALL, NONE ]
            values:
                description:
                    - Expected DNS resolution values
                    - Required for DNS monitors
                type: list
                elements: str
requirements:
    - Kener API v3.2+
author:
    - wheecious (@wheecious)
'''

EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - name: Delete monitor
      wheecious.kener.monitor:
        api_url: "http://localhost:3000"
        api_key: "supersecret_api_key"
        tag: 'ping-prod-DO-NOT-DELETE'
        state: 'absent'
        hosts: [] # need this for now; gotta get rid of it in future versions

    - name: API monitor
      wheecious.kener.monitor:
        api_url: "http://localhost:3000"
        api_key: "supersecret_api_key"
        tag: "node-exporter-api-endpoint"
        name: "API request to :9100/metrics"
        category_name: "Home"
        monitor_type: "API"
        cron: "* * * * *"
        monitor:
          url: "localhost:9100/metrics"
          method: 'GET'
          timeout: 3000

    - name: TCP monitor
      wheecious.kener.monitor:
        api_url: "http://localhost:3000"
        api_key: "supersecret_api_key"   
        tag: 'poke-ssh-localhost'
        name: "22 @ localhost"
        category_name: "Home"
        monitor_type: 'TCP'
        hosts:
          - host: '127.0.0.1'
            port: 22
            type: 'IP4'
            timeout: 3000

    - name: PING monitor
      wheecious.kener.monitor:
        api_url: "http://localhost:3000"
        api_key: "supersecret_api_key"
        tag: 'gateway-ping'
        name: 'ping router'
        category_name: 'Home'
        monitor_type: 'PING'
        hosts:
          - host: '192.168.0.1'
            timeout: 3000
            type: 'IP4'
            count: 4

    - name: SSL monitor
      wheecious.kener.monitor:
        api_url: "http://localhost:3000"
        api_key: "supersecret_api_key"
        tag: 'google-ssl'
        name: 'google.com SSL'
        category_name: 'Home'
        monitor_type: 'SSL'
        monitor:
          host: "google.com"
          port: 443
          degradedRemainingHours: 168
          downRemainingHours: 24

    - name: DNS monitor
      wheecious.kener.monitor:
        api_url: "http://localhost:3000"
        api_key: "supersecret_api_key"
        tag: "google-resolve"
        name: "google.com A record"
        category_name: "Hone"
        monitor_type: "DNS"
        monitor:
          host: "google.com"
          lookupRecord: "A"
          nameServer: "8.8.8.8"
          matchType: "ANY"
          values:
            - "142.251.140.14"
'''

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.wheecious.kener.plugins.module_utils.common import (
    make_api_request,
    is_changed
)

from ansible_collections.wheecious.kener.plugins.module_utils.monitor_utils import (
    build_payload,
    required_fields
)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            api_url = dict(type='str', required=True),
            api_key = dict(type='str', required=True, no_log=True),
            validate_certs = dict(type='bool', default=True),
            name = dict(type='str', default='Kener Monitor'),
            state = dict(type='str', default='present'),
            status = dict(type='str', default='ACTIVE'),
            tag = dict(type='str', required=True),
            cron = dict(type='str', default="* * * * *"),
            category_name = dict(type='str', default='Home'),
            monitor_type = dict(type='str', choices=['API', 'TCP', 'PING', 'SSL', 'DNS'], default='PING'),
            hosts = dict(
                type='list',
                elements='dict',
                options=dict(
                    host=dict(type='str', required=True),
                    port=dict(type='int'),
                    type=dict(type='str', choices=['IP4', 'IP6', 'DOMAIN'], default='IP4'),
                    timeout=dict(type='int', default=3000),
                    count=dict(type='int')
                )
            ),
            monitor=dict(
                type='dict',
                default={},
                options=dict(
                    # API
                    url=dict(type='str'),
                    method=dict(type='str'),
                    timeout=dict(type='int'),

                    # SSL and DNS
                    host=dict(type='str'),

                    # SSL
                    port=dict(type='int'),
                    degradedRemainingHours=dict(type='int'),
                    downRemainingHours=dict(type='int'),

                    # DNS
                    lookupRecord=dict(
                        type='str',
                        choices=['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SOA', 'PTR']
                    ),
                    nameServer=dict(type='str'),
                    matchType=dict(
                        type='str',
                        choices=['ANY', 'ALL', 'NONE']
                    ),
                    values=dict(
                        type='list', elements='str',
                    )
                )
            )
        ),
        required_if=[
            ('monitor_type', 'TCP', ['hosts']),
            ('monitor_type', 'PING', ['hosts']),
            ('monitor_type', 'API', ['monitor']),
            ('monitor_type', 'SSL', ['monitor']),
            ('monitor_type', 'DNS', ['monitor']),
        ],
        supports_check_mode=False
    )

    state = module.params['state']
    payload = build_payload(module.params)
    if state == 'present':
        existing = make_api_request(module, 'GET', f'/api/monitor?tag={payload["tag"]}')
        if existing:
            if is_changed(payload, existing[0]):
                payload['id'] = existing[0]["id"]
                result = make_api_request(
                    module, 'PUT', f'/api/monitor/{existing[0]["id"]}',
                    data=payload)
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False, msg=f'Monitor {payload["tag"]} with the same parameters already exists')
        else:
            result = make_api_request(
                module, 'POST', '/api/monitor', data=payload)
            module.exit_json(changed=True, msg=result)
    elif state == "absent":
        existing = make_api_request(module, 'GET', f'/api/monitor?tag={payload["tag"]}')
        if existing:
            make_api_request(module, 'DELETE', f'/api/monitor/{existing[0]['id']}')
            module.exit_json(changed=True, msg=f'Monitor {payload['tag']} was removed')
        else:
            module.exit_json(changed=False, msg=f'No monitor {payload['tag']} found')

if __name__ == '__main__':
    main()