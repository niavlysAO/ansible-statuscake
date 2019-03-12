#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.1'}

DOCUMENTATION = '''
---
module: statuscake_uptime
short_description: Manage StatusCake uptime tests
description:
    - Manage StatusCake uptime tests by using StatusCake REST API.
requirements:
  - "requests >= 2.18.0"
version_added: "2.2"
author: "Raphael Pereira Ribeiro (@raphapr)"
options:
  username:
    description:
      - StatusCake account username. Can also be supplied via $STATUSCAKE_USERNAME env variable.
    required: false
  api_key:
    description:
      - StatusCake API KEY. Can also be supplied via $STATUSCAKE_API_KEY env variable.
    required: false
  name:
    description:
      - Name of the test. It must be unique.
    required: false
  url:
    description:
      - Website URL, either an IP or a FQDN.
    required: false
  state:
    description:
      - Attribute that specifies if the test has to be created, deleted or a basic list of all tests.
    required: false
    default: present
    choices: ['present', 'absent', 'list']
  test_tags:
    description:
      - Website URL, either an IP or a FQDN.
    required: false
  check_rate:
    description:
  - The number of seconds between checks.
    default: 300
    required: false
  test_type:
    description:
      - Test type to use
    default: HTTP
    required: false
  port:
    description:
      - A Port to use on TCP Tests (mutually exclusive with tcp_type when it is TCP)
    required: false
  contact_group:
    description:
      - Contact group ID
    required: false
  paused:
    description:
      - 0 to unpause, 1 to pause the test.
    default: 0
    required: false
  node_locations:
    description:
      - Node locations ID separated by a comma
    required: false
  confirmation:
    description:
      - Alert delay rate
    default: 300
    required: false
  timeout:
    description:
      - Timeout in seconds
    default: 30
    required: false
  status_codes:
    description:
      - Comma separated list of status codes to trigger error on
    default: Standard codes
    required: false
  host:
    description:
      - Website host
    required: false
  custom_header:
    description:
      - Custom HTTP header supplied as JSON format
    required: false
  follow_redirect:
    description:
      - Enable (1) / disable (0) follow redirect
    default: 0
    required: false
  find_string:
    description:
      - A string that should either be found or not found.
    required: false
  do_not_find:
    description:
      - If the above string should be found to trigger a alert.
    default: 0
    required: false
  post_raw:
    description:
      - Use to populate the RAW POST data field on the test
    required: false
  basic_user:
    description:
      - A Basic Auth User account to use to login
    required: false
  basic_pass:
    description:
      - If BasicUser is set then this should be the password for the BasicUser
    required: false
'''

EXAMPLES = '''
---
- name: Create statuscake test
  statuscake:
    username: user
    api_key: api
    name: "MyWebSite"
    state: present
    url: "https://www.google.com"
    test_type: HTTP
    confirmation: 3
    paused: 0
    check_rate: 3
    status_codes: "204,205,206,303,400,401,403,404,405,406,408,410,413,444,429,494,495,496,499,500,501,502,503,504,505,506,507,508,509,510,511,521,522,523,524,520,598,599,301,302"
    timeout: 300
    test_tags: "Google, SSL"
    node_locations: "UG4,HRSM1,BR1,BR3"
    host: Google cloud
    contact_group: 0
    custom_header: ""
    follow_redirect: 0
    find_string: "/html>"
    do_not_find: 0
    post_raw: ""
    basic_user: "my_username"
    basic_pass: "my_password"

- name: List all statuscake tests
  statuscake:
    username: user
    api_key: api
    state: list
'''

RETURN = '''
---
name:
  description: Name of the StatusCake test.
  returned: success, when needed
  type: string
  sample: MyWebsite
state:
  description: State of the StatusCake test.
  returned: success, when needed
  type: string
  sample: present
response:
  description: HTTP response message of the request
  returned: success, when needed
  type: string
  type: string
  sample: "Test updated"
tests:
    description: List all tests.
    returned: success, when needed
    type: dictionary
    contains:
        output:
            description: Return a basic list of all tests
            returned: success
            type: dictionary
            sample: {"ContactGroup": ["0"], "NormalisedResponse": 0, "Paused": true, "Public": 0, "Status": "Up", "TestID": 2554887, "TestType": "HTTP", "Uptime": null, "WebsiteName": "MyWebsite"}
        count:
            description: Total number of tests
            returned: success
            type: int
            sample: 25
diff:
    description: Show the fields before and after each change
    returned: always
    type: dictionary
    contains:
        after:
            description: StatusCake fields after the test update.
            returned: success
            type: dictionary
            sample: { "confirmation": 300 }
        before:
            description: StatusCake fields before the test update.
            returned: success
            type: dictionary
            sample: { "confirmation": 200 }

'''

import requests
from ansible.module_utils.basic import *


class StatusCakeUptime:
    URL_UPDATE_TEST = "https://app.statuscake.com/API/Tests/Update"
    URL_ALL_TESTS = "https://app.statuscake.com/API/Tests"
    URL_DETAILS_TEST = "https://app.statuscake.com/API/Tests/Details"

    def __init__(self, module, username, api_key, name, url, state,
                 test_tags, check_rate, test_type, port, contact_group, paused,
                 node_locations, confirmation, timeout, status_codes, host,
                 custom_header, follow_redirect, find_string, do_not_find,
                 post_raw, basic_user, basic_pass):

        self.headers = {"Username": username, "API": api_key}
        self.module = module
        self.name = name
        self.url = url
        self.state = state
        self.test_tags = test_tags
        self.test_type = test_type
        self.contact_group = contact_group
        self.paused = paused
        self.node_locations = node_locations
        self.confirmation = confirmation
        self.timeout = timeout
        self.status_codes = status_codes
        self.host = host
        self.custom_header = custom_header
        self.follow_redirect = follow_redirect
        self.find_string = find_string
        self.do_not_find = do_not_find
        self.port = port
        self.post_raw = post_raw
        self.basic_user = basic_user
        self.basic_pass = basic_pass

        if not check_rate:
            self.check_rate = 300
        else:
            self.check_rate = check_rate

        if not test_type:
            self.test_type = "HTTP"
        else:
            self.test_type = test_type

        self.data = {"WebsiteName": self.name,
                     "WebsiteURL": self.url,
                     "CheckRate": self.check_rate,
                     "TestType": self.test_type,
                     "TestTags": self.test_tags,
                     "ContactGroup": self.contact_group,
                     "Paused": self.paused,
                     "NodeLocations": self.node_locations,
                     "Confirmation": self.confirmation,
                     "Timeout": self.timeout,
                     "StatusCodes": self.status_codes,
                     "WebsiteHost": self.host,
                     "FollowRedirect": self.follow_redirect,
                     "FindString": self.find_string,
                     "Port": self.port,
                     "DoNotFind": self.do_not_find,
                     "BasicUser": self.basic_user,
                     "BasicPass": self.basic_pass,
                     }

        if self.custom_header:
            self.data['CustomHeader'] = self.custom_header.replace("'", "\"")

        if self.post_raw:
            self.data['PostRaw'] = self.post_raw.replace("'", "\"")

        self.result = {
            'changed': False,
            'name': self.name,
            'state': self.state,
            'diff': {
                'before': {},
                'after': {}
            }
        }

    def get_all_tests(self):
        response = requests.get(self.URL_ALL_TESTS, headers=self.headers)
        del self.result['name']
        del self.result['state']
        self.result.update({'tests': {'output': response.json(),
                            'count': len(response.json())}})

    def check_response(self, response):
        self.result['response'] = response['Message']
        if response['Success']:
            self.result['changed'] = True
        elif not response['Message'].startswith('No data has been updated'):
            errormsg = response['Message']

            if response.get('Issues'):
                errormsg += ' '
                errormsg += ('; '.join("{0}: {1}".format(k, v)
                             for k, v in response['Issues'].items()))

            self.module.fail_json(msg=errormsg)

    def check_test(self):
        response = requests.get(self.URL_ALL_TESTS, headers=self.headers)

        for item in response.json():
            if item['WebsiteName'] == self.name:
                return item['TestID']

    def delete_test(self):
        test_id = self.check_test()

        if not test_id:
            self.result['response'] = "This Check doesn't exists"
        else:
            data = {'TestID': test_id}
            if self.module.check_mode:
                self.result['changed'] = True
                self.result['response'] = ("This Check Has Been Deleted. " +
                                           "It can not be recovered.")
            else:
                response = requests.delete(self.URL_DETAILS_TEST,
                                           headers=self.headers, data=data)
                self.check_response(response.json())

    def create_test(self):
        test_id = self.check_test()

        if not test_id:
            if self.module.check_mode:
                self.result['changed'] = True
                self.result['response'] = "Test inserted"
            else:
                response = requests.put(self.URL_UPDATE_TEST,
                                        headers=self.headers,
                                        data=self.data)
                self.check_response(response.json())
        else:
            self.data['TestID'] = test_id
            url_details_test = (self.URL_DETAILS_TEST +
                                "/?TestID=" +
                                str(test_id))
            response = requests.get(url_details_test, headers=self.headers)
            req_data = self.convert(response.json())
            diffkeys = ([k for k in self.data if self.data[k] and k in req_data and
                        str(self.data[k]) != str(req_data[k])])
            if self.module.check_mode:
                if len(diffkeys) != 0:
                    self.result['changed'] = True
                    self.result['response'] = "Test updated"
                else:
                    self.result['response'] = ("No data has been updated " +
                                               "(is any data different?) " +
                                               "Given: "+str(test_id))
            else:
                response = requests.put(self.URL_UPDATE_TEST,
                                        headers=self.headers,
                                        data=self.data)
                self.check_response(response.json())
            self.result['diff']['before'] = {k: req_data[k] for k in diffkeys}
            self.result['diff']['after'] = {k: self.data[k] for k in diffkeys}

    # convert data returned by request to a similar and comparable estruture
    def convert(self, req_data):
        req_data['WebsiteURL'] = req_data.pop('URI', None)
        req_data['TestTags'] = req_data.pop('Tags', None)
        req_data['ContactGroup'] = (req_data['ContactGroups'][0]['ID']
                                    if req_data['ContactGroup'] else None)
        req_data = ({k: req_data[k] for k in req_data.keys()
                    if k in self.data.keys()})
        for key in req_data.keys():
            if type(req_data[key]) is list:
                req_data[key] = [item.encode('UTF8') for item in req_data[key]]
                req_data[key] = ','.join(req_data[key])
            if type(req_data[key]) is unicode:
                req_data[key] = req_data[key].encode('UTF-8')
            if req_data[key] is True:
                req_data[key] = 1
            if req_data[key] is False:
                req_data[key] = 0
        return req_data

    def get_result(self):
        result = self.result
        return result


def run_module():

    module_args = dict(
        username=dict(type='str', required=False),
        api_key=dict(type='str', required=False),
        name=dict(type='str', required=False),
        url=dict(type='str', required=False),
        state=dict(choices=['absent', 'present', 'list'], default='present'),
        test_tags=dict(type='str', required=False),
        check_rate=dict(type='int', required=False),
        test_type=dict(type='str', required=False),
        port=dict(type='int', required=False),
        contact_group=dict(type='str', required=False),
        paused=dict(type='int', required=False),
        node_locations=dict(type='str', required=False),
        confirmation=dict(type='int', required=False),
        timeout=dict(type='int', required=False),
        status_codes=dict(type='str', required=False),
        host=dict(type='str', required=False),
        custom_header=dict(type='str', required=False),
        follow_redirect=dict(type='int', required=False),
        find_string=dict(type='str', required=False),
        do_not_find=dict(type='int', required=False),
        post_raw=dict(type='str', required=False),
        basic_user=dict(type='str', required=False),
        basic_pass=dict(type='str', required=False),
    )

    module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True,
            required_if=[
              ["state", "present", ["name", "url"]],
              ["state", "absent", ["name"]],
              ["test_type", "TCP", ["port"]]
            ]
            )

    username = module.params['username']
    api_key = module.params['api_key']
    name = module.params['name']
    url = module.params['url']
    state = module.params['state']
    test_tags = module.params['test_tags']
    check_rate = module.params['check_rate']
    test_type = module.params['test_type']
    port = module.params['port']
    contact_group = module.params['contact_group']
    paused = module.params['paused']
    node_locations = module.params['node_locations']
    confirmation = module.params['confirmation']
    timeout = module.params['timeout']
    status_codes = module.params['status_codes']
    host = module.params['host']
    custom_header = module.params['custom_header']
    follow_redirect = module.params['follow_redirect']
    find_string = module.params['find_string']
    do_not_find = module.params['do_not_find']
    post_raw = module.params['post_raw']
    basic_user = module.params['basic_user']
    basic_pass = module.params['basic_pass']

    if not (username and api_key) and \
            os.environ.get('STATUSCAKE_USERNAME') and \
            os.environ.get('STATUSCAKE_API_KEY'):
        username = os.environ.get('STATUSCAKE_USERNAME')
        api_key = os.environ.get('STATUSCAKE_API_KEY')
    if not (username and api_key) and \
            not (os.environ.get('STATUSCAKE_USERNAME') and \
            os.environ.get('STATUSCAKE_API_KEY')):
        module.fail_json(msg="You must set STATUSCAKE_USERNAME and " +
                             "STATUSCAKE_API_KEY environment variables " +
                             "or set username/api_key module arguments")

    test = StatusCakeUptime(module,
                            username,
                            api_key,
                            name,
                            url,
                            state,
                            test_tags,
                            check_rate,
                            test_type,
                            port,
                            contact_group,
                            paused,
                            node_locations,
                            confirmation,
                            timeout,
                            status_codes,
                            host,
                            custom_header,
                            follow_redirect,
                            find_string,
                            do_not_find,
                            post_raw,
                            basic_user,
                            basic_pass)

    if state == "absent":
        test.delete_test()
    if state == "present":
        test.create_test()
    if state == "list":
        test.get_all_tests()

    result = test.get_result()
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
