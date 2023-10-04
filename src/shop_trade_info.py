#!/usr/bin/python3
import os
import json
import decimal
import logging
from db_transaction import TradeInfoDb
from youzan_request import YouzanRequest


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


class ShopTradeInfo():

    def __init__(self, date):
        self.abs_path = os.getcwd()
        self.date = date
        self.res_path = self.abs_path + "/result/{}/".format(date)
        # print(self.res_path)
        # folder = os.path.exists(self.res_path)
        # if not folder:
        #     os.mkdir(self.res_path)

        self.shop_list = self._initShopList()
        logging.info("get {} shop info".format(self.shop_list))

    def _initShopList(self):
        req = YouzanRequest()
        param = {
            "page_size": 50,
            "page_num": 1
        }
        ret = req.makeRequest("youzan.shop.chain.descendent.organization.list", "1.0.1", param)
        logging.info("get shop info success")
        return json.loads(ret)["data"]["organization_list"]

    def ResolveForEachShop(self):
        result = {}
        info = TradeInfoDb(self.date)

        for shop in self.shop_list:
            logging.info("start generate result for shop {0} {1}".format(shop["kdt_id"], shop["name"]))
            param = {"node_kdt_id": shop["kdt_id"]}
            data = info.selectTradeInfo(param)
            sell_list, total = self._resolveData(data)
            if total == 0:
                logging.warn("shop {0} {1} has 0 trade info".format(shop["kdt_id"], shop["name"]))
                continue
            result = {
                "kdt_id": shop["kdt_id"],
                "name": shop["name"],
                "date": self.date,
                "total": total,
                "sell_list": sell_list
            }
            with open(self.res_path + "shop-{}.json".format(shop["kdt_id"]), "w", encoding="utf-8") as f:
                res = json.dumps(result, indent=2, ensure_ascii=False, separators=(',', ': '), cls=DecimalEncoder)
                f.write(res)
        

    def _resolveData(self, data):
        dict = {}
        total = 0
        for item in data:
            total += item[4]
            if item[1] in dict.keys():
                cnt = dict[item[1]]["cnt"] + item[3]
                fee = dict[item[1]]["fee"] + item[4]
                dict[item[1]] = {"cnt": cnt, "fee":fee}
            else:
                dict[item[1]] = {"cnt": item[3], "fee":item[4]}

        with open(self.abs_path + '/result/{0}/sku_list.json'.format(self.date), 'r', encoding='utf-8') as f:
            sku_list = json.load(f)

        for item in dict.keys():
            dict[item]["title"] = sku_list[item]

        return dict, total


if __name__ == '__main__':
    info = ShopTradeInfo("2023-09-27")
    info.ResolveForEachShop()
