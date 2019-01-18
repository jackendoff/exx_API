import time

from exx_api import ExxApi


class ChargeDataFormat(object):
    '''
    处理kryptono交易所返回的数据格式，提供正确格式，容错
    处理流程输入log文件
    '''
    def __init__(self):
        # 初始化公共接口和私有接口对象
        self.coin_name = 'eth_usdt'
        self.exx_api = ExxApi(self.coin_name)

        pass

    def charge_get_trades(self):
        # 获取最新成交价格
        # data_status = False
        try:
            data = self.exx_api.all_tickers()
            last_price = data['eth_usdt']['last']
        except Exception as err:
            print('获取最新价格，连接服务器失败',err)
            # logging.info('获取最新价格，连接服务器失败')
            data = self.charge_get_trades()
            return data
        return last_price  # str

    def charge_get_entrusts(self):
        # 获取订单簿数据,返回买一卖一的数据列表,市场深度
        try:
            data = self.exx_api.get_depth(self.coin_name)
        except Exception as err:
            print('获取买一卖一数据，连接服务器失败')
            # logging.info('获取买一卖一数据，连接服务器失败')
            data = self.charge_get_entrusts()
            return data
        # 卖一价格，数量
        asks_list_min = data['asks'][-1]
        # 买一价格，数量
        bids_list_max = data['bids'][0]
        return [asks_list_min,bids_list_max]

    def charge_add_entrust_buy(self,price,amount):
        # 新增委托（买单）买单 price=0.0728
        params = {
            'price':price,
            'amount':amount,
            'type':'buy',
        }
        try:
            data = self.exx_api.get_order(**params)
        except Exception as err:
            print('新增委托单（买单）连接服务器失败', err)
            # 服务器正常，但创建委托单失败，则重复创建
            data = self.charge_add_entrust_buy(price, amount)
            return data
        print(data)
        return data['id']

    def charge_add_entrust_sell(self,price,amount):
        # 新增委托（卖单） price=0.0728
        params = {
            'price': price,
            'amount': amount,
            'type': 'sell',
        }
        try:
            data = self.exx_api.get_order(**params)
        except Exception as err:
            print('新增委托单（卖单）连接服务器失败', err)
            # 服务器正常，但创建委托单失败，则重复创建
            data = self.charge_add_entrust_buy(price, amount)
            return data
        return data['id']

    def change_cancle_entrust(self,entrustId):
        # 取消委托单
        params = {
            'id':entrustId,
        }

        try:
            data = self.exx_api.get_cancel(**params)
        except Exception as err:
            print('取消委托单连接服务器失败',err)
            # logging.info('取消委托单连接服务器失败%s'%err)
            # 连接服务器失败，重新连接
            data = self.change_cancle_entrust(entrustId)
            return data
        # code:100表示取消成功
        return data['code']

    # 通过成交id获取成交状况
    def charge_get_entrust_by_id(self,entrustId):

        params = {
            'id':entrustId,
        }
        try:
            data = self.exx_api.get_order_data(**params)
        except Exception as err:
            print('委托单详情连接服务器失败',err)
            time.sleep(1)
            # logging.error('委托单详情连接服务器失败',err)
            # 连接服务器失败，重新连接
            data = self.charge_get_entrust_by_id(entrustId)
            return data
        # status 0,1,2,3,   2成交完成
        return data['status']

# 没有成交记录
    # def charge_get_user_entrust_list(self):
    #     # 获取自己最近成交的价格,完成订单
    #     params = {
    #         'symbol':'SWC_ETH'
    #     }
    #     try:
    #         data = self.exx_api.get_orders_data(**params)
    #         # print(data)
    #     except Exception as err:
    #         print('获取自己最新成交价格失败')
    #         # logging.error('获取自己最新成交价格失败')
    #         data = self.charge_get_user_entrust_list()
    #         return data
    #     return data['price']


if __name__ == '__main__':

    charge_data = ChargeDataFormat()
    # 获取所有行情
    # data = charge_data.charge_get_trades()
    # print(data,type(data))
    # 市场深度
    # data = charge_data.charge_get_entrusts()
    # print(data,type(data))
    # 买单
    # data = charge_data.charge_add_entrust_buy(price=,amount=)
    # print(data,type(data))
    # 卖单
    # data = charge_data.charge_add_entrust_sell(price=165,amount=1)
    # print(data,type(data))
    # 取消订单
    # data = charge_data.change_cancle_entrust(data)
    # print(data,type(data))
    # 获取订单详情
    data = charge_data.charge_get_entrust_by_id('68054807')
    print(data,type(data))