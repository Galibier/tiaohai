#!/usr/bin/python3
import os
import json
import time
import requests
import logging


class OpenApiRequest():

    def __init__(self, date):
        self.abs_path = os.getcwd()
        self.date = date
        self.app_id = ""
        self.app_secret = ""
        self.fold_token = ""
        self._loadIdentityInfo()
        self.tenant_access_token = self._getToken()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token
        }
        self.app_token = self._createBitable()

    def _loadIdentityInfo(self):
        with open(self.abs_path + '/config/lark.json', 'r', encoding = 'utf-8') as f:
            config = json.load(f)

        self.app_id = config["app_id"]
        self.app_secret = config["app_secret"]
        self.fold_token = config["fold_token"]

    # curl -i -X POST 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal' -H 'Content-Type: application/json' -d '{"app_id":"","app_secret":""}'
    def _getToken(self):
        token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        head = {"Content-Type": "application/json"}
        param = {"app_id": self.app_id, "app_secret": self.app_secret}
        response = requests.post(token_url, headers=head, json=param, verify=False)
        return json.loads(response.text)["tenant_access_token"]

    # curl -i -X POST 'https://open.feishu.cn/open-apis/bitable/v1/apps' \
    # -H 'Content-Type: application/json' \
    # -H 'Authorization: Bearer u-' \
    # -d '{
    #     "folder_token": "",
    #     "name": ""
    # }'
    def _createBitable(self):
        param = {
            "folder_token": self.fold_token,
            "name": self.date
        }
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps'
        response = requests.post(url, headers=self.headers, json=param, verify=False)
        logging.info("get ret of create bitable {0}, {1}".format(self.date, response.text))
        return json.loads(response.text)["data"]["app"]["app_token"]

    # curl -i -X POST 'https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables' \
    # -H 'Content-Type: application/json' \
    # -H 'Authorization: Bearer u-' \
    # -d '{
    #     "table": {
    #         "default_view_name": "跳海酒馆深圳南山书城(网店)",
    #         "fields": [
    #             {
    #                 "field_name": "sku_id",
    #                 "type": 1
    #             },
    #             {
    #                 "field_name": "name",
    #                 "type": 1
    #             },
    #             {
    #                 "field_name": "count",
    #                 "type": 2
    #             },
    #             {
    #                 "field_name": "fee",
    #                 "type": 2
    #             }
    #         ],
    #         "name": "跳海酒馆深圳南山书城(网店)"
    #     }
    # }'

    # curl -i -X POST 'https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records/batch_create' \
    # -H 'Content-Type: application/json' \
    # -H 'Authorization: Bearer u-' \
    # -d '{
    #     "records": [
    #         {
    #             "fields": {
    #                 "count": 1,
    #                 "fee": 118,
    #                 "name": "炼金大师（深一网）",
    #                 "sku_id": "P221215962725781"
    #             }
    #         },
    #         {
    #             "fields": {
    #                 "count": 1,
    #                 "fee": 118,
    #                 "name": "炼金大师（深一网）",
    #                 "sku_id": "P221215962725782"
    #             }
    #         }
    #     ]
    # }'
    def CreateTableForName(self, name, record_list):
        table_url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/{0}/tables'.format(self.app_token)
        param = {
            "table": {
                "default_view_name": name,
                "name": name,
            }
        }
        if len(record_list) == 0:
            print("empty record list")
        else:
            fields = []
            field = {}
            for key, value in record_list[0].items():
                print(key, value)
                print(type(value))
                field = {}
                field["field_name"] = key
                if isinstance(value, str):
                    field["type"] = 1
                else:
                    field["type"] = 2
                fields.append(field)
            print(fields)
        
        param["table"]["fields"] = fields
        logging.info("POST to url: '{0}' with param: {1}".format(table_url, param))
        response = requests.post(table_url, headers=self.headers, json=param, verify=False)
        logging.info("get ret of create table {0}, {1}".format(name, response.text))
        table_id = json.loads(response.text)["data"]["table_id"]

        record_url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/{0}/tables/{1}/records/batch_create'.format(self.app_token, table_id)
        records = []
        for item in record_list:
            record = {}
            record["fields"] = item
            print(record)
            records.append(record)
        param.clear()
        param["records"] = records
        logging.info("POST to url: '{0}' with param: {1}".format(record_url, param))
        response = requests.post(record_url, headers=self.headers, json=param, verify=False)


if __name__ == '__main__':
    req = OpenApiRequest("2023-10-01")
    # record_list = [{'sku_id': 'P230923766720733', 'cnt': 1, 'fee': 68.0, 'title': 'HBC'}, {'sku_id': 'P230923197441685', 'cnt': 1, 'fee': 68.0, 'title': '996'}, {'sku_id': 'P230916502139133', 'cnt': 2, 'fee': 76.0, 'title': '春游'}, {'sku_id': 'P230924020400147', 'cnt': 1, 'fee': 61.2, 'title': '荔荔安'}, {'sku_id': 'P230924738517161', 'cnt': 2, 'fee': 114.0, 'title': '文昌龙眼椰子'}, {'sku_id': 'P210624923392032', 'cnt': 3, 'fee': 180.0, 'title': '夕阳小茉莉'}, {'sku_id': 'P230923288965349', 'cnt': 1, 'fee': 70.0, 'title': '犬儒主义'}]
    record_list = [{'shop_name': '跳海酒馆深圳南山书城(网店)', 'shop_total': 274.0}, {'shop_name': '跳海酒馆北京安定门店', 'shop_total': 7717.0}, {'shop_name': '跳海village北京慈云寺店', 'shop_total': 18795.0}, {'shop_name': '跳海Drunk n Jump', 'shop_total': 179.5}, {'shop_name': '跳海酒馆成都玉林路店', 'shop_total': 3362.2}, {'shop_name': '跳海酒馆广州花城大道店', 'shop_total': 2988.2}, {'shop_name': '跳海酒馆杭州中山中路店', 'shop_total': 10224.2}, {'shop_name': '跳海酒馆深圳(O·Power)', 'shop_total': 5244.0}, {'shop_name': '跳海stage北京三里屯店', 'shop_total': 5033.0}, {'shop_name': '跳海酒馆北京北新桥店', 'shop_total': 3105.0}, {'shop_name': '跳海酒馆上海平武路店', 'shop_total': 8580.2}, {'shop_name': '跳海酒馆杭州（聚才路店）', 'shop_total': 4787.22}, {'shop_name': '跳海酒馆北京后海店', 'shop_total': 6597.0}, {'shop_name': '跳海酒馆广州六运店', 'shop_total': 6861.0}, {'shop_name': '跳海酒馆重庆新牌坊店', 'shop_total': 637.2}, {'shop_name': '跳海酒馆深圳(南山书城)', 'shop_total': 9912.0}]
    req.CreateTableForName('跳海酒馆重庆新牌坊店', record_list)
