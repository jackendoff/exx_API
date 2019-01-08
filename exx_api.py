import requests
import hmac
import hashlib
import time

from content_safe_new import api_key,secret_key


class ExxApi(object):

    def __init__(self,coin_name,api_key,secret_key):
        self.coin_name = coin_name
        self.api_key = api_key
        self.secret_key = secret_key
        pass

    # 配置签名
    def get_sign(self,secret):
        return hmac.new(self.secret_key.encode("UTF-8"), secret.encode("utf-8"), hashlib.sha512).hexdigest()
        pass

    # 获取所有市场
    def all_market(self):
        url = 'https://api.exx.com/data/v1/markets'
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.all_market()
        return data

    # 获取所有行情
    def all_tickers(self):
        url = 'https://api.exx.com/data/v1/tickers'
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.all_market()
        return data

    # 获取市场行情，包含买一卖一
    def get_ticker(self,coin_name):
        url = 'https://api.exx.com/data/v1/ticker?currency='+coin_name
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_ticker(coin_name)
        return data

    # 市场深度
    def get_depth(self,coin_name=None):
        if coin_name is None:
            coin_name = self.coin_name
        url = 'https://api.exx.com/data/v1/depth?currency='+coin_name
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_depth(coin_name)
        return data

    # 获取历史成交
    def get_trades(self,coin_name=None):
        if coin_name is None:
            coin_name = self.coin_name
        url = 'https://api.exx.com/data/v1/trades?currency='+coin_name
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_trades(coin_name)
        return data

    # 获取k线数据
    def get_kline(self):
        url = 'https://api.exx.com/data/v1/klines?market='+self.coin_name+'&type=1min&size=1&assist=cny'
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_kline()
        return data

    # 委托下单
    def get_order(self,price,amount,type):
        price = str(price)
        amount = str(amount)
        secret = 'accesskey='+self.api_key+'&amount='+amount+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&price='+price+'&type='+type
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/order?accesskey='+self.api_key+'&amount='+amount+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&price='+price+'&type='+type+'&signature='+sign

        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_order(price,amount,type)
        return data
        pass

    # 取消委托
    def get_cancel(self,id):
        id = str(id)
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&id='+id+'&nonce='+str(int(time.time()*1000))
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/cancel?accesskey='+self.api_key+'&currency='+self.coin_name+'&id='+id+'&nonce='+str(int(time.time()*1000))+'&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_cancel(id)
        return data

    # 获取委托买单和卖单详情
    def get_order_data(self,id):
        id = str(id)
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&id='+id+'&nonce='+str(int(time.time()*1000))
        print(secret)
        sign = self.get_sign(secret)
        print(sign)
        url = 'https://trade.exx.com/api/getOrder?accesskey='+self.api_key+'&currency='+self.coin_name+'&id='+id+'&nonce='+str(int(time.time()*1000))+'&signature='+sign
        print(url)
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_order_data(id)
        return data

    # 获取多个委托卖单买单 10条
    def get_orders_data(self,type):
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&pageIndex=1&type='+type
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/getOpenOrders?accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&pageIndex=1&type='+type+'&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_orders_data(type)
        return data

    #　获取充值地址
    def get_charge_address(self):
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/getChargeAddress?accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_charge_address()
        return data
        pass

    # 获取充值记录
    def get_charge_record(self):
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/getChargeRecord?accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&pageIndex=1&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_charge_record()
        return data
        pass

    # 获取认证提币地址
    def get_withdraw(self):
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/getWithdrawAddress?accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_withdraw()
        return data

    # 获取提币记录
    def get_withdraw_record(self):
        secret = 'accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/getWithdrawRecord?accesskey='+self.api_key+'&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&pageIndex=1&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_withdraw()
        return data
        pass

    # 提币,子账号不允许提币
    def withdraw(self,address,pwd):
        secret = ''
        sign = self.get_sign(secret)
        url = 'https://trade.exx.com/api/withdraw?accesskey='+self.api_key+'&amount=10&currency='+self.coin_name+'&nonce='+str(int(time.time()*1000))+'&receiveAddr='+address+'&safePwd='+pwd+'&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.withdraw(address,pwd)
        return data

    # 获取用户信息 验证成功,其他接口没有进行验证，账户没有数据
    def get_balance(self):
        secret = 'accesskey='+self.api_key+'&nonce='+str(int(time.time()*1000))
        sign = self.get_sign(secret)
        url = ' https://trade.exx.com/api/getBalance?accesskey='+self.api_key+'&nonce='+str(int(time.time()*1000))+'&signature='+sign
        try:
            data = requests.get(url)
            data = data.json()
        except Exception:
            data = self.get_balance()
        return data
        pass


if __name__ == '__main__':

    #
    params = {
        'coin_name':'eth_usdt',
        'api_key':api_key,
        'secret_key':secret_key
    }
    exx = ExxApi(**params)

    # 获取账户信息
    # data = exx.get_balance()
    # 下单
    # params_data = {
    #     'price':165,
    #     'amount':1,
    #     'type':'sell'
    #
    # }
    # data = exx.get_order(**params_data)
    # print(data)

    # 取消委托单
    # params_data = {
    #     'id':65302439
    # }
    # data = exx.get_cancel(**params_data)
    # print(data)

    # 获取市场深度
    # data = exx.get_depth()
    # print(data)

    # 获取委托单详情
    # params_data = {
    #     'id':'65302432',
    # }
    # id = '65302050'
    # data = exx.get_order_data(id)
    # print(data)

    # 获取多个委托单详情
    params_data = {
        'type':'buy',
    }
    data = exx.get_orders_data(**params_data)
    print(data)

    # 获取成交历史
    # data = exx.get_trades()
    # print(data)

    # 获取充值地址
    # data = exx.get_charge_address()
    # print(data)

    pass
