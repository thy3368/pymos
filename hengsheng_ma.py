import akshare as ak
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt  # 添加这行导入语句
from matplotlib.widgets import CheckButtons

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
my_style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.family': ['Heiti TC', 'Arial Unicode MS', 'sans-serif']})

# 添加判断对子数的函数
def is_double_number(price):
    # 转换为字符串并保留2位小数
    price_str = f"{price:.2f}"
    # 判断最后两位是否相同或为00
    return price_str[-2:] == '00' or price_str[-2] == price_str[-1]

# 添加价格显示配置
price_display_config = {
    'show_high': True,    # 是否显示最高价
    'show_low': True,     # 是否显示最低价
    'show_open': False,   # 是否显示开盘价
    'show_close': False   # 是否显示收盘价
}

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
last_positions = {}  # 记录上一个标注的位置

for idx, row in df_plot.iterrows():
    x_pos = len(df_plot.loc[:idx])-1
    price_range = row['High'] - row['Low']
    offset = price_range * 0.03
    
    # 创建价格标注列表
    price_labels = []
    if price_display_config['show_high'] and is_double_number(row['High']):
        price_labels.append(('H', row['High'], 'top', 'red'))
    if price_display_config['show_low'] and is_double_number(row['Low']):
        price_labels.append(('L', row['Low'], 'bottom', 'green'))
    if price_display_config['show_open'] and is_double_number(row['Open']):
        price_labels.append(('O', row['Open'], 'left', 'blue'))
    if price_display_config['show_close'] and is_double_number(row['Close']):
        price_labels.append(('C', row['Close'], 'right', 'purple'))
    
    # 对价格标注按价格排序
    price_labels.sort(key=lambda x: x[1])
    
    # 计算标注间距
    min_gap = price_range * 0.02
    
    # 添加价格标注
    for i, (label, price, pos, color) in enumerate(price_labels):
        # 计算y轴位置，避免重叠
        y_pos = price
        if i > 0 and abs(y_pos - price_labels[i-1][1]) < min_gap:
            y_pos = price_labels[i-1][1] + min_gap
        
        # 根据位置类型设置不同的x偏移
        x_offset = 0
        if pos == 'left':
            x_offset = -0.4
            ha = 'right'
        elif pos == 'right':
            x_offset = 0.4
            ha = 'left'
        else:
            ha = 'center'
        
        ax.text(x_pos + x_offset, y_pos, f'{label}:{price:.2f}', 
                ha=ha, va='center', fontsize=9, alpha=1.0,
                bbox=dict(facecolor='white', edgecolor=color, alpha=0.7, pad=1))

# 绘制K线图后，添加复选框控件
def update_display(label):
    # 更新配置
    if label == '最高价':
        price_display_config['show_high'] = not price_display_config['show_high']
    elif label == '最低价':
        price_display_config['show_low'] = not price_display_config['show_low']
    elif label == '开盘价':
        price_display_config['show_open'] = not price_display_config['show_open']
    elif label == '收盘价':
        price_display_config['show_close'] = not price_display_config['show_close']
    
    # 清除原有标注
    for text in ax.texts[:]:
        text.remove()
    
    # 重新绘制价格标注
    for idx, row in df_plot.iterrows():
        x_pos = len(df_plot.loc[:idx])-1
        price_range = row['High'] - row['Low']
        offset = price_range * 0.03
        
        # 创建价格标注列表
        price_labels = []
        if price_display_config['show_high'] and is_double_number(row['High']):
            price_labels.append(('H', row['High'], 'top', 'red'))
        if price_display_config['show_low'] and is_double_number(row['Low']):
            price_labels.append(('L', row['Low'], 'bottom', 'green'))
        if price_display_config['show_open'] and is_double_number(row['Open']):
            price_labels.append(('O', row['Open'], 'left', 'blue'))
        if price_display_config['show_close'] and is_double_number(row['Close']):
            price_labels.append(('C', row['Close'], 'right', 'purple'))
        
        # 对价格标注按价格排序
        price_labels.sort(key=lambda x: x[1])
        
        # 计算标注间距
        min_gap = price_range * 0.02
        
        # 添加价格标注
        for i, (label, price, pos, color) in enumerate(price_labels):
            # 计算y轴位置，避免重叠
            y_pos = price
            if i > 0 and abs(y_pos - price_labels[i-1][1]) < min_gap:
                y_pos = price_labels[i-1][1] + min_gap
            
            # 根据位置类型设置不同的x偏移
            x_offset = 0
            if pos == 'left':
                x_offset = -0.4
                ha = 'right'
            elif pos == 'right':
                x_offset = 0.4
                ha = 'left'
            else:
                ha = 'center'
            
            ax.text(x_pos + x_offset, y_pos, f'{label}:{price:.2f}', 
                    ha=ha, va='center', fontsize=9, alpha=1.0,
                    bbox=dict(facecolor='white', edgecolor=color, alpha=0.7, pad=1))
    
    plt.draw()

# 添加复选框
plt.subplots_adjust(right=0.85)  # 为复选框留出空间
rax = plt.axes([0.87, 0.5, 0.12, 0.15])
labels = ['最高价', '最低价', '开盘价', '收盘价']
visibility = [price_display_config['show_high'], 
             price_display_config['show_low'],
             price_display_config['show_open'], 
             price_display_config['show_close']]
check = CheckButtons(rax, labels, visibility)
check.on_clicked(update_display)

plt.show()