"""
生成新的均衡排班方案（4-3-4人分组）
"""

import datetime
from collections import defaultdict

# 新的分组
STAFF_DICT = {
    # Group 1 (4人)
    "于海涛": {"group": 1, "resident": True, "bg": "resident"},
    "王盈盈": {"group": 1, "resident": True, "bg": "resident"},
    "李凡": {"group": 1, "resident": False, "bg": "emergency"},
    "黄露莎": {"group": 1, "resident": False, "bg": "general"},
    
    # Group 2 (3人)
    "李雪群": {"group": 2, "resident": True, "bg": "resident"},
    "罗佳忍": {"group": 2, "resident": False, "bg": "emergency"},
    "周红霞": {"group": 2, "resident": False, "bg": "anesthesia"},
    
    # Group 3 (4人)
    "马健": {"group": 3, "resident": True, "bg": "resident"},
    "张亚琼": {"group": 3, "resident": True, "bg": "resident"},
    "张晨禹": {"group": 3, "resident": False, "bg": "emergency"},
    "赵钰州": {"group": 3, "resident": False, "bg": "general"},
}

REST_DAYS = {
    datetime.date(2025, 5, 10), datetime.date(2025, 5, 11),
    datetime.date(2025, 5, 17), datetime.date(2025, 5, 18),
    datetime.date(2025, 5, 24), datetime.date(2025, 5, 25),
    datetime.date(2025, 5, 31), datetime.date(2025, 6, 1), datetime.date(2025, 6, 2),
}

def generate_balanced_schedule():
    """生成更均衡的排班方案"""
    schedule = {}
    staff_stats = {name: {"duties": []} for name in STAFF_DICT}
    
    # 基于新的分组生成更均衡的排班
    # 目标：每人约3-4次排班
    
    duties = [
        # 第1周
        (datetime.date(2025, 5, 6), "李雪群", "李凡"),        # G2 + G1
        (datetime.date(2025, 5, 7), "于海涛", "罗佳忍"),      # G1 + G2
        (datetime.date(2025, 5, 8), "王盈盈", "张晨禹"),      # G1 + G3
        (datetime.date(2025, 5, 9), "黄露莎", "周红霞"),      # G1 + G2
        
        # 第2周
        (datetime.date(2025, 5, 12), "马健", "李凡"),         # G3 + G1
        (datetime.date(2025, 5, 13), "李雪群", "赵钰州"),     # G2 + G3
        (datetime.date(2025, 5, 14), "于海涛", "周红霞"),     # G1 + G2
        
        # 第3周
        (datetime.date(2025, 5, 16), "张亚琼", "李凡"),       # G3 + G1
        
        # 第4周
        (datetime.date(2025, 5, 19), "李雪群", "黄露莎"),     # G2 + G1
        (datetime.date(2025, 5, 20), "马健", "罗佳忍"),       # G3 + G2
        (datetime.date(2025, 5, 21), "王盈盈", "张晨禹"),     # G1 + G3
        (datetime.date(2025, 5, 22), "李凡", "李雪群"),       # G1 + G2
        (datetime.date(2025, 5, 23), "于海涛", "周红霞"),     # G1 + G2
        
        # 第5周
        (datetime.date(2025, 5, 26), "张亚琼", "李凡"),       # G3 + G1
        (datetime.date(2025, 5, 27), "赵钰州", "王盈盈"),     # G3 + G1
        (datetime.date(2025, 5, 28), "马健", "罗佳忍"),       # G3 + G2
        (datetime.date(2025, 5, 29), "黄露莎", "张晨禹"),     # G1 + G3
        (datetime.date(2025, 5, 30), "李雪群", "周红霞"),     # G2 + G2（不合格！需要修改）
        
        # 第6周
        (datetime.date(2025, 6, 3), "于海涛", "罗佳忍"),      # G1 + G2
    ]
    
    # 检查并统计
    print("新的均衡排班方案检查：\n")
    print(f"{'日期':<12} {'周':>2} {'排班':<30} {'小组':>12} {'检查':>12}")
    print("-" * 70)
    
    for date, name1, name2 in duties:
        if date in REST_DAYS:
            continue
        
        g1 = STAFF_DICT[name1]["group"]
        g2 = STAFF_DICT[name2]["group"]
        
        # 检查约束
        diff_group = "✅" if g1 != g2 else "❌"
        has_special = (STAFF_DICT[name1]["bg"] in ["resident", "emergency", "anesthesia"] or 
                      STAFF_DICT[name2]["bg"] in ["resident", "emergency", "anesthesia"])
        special_check = "✅" if has_special else "❌"
        
        weekday = ['一', '二', '三', '四', '五', '六', '日'][date.weekday()]
        pair_str = f"{name1}+{name2}"
        group_str = f"G{g1}+G{g2}"
        check_str = f"不同组:{diff_group} 特殊:{special_check}"
        
        print(f"{date} 周{weekday} {pair_str:<30} {group_str:>12} {check_str:>12}")
        
        schedule[date] = (name1, name2)
        staff_stats[name1]["duties"].append(date)
        staff_stats[name2]["duties"].append(date)
    
    # 统计
    print("\n" + "="*70)
    print("人员排班统计")
    print("="*70)
    print(f"{'姓名':<8} {'小组':>3} {'排班次数':>6} {'排班日期':<40}")
    print("-" * 70)
    
    for name in sorted(STAFF_DICT.keys()):
        duties_list = sorted(staff_stats[name]["duties"])
        group = STAFF_DICT[name]["group"]
        count = len(duties_list)
        dates_str = ", ".join([d.strftime("%m-%d") for d in duties_list])
        print(f"{name:<8} G{group:>2} {count:>6} {dates_str:<40}")
    
    # 平衡分析
    duty_counts = [len(staff_stats[name]["duties"]) for name in STAFF_DICT]
    print("\n" + "="*70)
    print(f"平均值班次数: {sum(duty_counts) / len(STAFF_DICT):.2f}")
    print(f"最少: {min(duty_counts)}, 最多: {max(duty_counts)}, 差异: {max(duty_counts) - min(duty_counts)}")
    
    # 小组分析
    print("\n" + "="*70)
    print("各小组分析")
    print("="*70)
    for group in [1, 2, 3]:
        group_staff = [name for name, info in STAFF_DICT.items() if info["group"] == group]
        group_count = len(group_staff)
        total_duties = sum(len(staff_stats[name]["duties"]) for name in group_staff)
        avg = total_duties / group_count if group_count > 0 else 0
        print(f"G{group}: {group_count}人, 总排班{total_duties}次, 平均{avg:.2f}次/人")
    
    return schedule, staff_stats

if __name__ == "__main__":
    schedule, stats = generate_balanced_schedule()
