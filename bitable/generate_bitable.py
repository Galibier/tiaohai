# import lark_oapi as lark
# from lark_oapi.api.bitable.v1 import *
import os
import json
import logging
from bitable.openapi_request import OpenApiRequest


class GenerateBitable:

    def __init__(self, date):
        self.date = date
        self.abs_path = os.getcwd()
        self.dir = self.abs_path + "/result/{}/".format(self.date)
        self.totals = []
        logging.info("load result in dir: {0}".format(self.dir))
        self.req = OpenApiRequest(self.date)

    def UploadTotal(self):
        logging.info("start upload total of each shop")
        self.UploadShopInfo("total", self.totals)
        logging.info("start upload total of each shop, size: {}".format(len(self.totals)))

    def DoIt(self):
        file_list = os.listdir(self.dir)
        for item in file_list:
            if os.path.splitext(item)[-1] == ".json" and item[0:4] == 'shop':
                self.ResolveShopData(self.dir + item)
            else:
                logging.warn("skip file {}".format(item))

    def ResolveShopData(self, file):
        logging.info("start resolve result file of {0}".format(file))
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        shop_name = data["name"]
        shop_total = data["total"]
        self.totals.append({"shop_name": shop_name, "shop_total":shop_total})
        record_list = []
        for item in data["sell_list"]:
            record = {}
            record["sku_id"] = item
            for key,value in data["sell_list"][item].items():
                record[key] = value
            record_list.append(record)

        if len(record_list) != 0:
            self.UploadShopInfo(shop_name, record_list)
        else:
            logging.info("empty list of file {0}".format(file))
        
        logging.info("end resolve result file of {0}".format(file))

    def UploadShopInfo(self, table_name, record_list):
        logging.info("should generate table for shop {}".format(table_name))
        self.req.CreateTableForName(table_name, record_list)


if __name__ == '__main__':
    bi = GenerateBitable('2023-09-27')
    bi.DoIt()
    bi.UploadTotal()
