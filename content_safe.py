# 测试账号，17630636381

# api_key = '3e9e9898-8d95-49ce-933e-af37deda9754'
# secret_key = '672164bc63180216b9f5a1dfb8e342ca830fcbb1'

url = 'https://www.bqopen.com/page/docs/exchange'

# 上涨和下跌的模式
parameters = [[-0.0002, 0.0015], [-0.00015, 0.008], [-0.00005, 0.0005], [0, 0.001], [0, 0.0006],
                      [0, 0.0004], [0.00005, 0.0005], [0.00015, 0.008], [0.0002, 0.0015]]


BID_ASK_SPREAD_HALF = 0.975


# 随机order 的币种数量
ORDER_AMOUNT_MIN = 200
ORDER_AMOUNT_MAX = 1500
# 随机下一单等待时间
TIMING_MIN = 3
TIMING_MAX = 10

# 被吃单 随机order的币种数量
EATEN_ORDER_AMOUNT_MIN = 200
EATEN_ORDER_AMOUNT_MAX = 600
# 被吃单 随机下一单等待时间
EATEN_TIMING_MIN = 20
EATEN_TIMING_MAX = 90