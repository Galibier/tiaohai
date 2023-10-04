#!/usr/bin/python3
import logging
import pymysql
import json
import os


class TradeInfoDb():

    def __init__(self, date):
        self.date = date
        self.abs_path = os.getcwd()
        self.table_name = date.replace('-', '_')
        self.sku_list = {}
        self.sku_no = 1
        with open(self.abs_path + '/config/db.json', 'r', encoding = 'utf-8') as f:
            config = json.load(f)

        self.db = pymysql.connect(
            host = config["host"],
            port = config["port"],
            user = config["user"],
            password = config["password"],
            database = config["database"])

    def createTradeTable(self):
        cursor = self.db.cursor()
        cursor.execute("DROP TABLE IF EXISTS {0}".format(self.table_name))
        logging.info("drop table: {0} if exists".format(self.table_name))
        cursor.execute("CREATE TABLE {0} (\
                        oid BIGINT NOT NULL,\
                        sku CHAR(20) NOT NULL,\
                        price DECIMAL(10,2) NOT NULL,\
                        count INT NOT NULL,\
                        payment DECIMAL(10,2) NOT NULL,\
                        tid CHAR(30) NOT NULL,\
                        node_kdt_id INT NOT NULL,\
                        PRIMARY KEY (oid)\
                        );".format(self.table_name))
        logging.info("create table {0} success".format(self.table_name))

    def insertTradeInfo(self, order_list):
        sql = "INSERT INTO {0} (oid, sku, price, count, payment, tid, node_kdt_id) VALUES ".format(self.table_name)
        first = True
        # print(len(order_list))
        for item in order_list:
            # payment = item["full_order_info"]["pay_info"]["payment"]
            tid = item["full_order_info"]["order_info"]["tid"]
            node_kdt_id = item["full_order_info"]["order_info"]["node_kdt_id"]
            # status = item["full_order_info"]["order_info"]["status"]
            # print("{0} {1} {2} {3}".format(payment, tid, node_kdt_id, status))
            for sku in item["full_order_info"]["orders"]:
                outer_sku_id = sku["outer_sku_id"]
                if outer_sku_id == "":
                    outer_sku_id = "TEMPSKU" + str(1000 + self.sku_no) + str(10000 + int(float(sku["price"])))
                    logging.warning("create temporary sku_id {0} for item loss info with tid {1}".format(outer_sku_id, tid))
                    self.sku_no += 1
                self.sku_list[outer_sku_id] = sku["title"]
                if first:
                    first = False
                else:
                    sql += ","
                sql += "({0}, '{1}', {2}, {3}, {4}, '{5}', {6})".format(sku["oid"], outer_sku_id, sku["price"], sku["num"], sku["payment"], tid, node_kdt_id)

        sql += ";"
        with open(self.abs_path + '/result/{0}/sku_list.json'.format(self.date), 'w', encoding='utf-8') as f:
            res = json.dumps(self.sku_list, indent=2, ensure_ascii=False, separators=(',', ': '))
            f.write(res)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
            logging.info("add {0} data to table: {1} success".format(len(order_list), self.table_name))
        except:
            self.db.rollback()
            logging.error("add {0} data to table: {1} failed".format(len(order_list), self.table_name))

    def selectTradeInfo(self, param=None):
        cursor = self.db.cursor()
        sql = "SELECT * FROM {0}".format(self.table_name)
        first = True
        if param == None:
            sql += ";"
            logging.info("generate select sql of '{0}'".format(sql))
        else:
            for key, value in param.items():
                if first:
                    first = False
                    sql += " WHERE {} = {}".format(key, value)
                else:
                    sql += " AND {} = {}".format(key, value)
            sql += ";"
            logging.info("generate select sql of '{0}'".format(sql))

        cursor.execute(sql)
        data = cursor.fetchall()
        logging.info("get {} info".format(len(data)))
        return data


if __name__ == '__main__':
    info = TradeInfoDb("2023-09-27")
    param = {"node_kdt_id": 94388142}
    print(info.selectTradeInfo(param))


