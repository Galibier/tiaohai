#!/usr/bin/python3
from youzan_request import YouzanRequest
from db_transaction import TradeInfoDb
import datetime
import logging
import json
import os

# getToken()

def makeRequestHook(api, version, param=None):
    print(param)
    ret = {
        "full_order_info_list": [],
        "total_results": 784,
        "param": param
    }

    return ret

class DailyTradeInfo():

    def __init__(self, date):
        self.abs_path = os.getcwd()
        self.date = date
        end_data = (datetime.datetime.strptime(self.date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.start = self.date + " 04:00:00"
        self.end = end_data + " 03:59:59"
        logging.info("start get all order info of {0} from {1} to {2}".format(self.date, self.start, self.end))

    def prepareAllOrders(self):
        page_size = 100
        total_cnt = 0
        total_result = 10000 # seem enough now
        param = {
            "start_created": self.start,
            "end_created": self.end,
            "page_size": page_size,
            "page_no": 0
        }
        # print(param)
        
        info_db = TradeInfoDb(self.date)
        info_db.createTradeTable()
        req = YouzanRequest()
        while total_cnt < total_result:
            param["page_no"] += 1
            ret = req.makeRequest("youzan.trades.sold.get", "4.0.4", param)
            data = json.loads(ret)["data"]

            # keep for debug
            # ret = req.makeRequestHook("youzan.trades.sold.get", "4.0.4", param)
            # data = json.loads(ret)
            # file_name = self.date + "-{}.json".format(param["page_no"])
            # data = loadRequestResult(file_name)

            total_result = data["total_results"]
            total_cnt += page_size
            if total_cnt > total_result:
                total_cnt = total_result
            logging.info("getting infomation {}/{}".format(total_cnt, total_result))

            # keep for debug
            # file_name = date + "-{}.json".format(param["page_no"])
            # self._dumpRequestResult(file_name, data)

            info_db.insertTradeInfo(data["full_order_info_list"])


    def _dumpRequestResult(self, file_name, data):
        with open(self.abs_path + '/data/' + file_name, 'w', encoding = 'utf-8') as f:
            json.dump(data, f)

    def _loadRequestResult(self, file_name):
        with open(self.abs_path + '/data/' + file_name, 'r', encoding = 'utf-8') as f:
            data = json.load(f)
            return data


if __name__ == '__main__':
    info = DailyTradeInfo("2023-09-27")
    info.prepareAllOrders()
