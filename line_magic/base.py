import requests


class BaseClient(object):
    def __init__(self, endpoint, headers):
        self.endpoint = endpoint
        self.headers = headers

    def isOK(self, resp):
        if resp.status_code == 200:
            return True
        else:
            raise Exception(resp.text)

    def reqPost(self, addr, headers=None, params=None, json=None):
        if headers is None:
            headers = self.headers
        if params is not None:
            return requests.post(
                self.endpoint + addr,
                headers=headers,
                params=params
            )
        else:
            return requests.post(
                self.endpoint + addr,
                headers=headers,
                json=json
            )

    def reqGet(self, addr, headers=None, params=None):
        if headers is None:
            headers = self.headers
        if params is None:
            params = {}
        return requests.get(self.endpoint+addr, headers=headers, params=params)

    def reqDel(self, addr, headers=None, params=None, json=None):
        if headers is None:
            headers = self.headers
        if params is None:
            params = {}
        if params is not None:
            return requests.delete(
                self.endpoint + addr,
                headers=headers,
                params=params
            )
        else:
            return requests.delete(
                self.endpoint + addr,
                headers=headers,
                json=json
            )
