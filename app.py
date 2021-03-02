import pandas as pd
import os
import talib
from flask import Flask, render_template, request
from patterns import patterns

app = Flask(__name__)

# 将Tushare/万得格式的股票代码转换成sina API接受的股票代码格式
def translate_code(code_dot):
    digits, mkt = code_dot.split(sep='.')
    return mkt.lower() + digits

@app.route('/')
def index():
    # ==========【1】准备存储TA-lib形态指标扫描结果的dictionary==========
    stocks = dict()
    with open('data800_list.csv', encoding='utf-8') as f:
        for l in f.readlines()[1:]: # 跳过表头
            code, name, _ = l.split(sep=',')
            code = translate_code(code)
            stocks[code] = {'name': name}
    # ==========【2】获取网页端提交的TA-lib形态指标，扫描股票，存储结果==========
    pattern = request.args.get('pattern', None)
    if pattern:
        for f in os.listdir('./data800'):
            code = f.replace('.csv', '')
            code = translate_code(code)
            df = pd.read_csv(f'./data800/{f}')
            df.sort_values(by='trade_date', inplace=True)
            pattern_func = getattr(talib, pattern)
            result = pattern_func(df['open'], df['high'], df['low'], df['close'])
            last = result.iloc[-1]
            if last > 0:
                stocks[code][pattern] = '技术看涨'
            elif last < 0:
                stocks[code][pattern] = '技术看跌'
            else:
                stocks[code][pattern] = None
    # ==========【3】渲染网页模板index.html, 并将必要的变量传入，用于在网页端展示==========
    return render_template('index.html', patterns=patterns, stocks=stocks, curr_pattern=pattern)
