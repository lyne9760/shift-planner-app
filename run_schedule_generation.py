#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班系统 - 16人2组29天全排班生成器
所有天数都需要排班（包括原休息日）
简化版本 - 直接在此脚本中执行
"""

from datetime import datetime, timedelta
from collections import defaultdict
import json

# 第一小组 - 8人
GROUP_1 = [
    {"name": "于海涛", "type": "resident"},
    {"name": "王盈盈", "type": "resident"},
    {"name": "李凡", "type": "emergency"},
    {"name": "罗佳忍", "type": "emergency"},
    {"name": "周红霞", "type": "anesthesia"},
    {"name": "黄露莎", "type": "general"},
    {"name": "杨伟雄", "type": "general"},
    {"name": "赵钰州", "type": "general"},
]

# 第二小组 - 8人
GROUP_2 = [
    {"name": "李雪群", "type": "resident"},
    {"name": "马健", "type": "resident"},
    {"name": "张亚琼", "type": "resident"},
    {"name": "张晨禹", "type": "emergency"},
    {"name": "郭思华", "type": "anesthesia"},
    {"name": "王一鸣", "type": "general"},
    {"name": "杨清淇", "type": "general"},
    {"name": "侯佳伟", "type": "general"},
]

def has_special_background(staff):
    """检查员工是否有特殊背景（resident/emergency/anesthesia）"""
    return staff["type"] in ["resident", "emergency", "anesthesia"]

def generate_schedule():
    """生成29天排班表"""
    start_date = datetime(2025, 5, 6)
    schedule = {}
    
    # 追踪每个人的排班计数
    duty_count = {}
    for staff in GROUP_1 + GROUP_2:
        duty_count[staff["name"]] = 0
    
    # 追踪每个人的最后排班日期
    last_duty_date = {}
    for staff in GROUP_1 + GROUP_2:
        last_duty_date[staff["name"]] = None
    
    # 生成29天排班
    for day_offset in range(29):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][current_date.weekday()]
        
        # 找到每组中排班次数最少的人
        min_g1 = min(GROUP_1, key=lambda x: (duty_count[x["name"]], last_duty_date[x["name"]] or start_date))
        min_g2 = min(GROUP_2, key=lambda x: (duty_count[x["name"]], last_duty_date[x["name"]] or start_date))
        
        person1 = min_g1["name"]
        person2 = min_g2["name"]
        
        # 记录排班
        schedule[date_str] = {
            "date": date_str,
            "weekday": weekday,
            "person1": person1,
            "person2": person2,
            "group1": 1,
            "group2": 2,
        }
        
        # 更新排班计数和最后排班日期
        duty_count[person1] += 1
        duty_count[person2] += 1
        last_duty_date[person1] = current_date
        last_duty_date[person2] = current_date
    
    return schedule, duty_count

# 执行主逻辑
print("=" * 60)
print("生成29天排班表（包括休息日）")
print("=" * 60)

schedule, duty_count = generate_schedule()

# 显示排班统计
print("\n📊 排班统计：")
print("-" * 60)

sorted_duty = sorted(duty_count.items(), key=lambda x: x[1], reverse=True)
for person, count in sorted_duty:
    print(f"{person:12} : {count}天")

# 计算统计信息
duties = list(duty_count.values())
print(f"\n统计摘要：")
print(f"  总天数：29天")
print(f"  总排班对数：29")
print(f"  平均每人排班：{sum(duties)/len(duties):.2f}天")
print(f"  最少排班：{min(duties)}天")
print(f"  最多排班：{max(duties)}天")
print(f"  排班差异：{max(duties) - min(duties)}天")

# 显示前10天的排班
print("\n📅 前10天排班预览：")
print("-" * 60)
start_date = datetime(2025, 5, 6)
for i in range(min(10, len(schedule))):
    current_date = start_date + timedelta(days=i)
    date_str = current_date.strftime("%Y-%m-%d")
    shift = schedule[date_str]
    print(f"{date_str} {shift['weekday']:4} : {shift['person1']:8} + {shift['person2']:8}")

# 保存为JSON
output_data = {
    "metadata": {
        "created": datetime.now().isoformat(),
        "system": "16人2组29天排班系统",
        "period": "2025-05-06 至 2025-06-03",
        "total_days": 29,
    },
    "statistics": {
        "total_shifts": 29,
        "total_people": 16,
        "average_duty": round(sum(duties)/len(duties), 2),
        "min_duty": min(duties),
        "max_duty": max(duties),
        "balance": max(duties) - min(duties)
    },
    "duty_count": duty_count,
    "schedule": schedule,
}

with open("schedule_final_v2.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 排班表已保存到 schedule_final_v2.json")
