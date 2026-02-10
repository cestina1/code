"""
股票走势相似度分析 - DTW算法实现
功能：查询股票历史上与最近a小时走势最相似的时间段
"""

import akshare as ak
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from fastdtw import fastdtw
import warnings
warnings.filterwarnings('ignore')

# 配置 matplotlib 中文字体
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class StockPatternMatcher:
    """股票走势相似度匹配器"""
    
    def __init__(self, stock_code):
        """
        初始化
        
        参数:
            stock_code: 股票代码 (如: 600519, 000858)
        """
        self.stock_code = stock_code
        self.data = None
        
    def fetch_data(self, period='daily'):
        """
        获取股票历史数据
        
        参数:
            period: 数据周期 ('daily'=日K, 'weekly'=周K)
        """
        try:
            print(f"正在获取股票 {self.stock_code} 的历史数据...")
            
            # 判断是沪深股票还是指数
            if self.stock_code.startswith('6'):
                # 上海股票
                self.data = ak.stock_zh_a_hist(symbol=self.stock_code, period=period, 
                                               start_date="19900101", adjust="qfq")
            elif self.stock_code.startswith('0') or self.stock_code.startswith('3'):
                # 深圳股票/创业板
                self.data = ak.stock_zh_a_hist(symbol=self.stock_code, period=period,
                                               start_date="19900101", adjust="qfq")
            else:
                raise ValueError(f"不支持的股票代码格式: {self.stock_code}")
            
            # 数据处理
            self.data['日期'] = pd.to_datetime(self.data['日期'])
            self.data = self.data.sort_values('日期').reset_index(drop=True)
            
            # 计算归一化价格 (用于DTW比较)
            self.data['收盘价_归一'] = self.normalize_series(self.data['收盘'].values)
            
            print(f"成功获取 {len(self.data)} 条数据，时间范围: {self.data['日期'].min()} 至 {self.data['日期'].max()}")
            return True
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            return False
    
    @staticmethod
    def normalize_series(series):
        """将序列归一化到[0,1]范围"""
        min_val = np.min(series)
        max_val = np.max(series)
        if max_val == min_val:
            return np.zeros_like(series)
        return (series - min_val) / (max_val - min_val)
    
    @staticmethod
    def calculate_dtw_distance(pattern1, pattern2):
        """
        使用DTW算法计算两个序列的相似度距离
        距离越小表示越相似
        """
        distance, path = fastdtw(pattern1, pattern2)
        return distance, path
    
    def get_recent_pattern(self, a_hours):
        """
        获取最近a小时的价格走势
        
        参数:
            a_hours: 时间长度（小时）
        
        返回:
            pattern: 归一化后的价格序列
            start_idx: 起始索引
            end_idx: 结束索引
        """
        # 将小时转换为交易日数量（每天4小时交易时间）
        # A股每个交易日约4小时（9:30-11:30, 13:00-15:00）
        days_needed = max(1, int(np.ceil(a_hours / 4)))
        
        # 设置最小数据点数量，确保有足够的数据进行有意义的分析
        min_data_points = 20
        if days_needed < min_data_points:
            days_needed = min_data_points
            print(f"提示: 输入的时间长度对应交易日太少，自动调整为至少{min_data_points}个交易日（约{min_data_points * 4}小时）")
        
        if len(self.data) < days_needed:
            raise ValueError(f"数据不足，需要{days_needed}天数据，但只有{len(self.data)}天")
        
        end_idx = len(self.data) - 1
        start_idx = max(0, end_idx - days_needed + 1)
        
        # 获取收盘价并归一化
        pattern = self.data['收盘价_归一'].iloc[start_idx:end_idx+1].values
        
        return pattern, start_idx, end_idx
    
    def find_similar_patterns(self, a_hours, top_n=5, min_gap_days=30):
        """
        查找历史上与最近a小时走势最相似的时间段
        
        参数:
            a_hours: 最近a小时
            top_n: 返回最相似的N个时间段
            min_gap_days: 相似模式之间的最小间隔天数
        
        返回:
            相似时间段列表，按相似度排序
        """
        # 获取最近走势
        recent_pattern, recent_start, recent_end = self.get_recent_pattern(a_hours)
        pattern_length = len(recent_pattern)
        
        print(f"\n分析最近 {a_hours} 小时（约{pattern_length}个交易日）的走势...")
        
        # 搜索历史数据（排除最近30天，避免重复）
        search_end = recent_start - min_gap_days
        if search_end < pattern_length:
            raise ValueError(f"历史数据不足，无法找到相似模式")
        
        similarities = []
        
        print("正在搜索相似走势...")
        # 滑动窗口搜索
        for i in range(pattern_length - 1, search_end):
            # 获取历史窗口
            hist_start = i - pattern_length + 1
            hist_end = i + 1
            
            hist_pattern = self.data['收盘价_归一'].iloc[hist_start:hist_end].values
            
            # 计算DTW距离
            dtw_distance, path = self.calculate_dtw_distance(recent_pattern, hist_pattern)
            
            # 计算皮尔逊相关系数作为辅助指标
            correlation = np.corrcoef(recent_pattern, hist_pattern)[0, 1]
            
            # 综合评分 (距离越小越好，相关性越大越好)
            # 归一化距离到[0,1]，然后计算综合得分
            score = correlation * (1 / (1 + dtw_distance))
            
            similarities.append({
                'start_idx': hist_start,
                'end_idx': hist_end - 1,
                'start_date': self.data['日期'].iloc[hist_start],
                'end_date': self.data['日期'].iloc[hist_end - 1],
                'dtw_distance': dtw_distance,
                'correlation': correlation,
                'score': score,
                'pattern': hist_pattern
            })
        
        # 按DTW距离排序（距离越小越相似）
        similarities.sort(key=lambda x: x['dtw_distance'])
        
        # 使用非极大值抑制，确保返回的模式之间有一定间隔
        filtered_similarities = []
        used_ranges = []
        
        for sim in similarities:
            # 检查是否与已选模式重叠
            overlap = False
            for used_start, used_end in used_ranges:
                if not (sim['end_idx'] < used_start - min_gap_days or 
                        sim['start_idx'] > used_end + min_gap_days):
                    overlap = True
                    break
            
            if not overlap:
                filtered_similarities.append(sim)
                used_ranges.append((sim['start_idx'], sim['end_idx']))
                
                if len(filtered_similarities) >= top_n:
                    break
        
        return filtered_similarities, recent_pattern, recent_start, recent_end
    
    def visualize_results(self, similar_patterns, recent_pattern, recent_start, recent_end, a_hours):
        """
        可视化相似走势
        """
        n_patterns = len(similar_patterns)
        fig, axes = plt.subplots(n_patterns + 1, 1, figsize=(14, 3 * (n_patterns + 2)))
        
        if n_patterns == 0:
            axes = [axes]
        elif n_patterns == 1:
            axes = [axes[0], axes[1]]
        
        # 颜色方案
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        # 绘制最近走势
        ax = axes[0]
        x_recent = range(len(recent_pattern))
        ax.plot(x_recent, recent_pattern, 'b-', linewidth=2, label='最近走势', marker='o', markersize=4)
        ax.fill_between(x_recent, recent_pattern, alpha=0.3, color='blue')
        
        start_date = self.data['日期'].iloc[recent_start].strftime('%Y-%m-%d')
        end_date = self.data['日期'].iloc[recent_end].strftime('%Y-%m-%d')
        ax.set_title(f'最近 {a_hours} 小时走势 ({start_date} 至 {end_date})', fontsize=12, fontweight='bold')
        ax.set_ylabel('归一化价格', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(-0.1, 1.1)
        
        # 绘制相似走势
        for idx, pattern_info in enumerate(similar_patterns):
            ax = axes[idx + 1]
            color = colors[idx % len(colors)]
            
            x_hist = range(len(pattern_info['pattern']))
            ax.plot(x_hist, pattern_info['pattern'], color=color, linewidth=2, 
                   label='历史走势', marker='s', markersize=4)
            ax.fill_between(x_hist, pattern_info['pattern'], alpha=0.3, color=color)
            
            # 添加对比线
            ax.plot(x_recent, recent_pattern, 'b--', linewidth=1.5, alpha=0.6, label='最近走势')
            
            date_str = f"{pattern_info['start_date'].strftime('%Y-%m-%d')} 至 {pattern_info['end_date'].strftime('%Y-%m-%d')}"
            ax.set_title(f'相似度 #{idx+1}: {date_str}\nDTW距离: {pattern_info["dtw_distance"]:.4f}, 相关系数: {pattern_info["correlation"]:.4f}', 
                        fontsize=11, fontweight='bold')
            ax.set_ylabel('归一化价格', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_ylim(-0.1, 1.1)
        
        plt.suptitle(f'股票 {self.stock_code} 走势相似度分析', fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{self.stock_code}_similarity_analysis.png', dpi=150, bbox_inches='tight')
        print(f"\n图表已保存: {self.stock_code}_similarity_analysis.png")
        plt.show()
    
    def print_results(self, similar_patterns, a_hours):
        """
        打印分析结果
        """
        print("\n" + "="*80)
        print(f"股票 {self.stock_code} - 最近 {a_hours} 小时走势相似度分析结果")
        print("="*80)
        
        for idx, pattern in enumerate(similar_patterns, 1):
            print(f"\n【相似度排名 #{idx}】")
            print(f"  时间段: {pattern['start_date'].strftime('%Y-%m-%d')} 至 {pattern['end_date'].strftime('%Y-%m-%d')}")
            print(f"  DTW距离: {pattern['dtw_distance']:.6f} (越小越相似)")
            print(f"  相关系数: {pattern['correlation']:.4f}")
            print(f"  综合得分: {pattern['score']:.6f}")
            
            # 计算该时段后的表现
            end_idx = pattern['end_idx']
            if end_idx + 5 < len(self.data):
                future_return_5d = (self.data['收盘'].iloc[end_idx + 5] / 
                                   self.data['收盘'].iloc[end_idx] - 1) * 100
                print(f"  此后5日涨跌: {future_return_5d:+.2f}%")
            
            if end_idx + 20 < len(self.data):
                future_return_20d = (self.data['收盘'].iloc[end_idx + 20] / 
                                    self.data['收盘'].iloc[end_idx] - 1) * 100
                print(f"  此后20日涨跌: {future_return_20d:+.2f}%")
        
        print("\n" + "="*80)


def main():
    """
    主程序
    """
    print("="*80)
    print("股票走势相似度分析系统 (DTW算法)")
    print("="*80)
    print("\n说明: 本程序使用DTW(动态时间规整)算法，可以识别形状相似但可能有")
    print("      时间偏移或幅度差异的股票走势模式。")
    print("\n支持的股票代码格式:")
    print("  - 上海股票: 600xxx, 601xxx, 603xxx, 688xxx (科创板)")
    print("  - 深圳股票: 000xxx (主板), 002xxx (中小板), 300xxx (创业板)")
    print("="*80)
    
    # 获取用户输入
    stock_code = input("\n请输入股票代码 (如: 600519): ").strip()
    
    while True:
        try:
            a_hours = float(input("请输入时间长度a（小时）: ").strip())
            if a_hours <= 0:
                print("时间长度必须大于0，请重新输入。")
                continue
            break
        except ValueError:
            print("请输入有效的数字。")
    
    top_n = input("请输入要返回的相似模式数量 (默认5): ").strip()
    top_n = int(top_n) if top_n else 5
    
    # 创建分析器
    matcher = StockPatternMatcher(stock_code)
    
    # 获取数据
    if not matcher.fetch_data():
        print("数据获取失败，程序退出。")
        return
    
    try:
        # 查找相似模式
        similar_patterns, recent_pattern, recent_start, recent_end = \
            matcher.find_similar_patterns(a_hours, top_n=top_n)
        
        # 打印结果
        matcher.print_results(similar_patterns, a_hours)
        
        # 可视化
        print("\n正在生成可视化图表...")
        matcher.visualize_results(similar_patterns, recent_pattern, 
                                  recent_start, recent_end, a_hours)
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
