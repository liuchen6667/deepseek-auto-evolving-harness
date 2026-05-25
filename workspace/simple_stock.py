import requests
import json
import time

# 尝试多个数据源
sources = [
    {
        'name': 'Alpha Vantage',
        'url': 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=BIDU&apikey=demo'
    },
    {
        'name': 'Financial Modeling Prep',
        'url': 'https://financialmodelingprep.com/api/v3/quote/BIDU?apikey=demo'
    }
]

print('尝试获取百度(BIDU)股价信息...')
print('=' * 40)

for source in sources:
    print(f'尝试从 {source["name"]} 获取数据...')
    try:
        response = requests.get(source['url'], timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f'成功从 {source["name"]} 获取数据:')
            print(json.dumps(data, indent=2))
            break
        else:
            print(f'HTTP错误: {response.status_code}')
    except Exception as e:
        print(f'错误: {e}')
    
    time.sleep(1)  # 避免请求过快

print('\n如果以上方法都失败，建议：')
print('1. 访问雅虎财经: https://finance.yahoo.com/quote/BIDU')
print('2. 访问谷歌财经: https://www.google.com/finance/quote/BIDU:NASDAQ')
print('3. 访问新浪财经: https://finance.sina.com.cn/realstock/company/bidu/nasdaq.shtml')