from hoshino.aiorequests import request
from time import time
from random import randint
from hashlib import md5
from urllib.parse import urlencode
from json import dumps, loads

common = {
    'Content-Type': 'application/vnd.api+json; charset=utf-8',
    'Accept': 'application/vnd.api+json'
}

Android362 = {
    'BF-Client-Type': 'BF-ANDROID',
    'BF-Client-Version': '3.6.2',
    'User-Agent': 'okhttp/3.12.12',
    'BF-Json-Api-Version': 'v1.0'
}

default_device = {
    'BF-Client-Data': 'TTJzMk9Xa3djMnBvZEhjeU1uVXlkRFpLTUd4amNVTTBPRkJUYjJwM05tOWlheTkxYkcxaFYwbE5UamRtWm5wQ2FYb3ZUelJRWm1GSWJIVktNMEkxUjJGeEx6Rk9WVXh0ZDBKT2IxQjBiMk5FWjNSU2NtSnpjMlZtVTBJdlRVRlpVVkp3YVZGdVRsTjBaMVpNYVdsYVNtbENOSGxpTjJSWmNEQnZWMnd3VUM4NVlYbE9VeTlOUkhOeGRWTjFkak4xZDNCWE5UQmxUR1UyU1RWbVpVUjNkMEpFVHpZekwxVmhTMWhtVUc1cmFsaFBlV1YxV0ZaV1VYRlVWVDA9',
    'device_number': '0a2db91f5854f414af9381b79a94f75e20210113114743845a301f32a91a5f31'
}

class bfclient:

    def __init__(self, appver, device, token=None):
        self.token = token
        self.device_number = device['device_number']
        self.header = {}

        for key in common:
            self.header[key] = common[key]
        
        for key in appver:
            self.header[key] = appver[key]

        self.header['BF-Client-Data'] = device['BF-Client-Data']

    @staticmethod
    def timestamp(): # returns (ts, rid)
        return (int(time()), int(time() * 1000 + randint(900000, 1000000)))

    
    def paramsign(self, param: dict) -> dict:
        (param['ts'], param['rid']) = bfclient.timestamp()
        param['device_number'] = self.device_number
        if self.token is not None:
            param['access_token'] = self.token
        lst = [f'{key}={param[key]}' for key in param]
        lst.sort()
        m = md5()
        print(('&'.join(lst) + 'WKO-2k_03jisxgH6').encode('utf8'))
        m.update(('&'.join(lst) + 'WKO-2k_03jisxgH6').encode('utf8'))
        param['sign'] = m.hexdigest()
    
    # method should be POST or GET
    async def callapi(self, method, endpoint, params):
        self.paramsign(params)

        get_params = {}

        if method == 'POST':
            if 'target' in params:
                get_params['target'] = params['target']
                get_params['method'] = params['method']
        else:
            get_params = params
        
        url = f'https://api.bigfun.cn{endpoint}{"" if len(get_params) == 0 else "?" + urlencode(get_params)}'

        print (f'calling with url={url}')
        return loads(await (await request(method, url, headers=self.header, data = dumps(params))).content)

