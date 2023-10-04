import sys
import os
import logging
sys.path.insert(0, 'src')
from shop_trade_info import ShopTradeInfo
from daily_trade_info import DailyTradeInfo
from bitable.generate_bitable import GenerateBitable


if __name__ == '__main__':
    date = '2023-10-03'
    path = os.getcwd()
    res_path = os.getcwd() + "/result/{}/".format(date)
    folder = os.path.exists(res_path)

    if not folder:
        os.mkdir(res_path)

    logging.basicConfig(filename=res_path + date + ".log", level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

    pre = DailyTradeInfo(date)
    pre.prepareAllOrders()
    info = ShopTradeInfo(date)
    info.ResolveForEachShop()
    bitable = GenerateBitable(date)
    bitable.DoIt()
    bitable.UploadTotal()
