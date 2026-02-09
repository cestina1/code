"""
A股数据爬取程序
功能：爬取今日A股实时行情和基本面数据，输出为CSV格式
使用akshare库获取数据（基于东方财富等公开数据源）
"""

import pandas as pd
import akshare as ak
from datetime import datetime
import os


def get_a_stock_list():
    """获取所有A股股票列表"""
    print("正在获取A股股票列表...")
    try:
        # 获取A股所有股票代码和名称
        stock_df = ak.stock_zh_a_spot_em()
        print(f"成功获取 {len(stock_df)} 只A股股票")
        return stock_df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None


def get_realtime_quotes():
    """获取A股实时行情数据"""
    print("正在获取实时行情数据...")
    try:
        # 获取东方财富实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 选择需要的列
        columns = {
            '代码': '股票代码',
            '名称': '股票名称',
            '最新价': '最新价',
            '涨跌幅': '涨跌幅(%)',
            '涨跌额': '涨跌额',
            '成交量': '成交量(手)',
            '成交额': '成交额(元)',
            '振幅': '振幅(%)',
            '最高': '最高价',
            '最低': '最低价',
            '今开': '今开价',
            '昨收': '昨收价',
            '量比': '量比',
            '换手率': '换手率(%)',
            '市盈率-动态': '市盈率(TTM)',
            '市净率': '市净率',
            '总市值': '总市值(元)',
            '流通市值': '流通市值(元)',
            '涨速': '涨速(%)',
            '5分钟涨跌': '5分钟涨跌(%)',
            '60日涨跌幅': '60日涨跌幅(%)',
            '年初至今涨跌幅': '年初至今涨跌幅(%)'
        }
        
        # 重命名列
        df = df.rename(columns=columns)
        
        # 添加数据更新时间
        df['数据更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"成功获取 {len(df)} 条实时行情数据")
        return df
        
    except Exception as e:
        print(f"获取实时行情数据失败: {e}")
        return None


def get_fundamental_data():
    """获取基本面数据"""
    print("正在获取基本面数据...")
    try:
        # 获取A股基本财务指标
        df = ak.stock_zh_a_spot_em()
        
        # 基本面相关列已在实时行情中包含，这里进行整理
        fundamental_cols = [
            '股票代码', '股票名称', '市盈率(TTM)', '市净率', 
            '总市值(元)', '流通市值(元)', '换手率(%)', '量比',
            '60日涨跌幅(%)', '年初至今涨跌幅(%)'
        ]
        
        print(f"成功获取 {len(df)} 条基本面数据")
        return df
        
    except Exception as e:
        print(f"获取基本面数据失败: {e}")
        return None


def merge_and_export():
    """合并数据并导出为CSV"""
    # 获取实时行情数据（已包含基本面数据）
    df = get_realtime_quotes()
    
    if df is None:
        print("数据获取失败，程序退出")
        return
    
    # 整理数据顺序
    columns_order = [
        '股票代码', '股票名称', '最新价', '涨跌幅(%)', '涨跌额',
        '今开价', '最高价', '最低价', '昨收价',
        '成交量(手)', '成交额(元)', '换手率(%)', '量比',
        '振幅(%)', '涨速(%)', '5分钟涨跌(%)',
        '市盈率(TTM)', '市净率',
        '总市值(元)', '流通市值(元)',
        '60日涨跌幅(%)', '年初至今涨跌幅(%)',
        '数据更新时间'
    ]
    
    # 确保所有列都存在
    available_cols = [col for col in columns_order if col in df.columns]
    df = df[available_cols]
    
    # 生成文件名
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"A股数据_{date_str}.csv"
    
    # 导出到CSV
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n数据已成功导出到: {os.path.abspath(filename)}")
        print(f"共导出 {len(df)} 条记录")
        
        # 显示数据统计
        print("\n数据统计:")
        print(f"  - 上涨股票数: {len(df[df['涨跌幅(%)'] > 0])}")
        print(f"  - 下跌股票数: {len(df[df['涨跌幅(%)'] < 0])}")
        print(f"  - 平盘股票数: {len(df[df['涨跌幅(%)'] == 0])}")
        
        if '市盈率(TTM)' in df.columns:
            pe_valid = df[df['市盈率(TTM)'] > 0]['市盈率(TTM)']
            if len(pe_valid) > 0:
                print(f"  - 平均市盈率: {pe_valid.mean():.2f}")
        
        # 显示前10条数据
        print("\n前10条数据预览:")
        print(df.head(10).to_string())
        
    except Exception as e:
        print(f"导出CSV失败: {e}")


def main():
    """主函数"""
    print("="*60)
    print("A股数据爬取程序")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 检查依赖
    try:
        import akshare
        import pandas
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请安装依赖: pip install akshare pandas")
        return
    
    print("\n开始爬取数据...\n")
    
    # 执行爬取和导出
    merge_and_export()
    
    print("\n" + "="*60)
    print(f"程序执行完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


if __name__ == "__main__":
    main()
