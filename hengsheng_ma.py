import akshare as ak
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt  # 添加这行导入语句

# 获取恒生电子的日线数据
stock_code = "600570"  # 恒生电子的股票代码
df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")

# 打印列名以查看实际的数据结构
print("原始数据列名:", df.columns.tolist())

# 处理数据格式 - 根据实际的数据列进行映射
df = df.rename(columns={
    '日期': 'Date',
    '股票代码': 'Code',
    '开盘': 'Open',
    '收盘': 'Close',
    '最高': 'High',
    '最低': 'Low',
    '成交量': 'Volume',
    '成交额': 'Amount',
    '振幅': 'Amplitude',
    '涨跌幅': 'PctChg',
    '涨跌额': 'Change',
    '换手率': 'Turnover'
})

# 删除不需要的列
df = df.drop(['Code', 'Turnover'], axis=1)

df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# 计算60日均线
# 先获取最后120天的数据，再计算均线
df_plot = df.tail(120).copy()
df_plot['MA60'] = df['Close'].rolling(window=60).mean().tail(120)

# 设置绘图样式
my_style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.family': 'SimHei'})

# 添加判断对子数的函数
def is_double_number(price):
    # 转换为字符串并保留2位小数
    price_str = f"{price:.2f}"
    # 判断最后两位是否相同或为00
    return price_str[-2:] == '00' or price_str[-2] == price_str[-1]

# 添加均线
add_plot = [
    mpf.make_addplot(df_plot['MA60'], color='red', width=0.7)
]

# 绘制K线图
fig, axes = mpf.plot(df_plot,
                    type='candle',
                    title='恒生电子日K线图 (含60日均线)',
                    volume=True,
                    addplot=add_plot,
                    style=my_style,
                    figsize=(15, 8),
                    returnfig=True)

# 在图上添加价格标注
ax = axes[0]
for idx, row in df_plot.iterrows():
    x_pos = len(df_plot.loc[:idx])-1
    offset = (row['High'] - row['Low']) * 0.03  # 增加偏移量
    
    # 检查并标注高价
    if is_double_number(row['High']):
        ax.text(x_pos, row['High'] + offset, f'H:{row["High"]:.2f}', 
                ha='center', va='bottom', fontsize=9, alpha=1.0,
                bbox=dict(facecolor='white', edgecolor='red', alpha=0.7, pad=1))
    
    # 检查并标注低价
    if is_double_number(row['Low']):
        ax.text(x_pos, row['Low'] - offset, f'L:{row["Low"]:.2f}', 
                ha='center', va='top', fontsize=9, alpha=1.0,
                bbox=dict(facecolor='white', edgecolor='green', alpha=0.7, pad=1))
    
    # 检查并标注开盘价
    if is_double_number(row['Open']):
        ax.text(x_pos - 0.4, row['Open'], f'O:{row["Open"]:.2f}', 
                ha='right', va='center', fontsize=9, alpha=1.0,
                bbox=dict(facecolor='white', edgecolor='blue', alpha=0.7, pad=1))
    
    # 检查并标注收盘价
    if is_double_number(row['Close']):
        ax.text(x_pos + 0.4, row['Close'], f'C:{row["Close"]:.2f}', 
                ha='left', va='center', fontsize=9, alpha=1.0,
                bbox=dict(facecolor='white', edgecolor='purple', alpha=0.7, pad=1))

plt.show()