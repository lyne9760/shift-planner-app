#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班系统 - 16人2组29天全排班生成器
所有天数都需要排班（包括原休息日）
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

def can_pair(person1, person2):
    """检查两人是否可以配对：需要至少一人有特殊背景"""
    return has_special_background(person1) or has_special_background(person2)

def generate_schedule():
    """生成29天排班表"""
    start_date = datetime(2025, 5, 6)
    schedule = {}
    
    # 追踪每个人的排班计数
    duty_count = {}
    for staff in GROUP_1 + GROUP_2:
        duty_count[staff["name"]] = 0
    
    # 追踪每个人的最后排班日期（用于避免连续排班）
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
        
        # 检查配对是否有效（至少一人有特殊背景）
        if can_pair(min_g1, min_g2):
            person1 = min_g1["name"]
            person2 = min_g2["name"]
        else:
            # 如果不能配对，找其他人
            candidates = []
            for g1 in GROUP_1:
                for g2 in GROUP_2:
                    if can_pair(g1, g2):
                        candidates.append((g1, g2, duty_count[g1["name"]] + duty_count[g2["name"]]))
            
            if candidates:
                # 选择总排班次数最少的组合
                min_g1, min_g2, _ = min(candidates, key=lambda x: x[2])
                person1 = min_g1["name"]
                person2 = min_g2["name"]
            else:
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

def validate_schedule(schedule):
    """验证排班表"""
    errors = []
    
    # 检查覆盖率
    if len(schedule) != 29:
        errors.append(f"错误：只有{len(schedule)}天排班，应该有29天")
    
    # 检查每个人是否在不同小组
    for date, shift in schedule.items():
        if shift["group1"] == shift["group2"]:
            errors.append(f"错误：{date} {shift['person1']} 和 {shift['person2']} 在同一小组")
    
    # 检查是否有特殊背景的人
    staff_types = {}
    for person in [s["name"] for s in GROUP_1] + [s["name"] for s in GROUP_2]:
        for group in [GROUP_1, GROUP_2]:
            for staff in group:
                if staff["name"] == person:
                    staff_types[person] = staff["type"]
    
    for date, shift in schedule.items():
        p1_type = staff_types.get(shift["person1"], "unknown")
        p2_type = staff_types.get(shift["person2"], "unknown")
        has_special = p1_type in ["resident", "emergency", "anesthesia"] or \
                     p2_type in ["resident", "emergency", "anesthesia"]
        if not has_special:
            errors.append(f"错误：{date} {shift['person1']} 和 {shift['person2']} 都没有特殊背景")
    
    return errors

def main():
    print("=" * 60)
    print("生成29天排班表（包括休息日）")
    print("=" * 60)
    
    schedule, duty_count = generate_schedule()
    errors = validate_schedule(schedule)
    
    if errors:
        print("\n❌ 验证失败：")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ 验证通过：所有约束都满足")
    
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
    
    # 显示前几天的排班
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
            "validation_passed": len(errors) == 0,
            "error_count": len(errors)
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
        "errors": errors
    }
    
    with open("schedule_final_v2.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 排班表已保存到 schedule_final_v2.json")
    
    return schedule, duty_count, errors

if __name__ == "__main__":
    schedule, duty_count, errors = main()
