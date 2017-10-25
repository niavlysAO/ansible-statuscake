from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

class StatusCake:
    URL_UPDATE_TEST = "https://app.statuscake.com/API/Tests/Update"
    URL_ALL_TESTS = "https://app.statuscake.com/API/Tests"
    URL_DETAILS_TEST = "https://app.statuscake.com/API/Tests/Details"

    def __init__(self, module, username, api_key, name, url, state, test_tags, check_rate, test_type, contact_group, user_agent, paused, node_locations, confirmation, timeout, status_codes, host, custom_header, follow_redirect, enable_ssl, find_string, do_not_find):
        self.headers = {"Username": username, "API": api_key}
        self.module = module
        self.name = name
        self.url = url
        self.state = state
        self.test_tags = test_tags
        self.test_type = test_type
        self.contact_group = contact_group
        self.user_agent = user_agent
        self.paused = paused
        self.node_locations = node_locations
        self.confirmation = confirmation
        self.timeout = timeout
        self.status_codes = status_codes
        self.host = host
        self.custom_header = custom_header
        self.follow_redirect = follow_redirect
        self.enable_ssl = enable_ssl
        self.find_string = find_string
        self.do_not_find = do_not_find

        if not check_rate:
            self.check_rate = 300
        else:
            self.check_rate = check_rate

        if not test_type:
            self.test_type = "HTTP"
        else:
            self.test_type = test_type

    def check_response(self,response):
        if response['Success'] == False:
            self.module.exit_json(changed=False, meta= response['Message'])
        else:
            self.module.exit_json(changed=True, meta= response['Message'])
            
    def check_test(self):
        response = open_url(self.URL_ALL_TESTS, headers=self.headers, method="PUT")
        json_resp = json.loads(response.read())

        for item in json_resp:
            if item['WebsiteName'] == self.name:
                return item['TestID']

    def delete_test(self):
        test_id = self.check_test()

        if not test_id:
            self.module.exit_json(changed=False, msg="This test doens't exists")
        else:
            data = {'TestID': test_id}
            response = open_url(self.URL_DETAILS_TESTS, headers=self.headers, data=self.data, method="DELETE")
            json_resp = json.loads(response.read())
            self.check_response(json_resp)
                    
    def create_test(self):
        data = {"WebsiteName": self.name,
                "WebsiteURL": self.url,
                "CheckRate": self.check_rate,
                "TestType": self.test_type,
                "TestTags": self.test_tags,
                "ContactGroup": self.contact_group,
                "UserAgent": self.user_agent,
                "Paused": self.paused,
                "NodeLocations": self.node_locations,
                "Confirmation": self.confirmation,
                "Timeout": self.timeout,
                "StatusCodes": self.status_codes,
                "WebsiteHost": self.host,
                "CustomHeader": self.custom_header.replace("'", "\""),
                "FollowRedirect": self.follow_redirect,
                "EnableSSLWarning": self.enable_ssl,
                "FindString": self.find_string,
                "DoNotFind": self.do_not_find,
                }

        test_id = self.check_test()
        
        if not test_id:
            response = open_url(self.URL_UPDATE_TEST, headers=self.headers, data=data, method="PUT")
            json_resp = json.loads(response.read())
            self.check_response(json_resp)
        else:
            data['TestID'] = test_id
            response = open_url(self.URL_UPDATE_TEST, headers=self.headers, data=data, method="PUT")
            json_resp = json.loads(response.read())
            self.check_response(response.json())

def run_module():

    module_args = dict(
        username=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        name=dict(type='str', required=True),
        url=dict(type='str', required=True),
        state = dict(default='present', choices=['absent', 'present']),
        test_tags=dict(type='str', required=False),
        check_rate=dict(type='int', required=False),
        test_type=dict(type='str', required=False),
        contact_group=dict(type='int', required=False),
        user_agent=dict(type='str', required=False),
        paused=dict(type='int', required=False),
        node_locations=dict(type='str', required=False),
        confirmation=dict(type='int', required=False),
        timeout=dict(type='int', required=False),
        status_codes=dict(type='str', required=False),
        host=dict(type='str', required=False),
        custom_header=dict(type='str', required=False),
        follow_redirect=dict(type='int', required=False),
        enable_ssl=dict(type='int', required=False),
        find_string=dict(type='str', required=False),
        do_not_find=dict(type='int', required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    
    username = module.params['username']
    api_key = module.params['api_key']
    name = module.params['name']
    url = module.params['url']
    state = module.params['state']
    test_tags = module.params['test_tags']
    check_rate = module.params['check_rate']
    test_type = module.params['test_type']
    contact_group = module.params['contact_group']
    user_agent = module.params['user_agent']
    paused = module.params['paused']
    node_locations = module.params['node_locations']
    confirmation = module.params['confirmation']
    timeout = module.params['timeout']
    status_codes = module.params['status_codes']
    host = module.params['host']
    custom_header = module.params['custom_header']
    follow_redirect = module.params['follow_redirect']
    enable_ssl = module.params['enable_ssl']
    find_string = module.params['find_string']
    do_not_find = module.params['do_not_find']

    test = StatusCake(module, username, api_key, name, url, state, test_tags, check_rate, test_type, contact_group, user_agent, paused, node_locations, confirmation, timeout, status_codes, host, custom_header, follow_redirect, enable_ssl, find_string, do_not_find)

    if state == "absent":
        test.delete_test()
    else:
        test.create_test()

def main():
    run_module()

if __name__ == '__main__':  
    main()
