#!/usr/bin/python3
import os
import json
import time
import requests
import logging


class YouzanRequest():

    def __init__(self):
        self.abs_path = os.getcwd()
        self.headers = {"Content-Type": "application/json"}  # 设置请求头
        self.access_token = self._getToken()

    def _getToken(self):
        ticks = (time.time() * 1000)
        with open(self.abs_path + '/config/token.json', 'r', encoding = 'utf-8') as config:
            token_info = json.load(config)
            expires = token_info["expires"]
            access_token = token_info["access_token"]

        if expires < ticks:
            new_info = self._updateToken()
            logging.info("update Token when timestamps expires {0} now: {1}".format(expires, ticks))
            access_token = new_info["access_token"]
            with open(self.abs_path + '/config/token.json', 'w', encoding = 'utf-8') as update_config:
                json.dump(new_info, update_config)
        else:
            logging.info("get Token from config file")

        return "access_token={0}".format(access_token)

    def _updateToken(self):
        tokenUrl = "https://open.youzanyun.com/auth/token"
        with open(self.abs_path + '/config/store.json', 'r', encoding = 'utf-8') as config:
            param = json.load(config)

        response = requests.post(tokenUrl, headers=self.headers, json=param)
        return json.loads(response.text)["data"]

    def makeRequest(self, api, version, param=None):
        url = self._makeUrl(api, version)
        logging.info("post to url {0}".format(url))
        if (param):
            response = requests.post(url, headers=self.headers, json=param)
        else:
            response = requests.post(url, headers=self.headers)
        if response.status_code:
            logging.info("get from url {0} success".format(url))
            return response.text
        else:
            logging.error("fail to get from url: {}".format(url))
            return {}
    
    def makeRequestHook(self, api, version, param=None):
        print(param)
        with open(self.abs_path + '/data/2023-09-27-{0}.json'.format(param["page_no"]), 'r', encoding = 'utf-8') as f:
            return f.read()

    def _makeUrl(self, api, version):
        return "https://open.youzanyun.com/api/{0}/{1}?{2}".format(api, version, self.access_token)


if __name__ == '__main__':
    req = YouzanRequest()
    param = {"keywords":"E20230929140855019706189"}
    ret = json.loads(req.makeRequest('youzan.trades.sold.get', '4.0.4', param))
    print(ret["trace_id"])
    print(ret["message"])
    print(param)
    print(ret["data"]["full_order_info_list"][0]["full_order_info"]["order_info"]["tid"])

