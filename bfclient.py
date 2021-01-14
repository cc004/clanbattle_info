#from requests import request
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
    'BF-Client-Data': 'WVcxMGIybHRlbXN3T0RscFpXczBPSEIzWW1sMU0zbEJTVmRPTWxVM05VbDFaMjlZVVZrNGVXOVlURXBHZUU1RFRsRXpkM0ZYU2tkQ1VFNWxTalJNTkUxYVVVSjFiSFoxTlVoM2NWWnBRelJUWnpGSmRXTTVlRnB0T1ZWQ1dXVmFiRXB4VFhsbmJWbHRObXhZVWxreVVWaDVVM1k1VkZGRmNpdGtVMFZaZEZsb1NtaFpSbFJwYjJ4dlRGYzBjMEpvZGtkUGVVTnNNeXM1ZVdWVGVTdDJTMjh4V0RScVRHMVhTVEpLZGpjMGRUTkJLM1kyZUc5NEszVXlUVDA9',
    'device_number': '0a2db91f5854f414af9381b79a94f75e20210113114743845a301f32a91a5f31'
}

class bfclient:

    @staticmethod
    def newdevice():
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        return ''.join([(alphabet[randint(0, 61)] if i != 14 else '_') for i in range(44)])

    def __init__(self, appver, device, key=None):
        self.key = key
        self.device_number = device['device_number']
        self.device = bfclient.newdevice()
        self.header = {}
        self.token = None

        for key in common:
            self.header[key] = common[key]
        
        for key in appver:
            self.header[key] = appver[key]

        self.header['BF-Client-Data'] = device['BF-Client-Data']

    @staticmethod
    def timestamp(): # returns (ts, rid)
        return (int(time()), int(time() * 1000 + randint(900000, 1000000)))

    
    def paramsign(self, param: dict, dologin) -> dict:
        (param['ts'], param['rid']) = bfclient.timestamp()
        param['buvid' if dologin else 'device_number'] = self.device_number
        if dologin:
            param['access_key'] = self.key
        elif self.token is not None:
            param['access_token'] = self.token
        lst = [f'{key}={param[key]}' for key in param]
        lst.sort()
        m = md5()
        m.update(('&'.join(lst) + 'WKO-2k_03jisxgH6').encode('utf8'))
        param['sign'] = m.hexdigest()
    
    async def refresh_token(self):
        data = await self.callapi('POST', '/client/android', {
            'method': 'login',
            'access_key': self.key,
            'base': '1',
            'buvid': '',
            'device': self.device,

        }, dologin = True)

        try:
            self.token = data['data'][0]['access_token']
            return None
        except:
            return data
    
    # method should be POST or GET
    async def callapi(self, method, endpoint, params, dologin = False, retry = False):
    
        if not dologin and self.token is None:
            result = await self.refresh_token()
            if result is not None:
                return result
        self.paramsign(params, dologin)

        get_params = {}

        if method == 'POST':
            if 'target' in params:
                get_params['target'] = params['target']
                params.pop('target')
            if 'method' in params:
                get_params['method'] = params['method']
                params.pop('method')
            params['ts'] = str(params['ts'])
            params['rid'] = str(params['rid'])
        else:
            get_params = params
        
        url = f'https://api.bigfun.cn{endpoint}{"" if len(get_params) == 0 else "?" + urlencode(get_params)}'
        print(f'calling with url={url}')
        result = loads(await (await request(method, url, headers=self.header, data = dumps(params))).content)

        if 'error' in result:
            code = result['error']['code']
            if code == 1103:
                result = await self.refresh_token()
                if result is not None:
                    return result
                elif not retry:
                    return await self.callapi(method, endpoint, params, dologin, True)
                else:
                    return result
