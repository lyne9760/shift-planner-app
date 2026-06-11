"""
排班系统 - 生成 Excel 输出版本
"""

import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from pathlib import Path

# ============ 排班数据 ============

STAFF_DICT = {
    # Group 1
    "于海涛": {"group": 1, "resident": True, "bg": "resident"},
    "王盈盈": {"group": 1, "resident": True, "bg": "resident"},
    "李凡": {"group": 1, "resident": False, "bg": "emergency"},
    "黄露莎": {"group": 1, "resident": False, "bg": "general"},
    "赵钰州": {"group": 1, "resident": False, "bg": "general"},
    
    # Group 2
    "李雪群": {"group": 2, "resident": True, "bg": "resident"},
    "罗佳忍": {"group": 2, "resident": False, "bg": "emergency"},
    "周红霞": {"group": 2, "resident": False, "bg": "anesthesia"},
    
    # Group 3
    "马健": {"group": 3, "resident": True, "bg": "resident"},
    "张亚琼": {"group": 3, "resident": True, "bg": "resident"},
    "张晨禹": {"group": 3, "resident": False, "bg": "emergency"},
}

# 固定排班（已知的二线排班）
FIXED_DUTIES = {
    datetime.date(2025, 5, 5): ("李思", "待定"),   # 需要验证
    datetime.date(2025, 5, 15): ("李思", "待定"),
    datetime.date(2025, 5, 25): ("李思", "待定"),
}

# 休息日
REST_DAYS = {
    datetime.date(2025, 5, 10), datetime.date(2025, 5, 11),
    datetime.date(2025, 5, 17), datetime.date(2025, 5, 18),
    datetime.date(2025, 5, 24), datetime.date(2025, 5, 25),
    datetime.date(2025, 5, 31), datetime.date(2025, 6, 1), datetime.date(2025, 6, 2),
}


class ScheduleData:
    """排班数据结构"""
    
    def __init__(self):
        self.schedule = {}  # {date: (name1, name2)}
        self.stats = {name: {
            "group": info["group"],
            "resident": info["resident"],
            "background": info["bg"],
            "duties": [],
            "duty_count": 0,
            "weekend_count": 0,
            "friday_count": 0,
            "min_gap": float('inf'),
        } for name, info in STAFF_DICT.items()}
    
    def add_duty(self, date: datetime.date, name1: str, name2: str):
        """添加排班"""
        if date not in self.schedule:
            self.schedule[date] = (name1, name2)
            self.stats[name1]["duties"].append(date)
            self.stats[name1]["duty_count"] += 1
            self.stats[name2]["duties"].append(date)
            self.stats[name2]["duty_count"] += 1
            
            # 计数特殊日期
            if date.weekday() >= 4:  # 周五-周日
                self.stats[name1]["weekend_count"] += 1
                self.stats[name2]["weekend_count"] += 1
            if date.weekday() == 4:  # 周五
                pass  # 这里可以单独计数周五
    
    def export_schedule_dict(self):
        """导出排班字典"""
        result = {}
        for date, (name1, name2) in sorted(self.schedule.items()):
            result[date.strftime("%Y-%m-%d")] = [name1, name2]
        return result
    
    def export_stats(self):
        """导出统计数据"""
        result = {}
        for name, stats in sorted(self.stats.items(), key=lambda x: x[0]):
            result[name] = {
                "小组": stats["group"],
                "进修": "是" if stats["resident"] else "否",
                "背景": stats["background"],
                "值班次数": stats["duty_count"],
                "周末次数": stats["weekend_count"],
                "值班日期": [d.strftime("%Y-%m-%d") for d in sorted(stats["duties"])],
            }
        return result


def generate_schedule() -> ScheduleData:
    """生成排班表"""
    schedule = ScheduleData()
    
    # 手动设置排班方案（基于贪心算法的初始方案）
    duties = [
        # 5月份
        (datetime.date(2025, 5, 6), "李雪群", "李凡"),
        (datetime.date(2025, 5, 7), "于海涛", "罗佳忍"),
        (datetime.date(2025, 5, 8), "李雪群", "张晨禹"),
        (datetime.date(2025, 5, 9), "王盈盈", "周红霞"),
        
        (datetime.date(2025, 5, 12), "马健", "李凡"),
        (datetime.date(2025, 5, 13), "李雪群", "赵钰州"),
        (datetime.date(2025, 5, 14), "于海涛", "周红霞"),
        
        (datetime.date(2025, 5, 16), "张亚琼", "李凡"),
        
        (datetime.date(2025, 5, 19), "李雪群", "黄露莎"),
        (datetime.date(2025, 5, 20), "马健", "罗佳忍"),
        (datetime.date(2025, 5, 21), "王盈盈", "李凡"),
        (datetime.date(2025, 5, 22), "李雪群", "李凡"),
        (datetime.date(2025, 5, 23), "于海涛", "周红霞"),
        
        (datetime.date(2025, 5, 26), "张亚琼", "李凡"),
        (datetime.date(2025, 5, 27), "李雪群", "黄露莎"),
        (datetime.date(2025, 5, 28), "马健", "罗佳忍"),
        (datetime.date(2025, 5, 29), "王盈盈", "李凡"),
        (datetime.date(2025, 5, 30), "李雪群", "周红霞"),
        
        # 6月份
        (datetime.date(2025, 6, 3), "于海涛", "罗佳忍"),
    ]
    
    for date, name1, name2 in duties:
        if date not in REST_DAYS:
            schedule.add_duty(date, name1, name2)
    
    return schedule


def print_schedule(schedule: ScheduleData):
    """打印排班表"""
    print("=" * 100)
    print("2025年5月6日 - 6月3日 排班表")
    print("=" * 100)
    
    current = datetime.date(2025, 5, 6)
    end = datetime.date(2025, 6, 3)
    
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    
    print(f"{'日期':<12} {'周':>2} {'排班信息':<40} {'备注'}")
    print("-" * 100)
    
    while current <= end:
        day_name = weekdays[current.weekday()]
        date_str = current.strftime("%Y-%m-%d")
        
        if current in REST_DAYS:
            print(f"{date_str} 周{day_name} {'【休息日】':<40}")
        elif current in schedule.schedule:
            n1, n2 = schedule.schedule[current]
            info = f"{n1}(G{STAFF_DICT[n1]['group']}) + {n2}(G{STAFF_DICT[n2]['group']})"
            print(f"{date_str} 周{day_name} {info:<40}")
        else:
            print(f"{date_str} 周{day_name} {'【未排班】':<40}")
        
        current += datetime.timedelta(days=1)
    
    print("\n" + "=" * 100)
    print("人员排班统计")
    print("=" * 100)
    
    print(f"{'姓名':<8} {'小组':>2} {'进修':>2} {'背景':>6} {'总次数':>4} {'周末':>4} {'排班日期':<50}")
    print("-" * 100)
    
    for name in sorted(STAFF_DICT.keys()):
        stats = schedule.stats[name]
        dates_str = ", ".join([d.strftime("%m-%d") for d in sorted(stats["duties"])])
        resident = "是" if stats["resident"] else ""
        print(f"{name:<8} {stats['group']:>2} {resident:>2} {stats['background']:>6} {stats['duty_count']:>4} {stats['weekend_count']:>4} {dates_str:<50}")
    
    # 统计分析
    duty_counts = [schedule.stats[name]["duty_count"] for name in STAFF_DICT.keys()]
    print("\n" + "=" * 100)
    print("平衡分析")
    print("=" * 100)
    print(f"平均值班次数: {sum(duty_counts) / len(STAFF_DICT):.2f}")
    print(f"最少值班: {min(duty_counts)} 次")
    print(f"最多值班: {max(duty_counts)} 次")
    print(f"差异: {max(duty_counts) - min(duty_counts)} 次")
    
    # 人数统计
    print(f"\n各小组排班分析:")
    for group in [1, 2, 3]:
        group_staff = [name for name, info in STAFF_DICT.items() if info["group"] == group]
        avg_duties = sum(schedule.stats[name]["duty_count"] for name in group_staff) / len(group_staff)
        print(f"  第{group}小组: {len(group_staff)}人, 平均{avg_duties:.2f}次/人")


if __name__ == "__main__":
    print("\n🏥 医院排班系统 - 心胸外科ICU")
    print("=" * 100)
    print("\n生成排班数据...")
    
    schedule = generate_schedule()
    print_schedule(schedule)
    
    # 导出数据
    print("\n" + "=" * 100)
    print("导出排班数据...")
    print("=" * 100)
    
    schedule_dict = schedule.export_schedule_dict()
    stats_dict = schedule.export_stats()
    
    # 尝试导出 Excel
    try:
        import pandas as pd
        
        # 创建排班表
        schedule_rows = []
        current = datetime.date(2025, 5, 6)
        end = datetime.date(2025, 6, 3)
        weekdays_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        while current <= end:
            weekday = weekdays_cn[current.weekday()]
            date_str = current.strftime("%Y-%m-%d")
            
            if current in REST_DAYS:
                schedule_rows.append({
                    "日期": date_str,
                    "星期": weekday,
                    "一值人员": "【休息日】",
                    "小组搭配": "",
                })
            elif current in schedule.schedule:
                n1, n2 = schedule.schedule[current]
                g1 = STAFF_DICT[n1]["group"]
                g2 = STAFF_DICT[n2]["group"]
                schedule_rows.append({
                    "日期": date_str,
                    "星期": weekday,
                    "一值人员": f"{n1} + {n2}",
                    "小组搭配": f"G{g1} + G{g2}",
                })
            else:
                schedule_rows.append({
                    "日期": date_str,
                    "星期": weekday,
                    "一值人员": "未排班",
                    "小组搭配": "",
                })
            
            current += datetime.timedelta(days=1)
        
        # 创建人员统计表
        stats_rows = []
        for name in sorted(STAFF_DICT.keys()):
            stats = schedule.stats[name]
            stats_rows.append({
                "姓名": name,
                "小组": stats["group"],
                "进修": "是" if stats["resident"] else "否",
                "背景": stats["background"],
                "总次数": stats["duty_count"],
                "周末次数": stats["weekend_count"],
                "排班日期": "; ".join([d.strftime("%m-%d") for d in sorted(stats["duties"])]),
            })
        
        # 写入 Excel
        output_file = Path("c:/Users/msi/Desktop/cc/排班表_2025年5月.xlsx")
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            pd.DataFrame(schedule_rows).to_excel(writer, sheet_name="排班表", index=False)
            pd.DataFrame(stats_rows).to_excel(writer, sheet_name="人员统计", index=False)
            
            # 写入人员分组信息
            group_rows = []
            for name, info in sorted(STAFF_DICT.items(), key=lambda x: (x[1]["group"], x[0])):
                group_rows.append({
                    "姓名": name,
                    "小组": info["group"],
                    "进修": "是" if info["resident"] else "否",
                    "背景": info["bg"],
                })
            pd.DataFrame(group_rows).to_excel(writer, sheet_name="人员分组", index=False)
        
        print(f"✅ Excel 文件已生成: {output_file}")
    
    except ImportError:
        print("⚠️ pandas 库未安装，跳过 Excel 导出")
        print("要安装 pandas，请运行: pip install pandas openpyxl")
    
    print("\n✅ 排班系统执行完成")
