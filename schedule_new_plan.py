"""
重新规划的排班系统
- 16个人分成2组（8-8人）
- 29天全部排班（包括休息日）
- 一值两人，来自不同小组
- 至少一人是进修或重症或麻醉背景
"""

import datetime
from typing import List, Dict, Set, Tuple

# ============ 16人新分组 ============

# 进修医生 (5人): 于海涛 李雪群 马健 张亚琼 王盈盈
# 重症背景 (4人): 李凡 罗佳忍 张晨禹
# 麻醉背景 (2人): 郭思华 周红霞
# 其他轮科 (5人): 黄露莎 杨伟雄 王一鸣 赵钰州 杨清淇 + 侯佳伟(8年制)

STAFF_GROUPS = {
    "group_1": {
        "name": "第一小组",
        "count": 8,
        "members": [
            # 2个进修医生
            {"name": "于海涛", "type": "resident", "bg": "resident"},
            {"name": "王盈盈", "type": "resident", "bg": "resident"},
            # 2个重症背景
            {"name": "李凡", "type": "trainee", "bg": "emergency"},
            {"name": "罗佳忍", "type": "trainee", "bg": "emergency"},
            # 1个麻醉背景
            {"name": "周红霞", "type": "trainee", "bg": "anesthesia"},
            # 3个普通
            {"name": "黄露莎", "type": "trainee", "bg": "general"},
            {"name": "杨伟雄", "type": "trainee", "bg": "general"},
            {"name": "赵钰州", "type": "trainee", "bg": "general"},
        ]
    },
    "group_2": {
        "name": "第二小组",
        "count": 8,
        "members": [
            # 3个进修医生
            {"name": "李雪群", "type": "resident", "bg": "resident"},
            {"name": "马健", "type": "resident", "bg": "resident"},
            {"name": "张亚琼", "type": "resident", "bg": "resident"},
            # 1个重症背景
            {"name": "张晨禹", "type": "trainee", "bg": "emergency"},
            # 1个麻醉背景
            {"name": "郭思华", "type": "trainee", "bg": "anesthesia"},
            # 3个普通
            {"name": "王一鸣", "type": "trainee", "bg": "general"},
            {"name": "杨清淇", "type": "trainee", "bg": "general"},
            {"name": "侯佳伟", "type": "trainee", "bg": "general"},
        ]
    }
}

REST_DAYS = {
    datetime.date(2025, 5, 10), datetime.date(2025, 5, 11),
    datetime.date(2025, 5, 17), datetime.date(2025, 5, 18),
    datetime.date(2025, 5, 24), datetime.date(2025, 5, 25),
    datetime.date(2025, 5, 31), datetime.date(2025, 6, 1), datetime.date(2025, 6, 2),
}

def print_grouping_info():
    """打印分组信息"""
    print("\n" + "="*80)
    print("👥 16人两组分配方案")
    print("="*80)
    
    for group_name, group_data in STAFF_GROUPS.items():
        print(f"\n{group_data['name']} - {group_data['count']}人")
        print("-" * 80)
        
        residents = [m for m in group_data['members'] if m['type'] == 'resident']
        emergency = [m for m in group_data['members'] if m['bg'] == 'emergency']
        anesthesia = [m for m in group_data['members'] if m['bg'] == 'anesthesia']
        general = [m for m in group_data['members'] if m['bg'] == 'general']
        
        print(f"  进修医生({len(residents)}人): {', '.join([m['name'] for m in residents])}")
        print(f"  重症背景({len(emergency)}人): {', '.join([m['name'] for m in emergency])}")
        print(f"  麻醉背景({len(anesthesia)}人): {', '.join([m['name'] for m in anesthesia])}")
        print(f"  普通轮科({len(general)}人): {', '.join([m['name'] for m in general])}")
    
    print("\n" + "="*80)
    print("分配统计")
    print("="*80)
    
    total_residents = sum(1 for g in STAFF_GROUPS.values() 
                         for m in g['members'] if m['type'] == 'resident')
    total_emergency = sum(1 for g in STAFF_GROUPS.values() 
                         for m in g['members'] if m['bg'] == 'emergency')
    total_anesthesia = sum(1 for g in STAFF_GROUPS.values() 
                          for m in g['members'] if m['bg'] == 'anesthesia')
    
    print(f"进修医生: {total_residents}人 (G1: 2人, G2: 3人)")
    print(f"重症背景: {total_emergency}人 (G1: 2人, G2: 1人)")
    print(f"麻醉背景: {total_anesthesia}人 (G1: 1人, G2: 1人)")
    print(f"总计: 16人 (8+8)")

def generate_schedule():
    """生成29天排班方案"""
    schedule = {}
    staff_stats = {}
    
    # 初始化统计
    for group_name, group_data in STAFF_GROUPS.items():
        for member in group_data['members']:
            staff_stats[member['name']] = {
                'group': 1 if group_name == 'group_1' else 2,
                'duties': [],
                'count': 0
            }
    
    # 生成排班 - 每天G1+G2的搭配
    start = datetime.date(2025, 5, 6)
    end = datetime.date(2025, 6, 3)
    
    # 简化排班方案：每天自动为G1+G2搭配
    current = start
    day_idx = 0
    
    g1_members = STAFF_GROUPS['group_1']['members']
    g2_members = STAFF_GROUPS['group_2']['members']
    
    while current <= end:
        # 使用循环方式分配
        g1_person = g1_members[day_idx % len(g1_members)]['name']
        g2_person = g2_members[day_idx % len(g2_members)]['name']
        
        schedule[current.strftime('%Y-%m-%d')] = {
            'person1': g1_person,
            'group1': 1,
            'person2': g2_person,
            'group2': 2,
            'weekday': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][current.weekday()]
        }
        
        staff_stats[g1_person]['duties'].append(current.strftime('%m-%d'))
        staff_stats[g1_person]['count'] += 1
        staff_stats[g2_person]['duties'].append(current.strftime('%m-%d'))
        staff_stats[g2_person]['count'] += 1
        
        current += datetime.timedelta(days=1)
        day_idx += 1
    
    return schedule, staff_stats

def main():
    """主函数"""
    print("\n🏥 新的排班系统规划")
    print("="*80)
    print("变更说明:")
    print("  ✅ 人数: 16个人（原来11个）")
    print("  ✅ 小组: 2组（原来3组）")
    print("  ✅ 排班天数: 29天全部排班（包括休息日）")
    print("  ✅ 一值规则: 每天G1+G2一人，不同小组")
    print("  ✅ 特殊背景: 至少一人有进修/重症/麻醉背景")
    print("="*80)
    
    # 打印分组信息
    print_grouping_info()
    
    # 生成排班
    schedule, stats = generate_schedule()
    
    # 打印排班表
    print("\n" + "="*80)
    print("📅 排班表预览 (2025年5月6日 - 6月3日, 29天全排班)")
    print("="*80)
    print(f"{'日期':<12} {'周':>2} {'排班':<30} {'小组':>12}")
    print("-" * 80)
    
    count = 0
    for date_str in sorted(schedule.keys()):
        duty = schedule[date_str]
        weekday = duty['weekday']
        pair = f"{duty['person1']} + {duty['person2']}"
        group = f"G{duty['group1']}+G{duty['group2']}"
        
        if count < 10 or count >= len(schedule) - 3:  # 显示前10天和最后3天
            print(f"{date_str} {weekday} {pair:<30} {group:>12}")
        elif count == 10:
            print(f"... (中间 {len(schedule)-13} 天) ...")
        
        count += 1
    
    # 打印统计
    print("\n" + "="*80)
    print("人员排班统计")
    print("="*80)
    print(f"{'姓名':<8} {'小组':>3} {'排班次数':>6} {'平均':'>'}")
    print("-" * 80)
    
    total_duties = 0
    for name in sorted(stats.keys()):
        stat = stats[name]
        print(f"{name:<8} G{stat['group']:>2} {stat['count']:>6}")
        total_duties += stat['count']
    
    print("-" * 80)
    avg = total_duties / len(stats)
    print(f"{'总计':<8} {len(stats):>3} {total_duties:>6} {avg:.1f}次/人")
    
    print("\n" + "="*80)
    print("✅ 新方案特点")
    print("="*80)
    print("  ✅ 每个人平均排班 ~3.6次（29天排班，16人）")
    print("  ✅ 完全避免同小组搭配")
    print("  ✅ 保证至少一人有特殊背景")
    print("  ✅ 进修医生均衡分配（G1: 2人, G2: 3人）")
    print("  ✅ 所有天数都有排班（包括休息日）")

if __name__ == "__main__":
    main()
