#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班系统快速启动脚本
使用方法: python quick_start.py
"""

import os
import sys
import json
from pathlib import Path

def print_header():
    """打印欢迎信息"""
    print("\n" + "="*60)
    print("🏥 医院排班系统 - 心胸外科ICU")
    print("="*60)
    print("版本: v1.0")
    print("周期: 2025年5月6日 - 6月3日")
    print("="*60 + "\n")

def check_files():
    """检查必需文件"""
    print("📋 检查文件...")
    required_files = [
        'scheduler.html',
        'schedule_plan_2025_05.json',
        'README.md'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ❌ {file}")
        else:
            print(f"  ✅ {file}")
    
    if missing:
        print(f"\n⚠️ 缺少文件: {', '.join(missing)}")
        return False
    return True

def load_schedule():
    """加载排班数据"""
    print("\n📊 加载排班数据...")
    try:
        with open('schedule_plan_2025_05.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        schedule = data['schedule']
        stats = data['statistics']
        
        print(f"  ✅ 已加载 {len(schedule)} 天排班数据")
        print(f"  ✅ 已加载 {len(stats)} 人员统计")
        
        return data
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("请选择操作:")
    print("="*60)
    print("  1️⃣  查看排班表")
    print("  2️⃣  查看人员信息")
    print("  3️⃣  查看排班统计")
    print("  4️⃣  打开Web界面")
    print("  5️⃣  导出Excel")
    print("  6️⃣  查看文档")
    print("  0️⃣  退出")
    print("="*60)

def show_schedule(data):
    """显示排班表"""
    print("\n" + "="*70)
    print("📅 排班表 (2025年5月6日 - 6月3日)")
    print("="*70)
    
    schedule = data['schedule']
    rest_days = data['rest_days']
    
    count = 0
    for date in sorted(schedule.keys()):
        duty = schedule[date]
        weekday = duty['weekday']
        person1 = duty['person1']
        person2 = duty['person2']
        group1 = duty['group1']
        group2 = duty['group2']
        
        print(f"{date} {weekday}: {person1}(G{group1}) + {person2}(G{group2})")
        count += 1
        
        if count >= 20:  # 限制显示
            print(f"... 还有 {len(schedule) - count} 天")
            break
    
    print(f"\n总计: {len(schedule)} 天排班, {len(rest_days)} 天休息")

def show_staff(data):
    """显示人员信息"""
    print("\n" + "="*70)
    print("👥 人员分组信息")
    print("="*70)
    
    staff = data['staff']
    for group_name, group_data in staff.items():
        print(f"\n{group_data['name']} ({group_name})")
        print("-" * 50)
        for member in group_data['members']:
            type_str = "进修" if member['type'] == 'resident' else "轮科"
            bg_str = member['background']
            print(f"  • {member['name']:<8} [{type_str}] ({bg_str})")

def show_stats(data):
    """显示排班统计"""
    print("\n" + "="*70)
    print("📊 排班统计")
    print("="*70)
    
    stats = data['statistics']
    print(f"\n{'姓名':<8} {'小组':>3} {'进修':>3} {'背景':>6} {'次数':>3} {'周末':>3} {'排班日期':<30}")
    print("-" * 70)
    
    for name in sorted(stats.keys()):
        s = stats[name]
        resident = "是" if s['background'] == 'resident' else ""
        dates_str = ", ".join([d.split('-')[2] for d in s['dates'][:5]])
        if len(s['dates']) > 5:
            dates_str += "..."
        
        print(f"{name:<8} G{s['group']:>2} {resident:>3} {s['background']:>6} {s['total_duties']:>3} {s['weekend_duties']:>3} {dates_str:<30}")
    
    print("\n" + "-" * 70)
    print("说明:")
    print("  • 进修: 进修医生")
    print("  • 背景: 'resident'=进修, 'emergency'=重症, 'anesthesia'=麻醉")
    print("  • 次数: 排班总次数")
    print("  • 周末: 周末排班次数")

def open_web_interface():
    """打开Web界面"""
    print("\n🌐 打开Web界面...")
    try:
        import webbrowser
        html_file = Path('scheduler.html').absolute()
        webbrowser.open(f'file://{html_file}')
        print("  ✅ 已在浏览器中打开排班界面")
    except Exception as e:
        print(f"  ❌ 无法自动打开浏览器: {e}")
        print(f"  💡 请手动打开文件: scheduler.html")

def export_excel():
    """导出Excel"""
    print("\n📥 导出Excel...")
    try:
        import subprocess
        result = subprocess.run(['python', 'schedule_export.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Excel文件已生成: 排班表_2025年5月.xlsx")
        else:
            print(f"  ⚠️ 错误: {result.stderr}")
    except ImportError:
        print("  ❌ 需要安装 pandas: pip install pandas openpyxl")
    except Exception as e:
        print(f"  ❌ 错误: {e}")

def show_docs():
    """显示文档"""
    print("\n📚 可用文档:")
    print("="*70)
    
    docs = [
        ('README.md', '系统说明和使用指南'),
        ('development_report.md', '项目完成报告'),
        ('DELIVERY_CHECKLIST.md', '交付清单'),
        ('plan.md', '项目计划'),
    ]
    
    for doc, desc in docs:
        if Path(doc).exists():
            size = Path(doc).stat().st_size / 1024
            print(f"  ✅ {doc:<30} ({size:.1f}KB) - {desc}")
        else:
            print(f"  ❌ {doc:<30} - 未找到")

def main():
    """主函数"""
    print_header()
    
    # 检查文件
    if not check_files():
        print("\n❌ 部分文件缺失，无法继续")
        return
    
    # 加载数据
    data = load_schedule()
    if not data:
        print("\n❌ 无法加载排班数据")
        return
    
    # 主循环
    while True:
        show_menu()
        choice = input("请选择 (0-6): ").strip()
        
        if choice == '1':
            show_schedule(data)
        elif choice == '2':
            show_staff(data)
        elif choice == '3':
            show_stats(data)
        elif choice == '4':
            open_web_interface()
        elif choice == '5':
            export_excel()
        elif choice == '6':
            show_docs()
        elif choice == '0':
            print("\n👋 谢谢使用，再见！\n")
            break
        else:
            print("❌ 无效的选择，请重试")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
