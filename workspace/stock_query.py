import yfinance as yf
import json

# 获取百度股票信息
bidu = yf.Ticker('BIDU')
info = bidu.info

print('百度(BIDU)股票信息:')
print('=' * 30)

# 显示关键信息
key_info = {
    '当前价格': info.get('currentPrice', 'N/A'),
    '今日涨跌': info.get('regularMarketChange', 'N/A'),
    '涨跌幅': info.get('regularMarketChangePercent', 'N/A'),
    '开盘价': info.get('regularMarketOpen', 'N/A'),
    '最高价': info.get('dayHigh', 'N/A'),
    '最低价': info.get('dayLow', 'N/A'),
    '成交量': info.get('volume', 'N/A'),
    '市值': info.get('marketCap', 'N/A'),
    '52周最高': info.get('fiftyTwoWeekHigh', 'N/A'),
    '52周最低': info.get('fiftyTwoWeekLow', 'N/A')
}

for key, value in key_info.items():
    if key in ['当前价格', '今日涨跌', '开盘价', '最高价', '最低价']:
        print(f'{key}: ${value}')
    elif key == '涨跌幅':
        print(f'{key}: {value}%')
    elif key == '市值':
        # 格式化市值显示
        if isinstance(value, (int, float)):
            if value >= 1e9:
                print(f'{key}: ${value/1e9:.2f}B')
            elif value >= 1e6:
                print(f'{key}: ${value/1e6:.2f}M')
            else:
                print(f'{key}: ${value}')
        else:
            print(f'{key}: {value}')
    else:
        print(f'{key}: {value}')