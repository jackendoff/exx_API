import random
import numpy as np
import math
import sys

import logging
from charge_data_format import ChargeDataFormat
import time
import threading
from content_safe import *
# logging.basicConfig(filename='logger_main_1.log',level=logging.INFO)


# '''策略4:下单，成交空间不同模式随机价格,生成一分钟随机列表'''


class MarketMarkerOne(ChargeDataFormat):

    def __init__(self,start_price):
        ChargeDataFormat.__init__(self)
        # 已下单的id
        self.entrustId_buy = None
        self.entrustId_sell = None
        # 现价
        self.now_price = None
        # 即将下单价
        self.price = None
        # 即将下单数量
        self.amount = None
        # 睡眠时间
        # self.time_sleep = None
        # 初始化睡眠时间
        self.timing = None

        # 默认被吃单状态为False
        self.safe_or = False

        # 随机列表
        self.order_list = [0,-1,-2,2,3,4,0,2,1,1,-2]

        # 随机列表索引
        self.order_list_index = 0

        # 保存上次时间，和现在的时间进行对比
        self.last_time = None

        # 初始化中间价格
        self.center_price = float(start_price)

        # 卖一买一中间价
        self.bid_asks_price_center = 0.1111

    # 计算随机下单价格
    def get_perfect_price_amount(self):

        # 获取买一，卖一的价格
        # 获取最新成交价，参数用来传递开始的价格
        self.now_price = float(self.charge_get_trades())  # str-->float
        # print(self.safe_or,self.base_price)
        # 获取自己上一笔成交价格
        # self.last_price = float(self.charge_get_user_entrust_list())
        # print('+++++++++++++last_price',last_price)
        # self.timing = None
        # 获取买一卖一价格,数量
        asks_list_one, bids_list_one = self.charge_get_entrusts()
        asks_list_price = float(asks_list_one[0])
        bids_list_price = float(bids_list_one[0])

        # 计算买一卖一中间价
        self.bid_asks_price_center = round((asks_list_price+bids_list_price)/2,4)
        #如果成交空间过小，则执行吃小单
        if abs(asks_list_price - bids_list_price) < 0.0050:
            # 执行应对动态压单的策略
            self.eat_dynamic_order()

        # if self.center_price is not None:
        #     last_price = float(self.start_price)
        #     print('start_price:',self.start_price)
        #     self.start_price = None

        now_localtime = time.localtime(time.time()).tm_min
        # 如果不再是同一分钟，则再次计算中间价格
        if now_localtime != self.last_time:
            x0 = float(np.random.normal(0, 0.0009, 1))
            # print(x0, type(x0))

            x = min(0.90 * math.sqrt(0.0009), max(-0.90 * math.sqrt(0.0009), x0))
            num = random.randint(2,4)
            order_list = 0.0001 * np.random.randint(low=-num, high=num, size=4)
            valure_list = [0,0.0001]
            valure_list_after = [0.0001,-0.0001]
            valure_list.extend(list(order_list))
            valure_list.extend(valure_list_after)
            self.order_list = valure_list
            self.order_list_index = 0
            rt = float(x)
            self.last_time = now_localtime
            # 计算中心价格
            self.center_price = min(max(self.center_price * (1 + rt), bids_list_price+0.0001), asks_list_price-0.0001)
            # print(self.order_list,self.base_price)

        # 被吃单状态为Flase
        if self.safe_or is False:
            # 计算正常下单数量
            self.amount = random.randint(ORDER_AMOUNT_MIN,ORDER_AMOUNT_MAX)
            # 计算正常睡眠时间
            self.timing = random.randint(TIMING_MIN, TIMING_MAX)

        # 被吃单状态为True
        elif self.safe_or is True:
            # 计算被吃单下单数量
            self.amount = random.randint(EATEN_ORDER_AMOUNT_MIN,EATEN_ORDER_AMOUNT_MAX)
            # 计算被吃单睡眠时间
            self.timing = random.randint(EATEN_TIMING_MIN, EATEN_TIMING_MAX)

        # 当列表索引大于列表元素值时，重新计算列表并重置列表索引为0
        if self.order_list_index >= 8:
            order_list = 0.0001 * np.random.randint(low=-4, high=4, size=10)
            self.order_list = list(order_list)
            self.order_list_index = 0

        # 通过中心价格和震荡列表，计算出下单价格
        order_price = self.center_price+self.order_list[self.order_list_index]
        print(self.center_price,'--------------------')
        self.order_list_index += 1

        # 保证下单价格在成交空间内
        self.price = max(min(round(float(order_price),4),asks_list_price-0.0001),bids_list_price+0.0001)

        # 如果中心价格不在成交空间内，则调整中心价格，跟随一次上一笔成交价
        if self.center_price >=asks_list_price or self.center_price <= bids_list_price:
            print('中心价格不在成交空间内')
            self.center_price = self.price
        # 计算的下单价格依然不在成交空间内（成交空间被挤压为0）
        if self.price >= asks_list_price or self.price<=bids_list_price:
            print('卖一价格{0}，计算价格{1}，买一价格{2}'.format(asks_list_price,self.price,bids_list_price))
            return None,self.amount,self.timing
        print('中心价格{0}，下单价格{3}，列表{1},列表索引{2}'.format(round(self.center_price,4), self.order_list, self.order_list_index,self.price))
        return self.price, self.amount,self.timing

#++++++++++++++++++++++++++++++++++师傅 ---^


    # 保证双向成交，双向下单完成之后要保证成交
    def must_deal_sell(self,entrustId):
        # 通过订单id，获取订单是否完全成交，未完全成交的进行撤单1取消 2交易成功 3交易一部分
        if entrustId is None:
            print('X'*10,'未获取到buy_id')
            return
        params = {"entrustId":entrustId}
        deal_status = self.charge_get_entrust_by_id(**params)
        print('deal_status_sell:',deal_status)
        # logging.info('deal_status_sell:%s'%deal_status)

        # 如果成交状态不是全部成交则撤单
        for i in range(3):
            if deal_status != 2:
                cancle_data = self.change_cancle_entrust(entrustId)

                # self.start_time += 20

                # 当等待时间大于100时自动恢复
                # if self.start_time > 100:
                #     self.start_time = 5
                print('sell撤单信息：',cancle_data,entrustId)
                self.safe_or = True
                self.timing = random.randint(EATEN_TIMING_MIN,EATEN_TIMING_MAX)

                # logging.info('sell撤单信息：%s'%cancle_data)

        pass

    def must_deal_buy(self,entrustId):
        # 通过订单id，获取订单是否完全成交，未完全成交的进行撤单1取消 2交易成功 3交易一部分
        if entrustId is None:
            print('X'*10,'未获取到buy_id')
            return

        params = {"entrustId":entrustId}
        deal_status = self.charge_get_entrust_by_id(**params)
        print('deal_status_buy:',deal_status)
        # logging.info('deal_status_buy:%s'%deal_status,type(deal_status))

        # 如果成交状态不是全部成交则撤单
        for i in range(5):
            if deal_status != 2:
                cancle_data = self.change_cancle_entrust(entrustId)
                # self.start_time += 20
                # if self.start_time > 100:
                #     self.start_time = 5
                print('buy撤单信息：',cancle_data,entrustId,'延长等待时间',self.timing)
                self.safe_or = True
                self.timing = random.randint(EATEN_TIMING_MIN,EATEN_TIMING_MAX)

                # logging.info('buy撤单信息：%s'%cancle_data)

        pass

    # 挂卖单
    def add_entrust_sell(self):
        self.entrustId_sell = self.charge_add_entrust_sell(float(self.price),int(self.amount))
        # time.sleep(1)
        # self.must_deal_sell(self.entrustId_sell)

    # 挂买单
    def add_entrust_buy(self):
        self.entrustId_buy = self.charge_add_entrust_buy(float(self.price),int(self.amount))
        # time.sleep(1)
        # self.must_deal_buy(self.entrustId_buy)

    # 吃小单策略，当成交空间小于100，如果有小于10的单子，则吃1-5次
    def eat_dynamic_order(self):
        print('检测到成交空间<50 《~~》')
        try:
            global asks_list_price
            global bids_list_price
            global asks_list_amount
            global bids_list_amount
            asks_list_one, bids_list_one = self.charge_get_entrusts()
            asks_list_price = float(asks_list_one[0])
            bids_list_price = float(bids_list_one[0])

            asks_list_amount = float(asks_list_one[1])
            bids_list_amount = float(bids_list_one[1])
            self.bid_asks_price_center = round((asks_list_price + bids_list_price) / 2, 4)

            i = 0
            if abs(asks_list_price - bids_list_price) < 0.0050:
                # 获取买一卖一数据
                while asks_list_amount < 20 and i < 5:
                    print('发现卖一<10,准备吃单')
                    # 下buy单成交并撤单，吃小单
                    order_data = self.charge_add_entrust_buy(price=asks_list_price, amount=2)
                    cancel_data = self.change_cancle_entrust(order_data)

                    # 获取买一卖一数据
                    asks_list_one, bids_list_one = self.charge_get_entrusts()

                    asks_list_price = float(asks_list_one[0])
                    bids_list_price = float(bids_list_one[0])

                    asks_list_amount = float(asks_list_one[1])
                    bids_list_amount = float(bids_list_one[1])
                    self.bid_asks_price_center = round((asks_list_price + bids_list_price) / 2, 4)

                    i += 1
                    # print(data,type(data))
                    print(order_data)
                    print(cancel_data)
                    time.sleep(1)
                    # 成交空间大于100停止吃单
                    if abs(asks_list_price - bids_list_price) >= 0.0100:
                        return
                while bids_list_amount < 20 and i < 5:
                    # 下sell单成交并撤单，吃小单
                    print('发现买一<10,准备吃单')

                    order_data = self.charge_add_entrust_sell(price=bids_list_price, amount=2)
                    cancel_data = self.change_cancle_entrust(order_data)

                    # 获取买一卖一数据
                    asks_list_one, bids_list_one = self.charge_get_entrusts()
                    asks_list_price = float(asks_list_one[0])
                    bids_list_price = float(bids_list_one[0])

                    asks_list_amount = float(asks_list_one[1])
                    bids_list_amount = float(bids_list_one[1])
                    self.bid_asks_price_center = round((asks_list_price + bids_list_price) / 2, 4)

                    i += 1
                    # print(data,type(data))
                    print(order_data)
                    print(cancel_data)
                    time.sleep(1)
                    # 成交空间大于100停止吃单
                    if abs(asks_list_price - bids_list_price) >= 0.0100:
                        return
            else:
                return
        except Exception:
            return

    # 吃小单策略,当成交空间小于100，如果有小于2的单子，则吃1-5个
    # 应对静态压单的小单机器人
    # 触发条件：计算随机价格连续失败5次
    def eat_small_order(self):
        # 获取买一卖一数据
        global asks_list_price
        global bids_list_price
        global asks_list_amount
        global bids_list_amount
        asks_list_one, bids_list_one = self.charge_get_entrusts()
        asks_list_price = float(asks_list_one[0])
        bids_list_price = float(bids_list_one[0])

        asks_list_amount = float(asks_list_one[1])
        bids_list_amount = float(bids_list_one[1])
        self.bid_asks_price_center = round((asks_list_price+bids_list_price)/2,4)

        i = 0
        while asks_list_amount<1 and i<5:
        # 下buy单成交并撤单，吃小单
            order_data = self.charge_add_entrust_buy(price=asks_list_price, amount=2)
            cancel_data = self.change_cancle_entrust(order_data)

            # 获取买一卖一数据
            asks_list_one, bids_list_one = self.charge_get_entrusts()

            asks_list_price = float(asks_list_one[0])
            bids_list_price = float(bids_list_one[0])

            asks_list_amount = float(asks_list_one[1])
            bids_list_amount = float(bids_list_one[1])
            self.bid_asks_price_center = round((asks_list_price+bids_list_price)/2,4)

            i+=1
            # print(data,type(data))
            print(order_data)
            print(cancel_data)
            time.sleep(1)
            # 成交空间大于100停止吃单
            if abs(asks_list_price-bids_list_price) >= 0.0100:
                return
        while bids_list_amount < 1 and i<5:
            # 下sell单成交并撤单，吃小单
            order_data = self.charge_add_entrust_sell(price=bids_list_price, amount=2)
            cancel_data = self.change_cancle_entrust(order_data)

            # 获取买一卖一数据
            asks_list_one, bids_list_one = self.charge_get_entrusts()
            asks_list_price = float(asks_list_one[0])
            bids_list_price = float(bids_list_one[0])

            asks_list_amount = float(asks_list_one[1])
            bids_list_amount = float(bids_list_one[1])
            self.bid_asks_price_center = round((asks_list_price + bids_list_price) / 2, 4)

            i+=1
            # print(data,type(data))
            print(order_data)
            print(cancel_data)
            # 成交空间大于100停止吃单
            time.sleep(1)
            if abs(asks_list_price - bids_list_price) >= 0.0100:
                return


def run_threading(marker):
    # 获取计算的下单价格和个数

    # price,amount,time_data = marker.get_perfect_price_amount()
    # price = None

    # 执行动态压单，应对措施
    def re_get_price():
        global price
        global amount
        global time_data
        try:
            price,amount,time_data = marker.get_perfect_price_amount()
            # print(price, amount, time_data)

        except Exception as err:
            print(err)
            print('main_2.py,re_get_price,小心内存溢出 line：403')
            price, amount, time_data = re_get_price()
            # print(price, amount, time_data)

        return price,amount,time_data
    price, amount, time_data = re_get_price()
    print(price, amount, time_data)
    # 没有满足条件的下单价格
    i = 0
    while price is None and i<5:
        print('随机下单价格计算失败，2秒后重新运行')
        time.sleep(2)
        price, amount,time_data = marker.get_perfect_price_amount()
        print('重复计算的价格',price, amount, time_data)

        i+=1
    # 重复计算5次仍然失败，则吃小单,并把中心价格切换到买一卖一中间
    z = 0
    while price is None and z<10:
        print('重复计算下单价格失败，准备吃单')
        marker.eat_small_order()
        # marker.center_price = marker.bid_asks_price_center
        price, amount, time_data = marker.get_perfect_price_amount()
        # 吃小单后，再计算8次，任然失败，则吃靠近中心价格的单子，并将中心价格调节到买一卖一中间
        if z > 8:
            marker.center_price = marker.bid_asks_price_center
            marker.price = marker.bid_asks_price_center
        z += 1
    # if price is None:
    # 十次计算下单失败，使用计算的随机数下单，会吃单
    # 多线程布单
    sell = threading.Thread(target=marker.add_entrust_sell())
    buy = threading.Thread(target=marker.add_entrust_buy())
    buy.start()
    sell.start()
    buy.join()
    sell.join()
    marker.safe_or = False
    time.sleep(0.5)
    # 布单结束后，查看订单状态，判断是否进行撤单
    cancel_deal_sell = threading.Thread(target=marker.must_deal_sell, args=(marker.entrustId_sell,))
    cancel_deal_buy = threading.Thread(target=marker.must_deal_buy, args=(marker.entrustId_buy,))
    cancel_deal_sell.start()
    cancel_deal_buy.start()
    cancel_deal_sell.join()
    cancel_deal_buy.join()

    # timing = random.randint(marker.start_time,marker.start_time+5)
    print(time.localtime(time.time()),'睡眠时间是--------------------------------------------------->',marker.timing)
    # time.sleep(marker.timing)
    global baiwan
    baiwan = threading.Timer(marker.timing, run_threading, args=(marker,))
    baiwan.start()
    # 不能加join,会阻塞，造成线程堆积
    # baiwan.join()


if __name__ == '__main__':
    # 创建策略对象
    # input_price = input('请输入初始价格：')
    # if len(sys.argv) < 2:
    #     input_price = input('请输入初始价格：')
    # elif len(sys.argv) == 2:
    #     input_price = sys.argv[1]
    # marker = MarketMarkerOne(float(input_price))
    # run_threading(marker)
    # while True:
    #     baiwan = threading.Timer(marker.timing,run_threading, (marker,))
    #     baiwan.start()
        # baiwan.join()

    #　××××××××××××××××××××××　get_price_amount
    # data = marker.get_price_amount()
    # print(data)
    # print(marker.now_price)
    # print(marker.price)
    # print(marker.amount)
    # ********************** must_deal_all
    # marker.must_deal_all(entrustId='E6481360382693752832')



    pass
