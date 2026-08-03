# -*- coding: utf-8 -*-
"""用 OR-Tools CP-SAT 求解 ICU 一值班表（2026-08-03 至 2026-08-31）
约束与 ICU排班助手.html 的 solveBalancedFirstLine 一致：强优先跨组，无解时仅周五、周六同组兜底并标记。
"""
from ortools.sat.python import cp_model
from datetime import date, timedelta
import argparse, io, math, os, sys

# 强制 stdout/stderr 使用 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

parser = argparse.ArgumentParser(description="生成 ICU 一值班表")
parser.add_argument(
    "--day-shift-mode",
    choices=("none", "saturday", "weekend"),
    default="none",
    help="白班模式：none=不安排，saturday=仅周六，weekend=周六和周日",
)
parser.add_argument("--output", default="icu_first_line_schedule.csv", help="CSV 输出路径")
args = parser.parse_args()

# ================== 数据 ==================
people_data = [
    # A组
    {"name": "A01", "role": "main", "group": "A组", "level": 3, "certified": False, "active": True,  "unavailable": [21, 22, 23]},
    {"name": "A02", "role": "sub",  "group": "A组", "level": 2, "certified": False, "active": True,  "unavailable": [21, 22, 23]},
    {"name": "A03", "role": "sub",  "group": "A组", "level": 2, "certified": False, "active": True,  "unavailable": [21, 22, 23]},
    {"name": "A04", "role": "main", "group": "A组", "level": 2, "certified": False, "active": True,  "unavailable": []},
    {"name": "A05", "role": "main", "group": "A组", "level": 3, "certified": True,  "active": False, "unavailable": []},
    # B组
    {"name": "B01", "role": "main", "group": "B组", "level": 3, "certified": False, "active": True,  "unavailable": []},
    {"name": "B02", "role": "main", "group": "B组", "level": 2, "certified": True,  "active": True,  "unavailable": []},
    {"name": "B03", "role": "sub",  "group": "B组", "level": 2, "certified": True,  "active": True,  "unavailable": []},
    {"name": "B04", "role": "sub",  "group": "B组", "level": 2, "certified": False, "active": True,  "unavailable": [21, 22, 23]},
    {"name": "B05", "role": "sub",  "group": "B组", "level": 2, "certified": True,  "active": True,  "unavailable": []},
    {"name": "B06", "role": "main", "group": "B组", "level": 2, "certified": True,  "active": False, "unavailable": []},
    # C组
    {"name": "C01", "role": "sub",  "group": "C组", "level": 2, "certified": False, "active": True, "unavailable": [21, 22, 23]},
    {"name": "C02", "role": "main", "group": "C组", "level": 2, "certified": False, "active": True, "unavailable": [21, 22, 23]},
    {"name": "C03", "role": "sub",  "group": "C组", "level": 2, "certified": False, "active": True, "unavailable": [21, 22, 23]},
    {"name": "C04", "role": "main", "group": "C组", "level": 3, "certified": True,  "active": True, "unavailable": []},
    {"name": "C05", "role": "sub",  "group": "C组", "level": 2, "certified": False, "active": True, "unavailable": [21, 22, 23]},
    {"name": "C06", "role": "main", "group": "C组", "level": 2, "certified": True,  "active": True, "unavailable": []},
]

# 过滤参加排班的人员
people = [p for p in people_data if p["active"]]
names = [p["name"] for p in people]
idx = {p["name"]: i for i, p in enumerate(people)}
n = len(people)

# 日期
start = date(2026, 8, 3)
end = date(2026, 8, 31)
dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
m = len(dates)

def day_number(d): return d.toordinal()
def iso(d): return d.isoformat()
def weekday_cn(d): return "一二三四五六日"[d.weekday()]
def duty_category(d):
    return {3: "thu", 4: "fri", 5: "sat", 6: "sun"}.get(d.weekday(), "")
def quality_score(d):
    return {0: 5, 1: 5, 2: 5, 3: 6, 4: 4, 5: 1, 6: 2}[d.weekday()]
def quality_name(d):
    labels = {3: "周四最佳", 4: "周五", 5: "周六最差", 6: "周日"}
    return f"{labels.get(d.weekday(), '工作日')}·权重{quality_score(d)}"

# 主班实力：主班 +100，oldICU +20，level
strength = [100 + p["level"] if p["role"] == "main" else p["level"] for p in people]

# 配对候选 (a,b)：a 当主班、b 当副班。允许同组，由后续约束控制。
pairs = []
for i in range(n):
    for j in range(i + 1, n):
        # 主班由实力高者担任
        if strength[j] > strength[i]:
            main, sub = j, i
        else:
            main, sub = i, j
        same_group = people[i]["group"] == people[j]["group"]
        main_count = int(people[i]["role"] == "main") + int(people[j]["role"] == "main")
        double_deputy = main_count == 0
        double_main = main_count == 2
        temporary_main = people[main]["role"] != "main"
        pairs.append({
            "main": main, "sub": sub, "key": (i, j),
            "same_group": same_group,
            "double_deputy": double_deputy,
            "double_main": double_main,
            "temporary_main": temporary_main,
            "certified": people[i]["certified"] or people[j]["certified"]
        })

# 统计
thu_days = [d for d in dates if duty_category(d) == "thu"]
fri_days = [d for d in dates if duty_category(d) == "fri"]
sat_days = [d for d in dates if duty_category(d) == "sat"]
sun_days = [d for d in dates if duty_category(d) == "sun"]
weekend_days = fri_days + sat_days + sun_days
white_days = [
    d for d in dates
    if args.day_shift_mode == "weekend" and d.weekday() in (5, 6)
    or args.day_shift_mode == "saturday" and d.weekday() == 5
]
white_day_indices = [dates.index(d) for d in white_days]

# 与人次相关的限制
total_slots = m * 2
total_min = total_slots // n
total_max = (total_slots + n - 1) // n
# 因为 58 = 15*3 + 13，所以 13 人 4 次、2 人 3 次
# 用平衡范围 {min, max} 并让 solver 自动分配
cat_limits = {
    "thu": (len(thu_days) * 2 // n, (len(thu_days) * 2 + n - 1) // n),
    "fri": (len(fri_days) * 2 // n, (len(fri_days) * 2 + n - 1) // n),
    "sat": (len(sat_days) * 2 // n, (len(sat_days) * 2 + n - 1) // n),
    "sun": (len(sun_days) * 2 // n, (len(sun_days) * 2 + n - 1) // n),
}
weekend_min = len(weekend_days) * 2 // n
weekend_max = (len(weekend_days) * 2 + n - 1) // n

print(f"排班日期：{iso(start)} 至 {iso(end)}，共 {m} 天")
print(f"参加排班：{n} 人，每人 {total_min}–{total_max} 次")
print(f"周四 {len(thu_days)} 天、周五 {len(fri_days)} 天、周六 {len(sat_days)} 天、周日 {len(sun_days)} 天")
print(f"白班模式：{args.day_shift_mode}，共 {len(white_days)} 个白班")

# ================== 模型 ==================
model = cp_model.CpModel()

# x[p, d] = 1 表示人员 p 在日期 d 值班（无论主/副）
x = {}
for i, p in enumerate(people):
    for d_idx, d in enumerate(dates):
        x[i, d_idx] = model.NewBoolVar(f"x_{i}_{d_idx}")

# y[k, d] = 1 表示配对 k 在日期 d 使用
y = {}
for k_idx, pair in enumerate(pairs):
    for d_idx, d in enumerate(dates):
        y[k_idx, d_idx] = model.NewBoolVar(f"y_{k_idx}_{d_idx}")

# w[p, d] = 1 表示人员 p 在选定日期承担额外白班
w = {
    (i, d_idx): model.NewBoolVar(f"w_{i}_{d_idx}")
    for i in range(n)
    for d_idx in white_day_indices
}

# 1. 每天恰好一个配对
for d_idx in range(m):
    model.Add(sum(y[k_idx, d_idx] for k_idx in range(len(pairs))) == 1)

# 2. 配对与人员关联
for k_idx, pair in enumerate(pairs):
    main, sub = pair["main"], pair["sub"]
    for d_idx in range(m):
        model.Add(y[k_idx, d_idx] <= x[main, d_idx])
        model.Add(y[k_idx, d_idx] <= x[sub, d_idx])
        # 若配对使用，这两人当天都值班
        model.Add(y[k_idx, d_idx] * 2 <= x[main, d_idx] + x[sub, d_idx])

# 3. 每天每人最多值班一次（由配对定义已保证，但再加一层保险）
for i in range(n):
    for d_idx in range(m):
        # x[i,d] 应该等于所有包含 i 的配对 y 之和
        model.Add(x[i, d_idx] == sum(y[k_idx, d_idx] for k_idx, pair in enumerate(pairs) if i in (pair["main"], pair["sub"])))

# 4. 禁排日期
for i, p in enumerate(people):
    for d_idx, d in enumerate(dates):
        if d.day in p["unavailable"]:
            model.Add(x[i, d_idx] == 0)

# 白班：每天 1 人；不能与当天夜班重复，前一天值夜班者不能排次日白班
for d_idx in white_day_indices:
    model.Add(sum(w[i, d_idx] for i in range(n)) == 1)
    for i, p in enumerate(people):
        model.Add(w[i, d_idx] + x[i, d_idx] <= 1)
        if d_idx > 0:
            model.Add(w[i, d_idx] + x[i, d_idx - 1] <= 1)
        if dates[d_idx].day in p["unavailable"]:
            model.Add(w[i, d_idx] == 0)

# 5. 4 天间隔
for i in range(n):
    for d1_idx, d1 in enumerate(dates):
        for d2_idx, d2 in enumerate(dates):
            if d1_idx >= d2_idx: continue
            if abs(day_number(d1) - day_number(d2)) < 4:
                model.Add(x[i, d1_idx] + x[i, d2_idx] <= 1)

# 6. 周一至周四、周日强制跨组；周五、周六采用最高优先级软约束。
# 若严格跨组有解，百万级惩罚保证不会选择同组；否则才使用周五/周六同组兜底。
for k_idx, pair in enumerate(pairs):
    if not pair["same_group"]:
        continue
    for d_idx, d in enumerate(dates):
        if d.weekday() not in (4, 5):
            model.Add(y[k_idx, d_idx] == 0)

# 7. 总次数限制 [total_min, total_max]
for i in range(n):
    total = sum(x[i, d_idx] for d_idx in range(m))
    model.Add(total >= total_min)
    model.Add(total <= total_max)

# 8. 周四/周五/周六/周日 次数限制
for cat, (cmin, cmax) in cat_limits.items():
    cat_days = [d_idx for d_idx, d in enumerate(dates) if duty_category(d) == cat]
    for i in range(n):
        s = sum(x[i, d_idx] for d_idx in cat_days)
        model.Add(s >= cmin)
        model.Add(s <= cmax)

# 9. 周末次数限制
for i in range(n):
    s = sum(x[i, d_idx] for d_idx, d in enumerate(dates) if duty_category(d) in ("fri", "sat", "sun"))
    model.Add(s >= weekend_min)
    model.Add(s <= weekend_max)

# 10. 班次质量均衡：一至三=5、四=6、五=4、六=1、日=2
total_quality = sum(quality_score(d) * 2 for d in dates)  # 每天两人
avg_quality = total_quality / n
q_min = max(0, math.floor(avg_quality) - 3)
q_max = math.ceil(avg_quality) + 3
print(f"班次质量：总{total_quality}，人均{avg_quality:.1f}，约束范围[{q_min},{q_max}]")

qsum = {}
for i in range(n):
    qsum[i] = model.NewIntVar(0, 100, f"qsum_{i}")
    model.Add(qsum[i] == sum(x[i, d_idx] * quality_score(dates[d_idx]) for d_idx in range(m)))
    model.Add(qsum[i] >= q_min)
    model.Add(qsum[i] <= q_max)

# 11. 白班与夜班合计尽量均衡；白班不计入夜班质量分
combined_min = (total_slots + len(white_days)) // n
combined_max = math.ceil((total_slots + len(white_days)) / n)
for i in range(n):
    combined = sum(x[i, d_idx] for d_idx in range(m)) + sum(
        w[i, d_idx] for d_idx in white_day_indices
    )
    model.Add(combined >= combined_min)
    model.Add(combined <= combined_max)

# 12. 周六劣(最差班次)均衡：每人周六次数尽量均等
sat_count = {}
for i in range(n):
    sat_count[i] = model.NewIntVar(0, 10, f"sat_{i}")
    sat_day_idxs = [d_idx for d_idx, d in enumerate(dates) if duty_category(d) == "sat"]
    model.Add(sat_count[i] == sum(x[i, d_idx] for d_idx in sat_day_idxs))

# 13. 周末综合负担：周五/周六/周日夜班 + 周六/周日白班，人数差控制在 1 以内
weekend_total_slots = len(weekend_days) * 2 + len(white_days)
weekend_combined_min = weekend_total_slots // n
weekend_combined_max = math.ceil(weekend_total_slots / n)
weekend_combined = {}
for i in range(n):
    weekend_combined[i] = model.NewIntVar(0, 20, f"weekend_combined_{i}")
    model.Add(weekend_combined[i] ==
              sum(x[i, d_idx] for d_idx, d in enumerate(dates) if duty_category(d) in ("fri", "sat", "sun")) +
              sum(w[i, d_idx] for d_idx in white_day_indices))
    model.Add(weekend_combined[i] >= weekend_combined_min)
    model.Add(weekend_combined[i] <= weekend_combined_max)

# ================== 目标函数 ==================
# 同组使用百万级惩罚，优先级高于全部人员搭配偏好；双副 +5000、双主 +900
objective_terms = []
for k_idx, pair in enumerate(pairs):
    for d_idx in range(m):
        if pair["double_deputy"]:
            objective_terms.append(y[k_idx, d_idx] * 5000)
        if pair["double_main"]:
            objective_terms.append(y[k_idx, d_idx] * 900)
        if pair["same_group"]:
            objective_terms.append(y[k_idx, d_idx] * 1_000_000)

# 白班优先与该人员其他夜班间隔超过 3 天；必要时允许短间隔兜底
for i in range(n):
    for white_idx in white_day_indices:
        for night_idx in range(m):
            gap = abs(day_number(dates[white_idx]) - day_number(dates[night_idx]))
            if gap <= 3 and night_idx not in (white_idx, white_idx - 1):
                near = model.NewBoolVar(f"near_{i}_{white_idx}_{night_idx}")
                model.Add(near >= w[i, white_idx] + x[i, night_idx] - 1)
                objective_terms.append(near * 2)

# 质量均衡：惩罚每人质量分偏离平均值
for i in range(n):
    # 偏离平均值的绝对值（用两个非负变量表示正负偏差）
    pos_dev = model.NewIntVar(0, 100, f"qpos_{i}")
    neg_dev = model.NewIntVar(0, 100, f"qneg_{i}")
    model.Add(qsum[i] - int(round(avg_quality)) == pos_dev - neg_dev)
    objective_terms.append(pos_dev * 100)
    objective_terms.append(neg_dev * 100)

model.Minimize(sum(objective_terms))

# ================== 求解 ==================
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0
# 先找可行解，再优化
solver.parameters.num_search_workers = 8
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("\n未能找到可行解。状态:", solver.StatusName(status))
    exit(1)

print(f"\n求解成功（{solver.StatusName(status)}），目标值：{solver.ObjectiveValue()}\n")

# ================== 输出 ==================
rows = []
for d_idx, d in enumerate(dates):
    for k_idx, pair in enumerate(pairs):
        if solver.Value(y[k_idx, d_idx]) == 1:
            main_i, sub_i = pair["main"], pair["sub"]
            rows.append({
                "date": d,
                "main": people[main_i]["name"],
                "main_group": people[main_i]["group"],
                "sub": people[sub_i]["name"],
                "sub_group": people[sub_i]["group"],
                "double_deputy": pair["double_deputy"],
                "double_main": pair["double_main"],
                "same_group": pair["same_group"],
                "temporary_main": pair["temporary_main"],
                "quality": quality_name(d)
            })
            break

white_by_date = {}
for d_idx in white_day_indices:
    white_by_date[dates[d_idx]] = next(
        people[i]["name"] for i in range(n) if solver.Value(w[i, d_idx]) == 1
    )
for row in rows:
    row["white"] = white_by_date.get(row["date"], "")

rows.sort(key=lambda r: r["date"])

print("| 日期 | 星期 | 主班 | 组 | 副班 | 组 | 白班 | 提示 |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    tags = []
    if r["double_deputy"]: tags.append("双副")
    if r["double_main"]: tags.append("双主")
    if r["same_group"]: tags.append("同组")
    if r["temporary_main"]: tags.append("临时主班")
    tag_str = "·".join(tags)
    print(f"| {r['date'].strftime('%m-%d')} | 周{weekday_cn(r['date'])} | {r['main']} | {r['main_group']} | {r['sub']} | {r['sub_group']} | {r['white'] or '—'} | {r['quality']}{'·' + tag_str if tag_str else ''} |")

# 个人统计
stats = {p["name"]: {"count": 0, "main": 0, "sub": 0, "white": 0, "thu": 0, "fri": 0, "sat": 0, "sun": 0, "weekend": 0, "quality": 0} for p in people}
for r in rows:
    stats[r["main"]]["count"] += 1
    stats[r["main"]]["main"] += 1
    stats[r["main"]]["quality"] += quality_score(r["date"])
    stats[r["sub"]]["count"] += 1
    stats[r["sub"]]["sub"] += 1
    stats[r["sub"]]["quality"] += quality_score(r["date"])
    cat = duty_category(r["date"])
    if cat == "thu":
        stats[r["main"]]["thu"] += 1; stats[r["sub"]]["thu"] += 1
    elif cat == "fri":
        stats[r["main"]]["fri"] += 1; stats[r["sub"]]["fri"] += 1
        stats[r["main"]]["weekend"] += 1; stats[r["sub"]]["weekend"] += 1
    elif cat == "sat":
        stats[r["main"]]["sat"] += 1; stats[r["sub"]]["sat"] += 1
        stats[r["main"]]["weekend"] += 1; stats[r["sub"]]["weekend"] += 1
    elif cat == "sun":
        stats[r["main"]]["sun"] += 1; stats[r["sub"]]["sun"] += 1
        stats[r["main"]]["weekend"] += 1; stats[r["sub"]]["weekend"] += 1
    if r["white"]:
        stats[r["white"]]["white"] += 1
        stats[r["white"]]["weekend"] += 1

print("\n### 个人统计")
print("| 人员 | 组 | 夜班 | 主班 | 副班 | 白班 | 周四 | 周五 | 周六 | 周日 | 周末综合 | 质量分 |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for p in people:
    s = stats[p["name"]]
    print(f"| {p['name']} | {p['group']} | {s['count']} | {s['main']} | {s['sub']} | {s['white']} | {s['thu']} | {s['fri']} | {s['sat']} | {s['sun']} | {s['weekend']} | {s['quality']} |")

double_deputy_days = sum(1 for r in rows if r["double_deputy"])
same_group_days = sum(1 for r in rows if r["same_group"])
print(f"\n总班数：{len(rows)} 天，双副班：{double_deputy_days} 天，同组：{same_group_days} 天")

# 输出为 Excel/CSV 友好的格式
import csv
out_csv = os.path.abspath(args.output)
with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["日期", "星期", "主班", "主班组", "副班", "副班组", "白班", "提示", "同组", "双副", "双主"])
    for r in rows:
        w.writerow([
            r["date"].strftime("%Y-%m-%d"),
            f"周{weekday_cn(r['date'])}",
            r["main"], r["main_group"],
            r["sub"], r["sub_group"],
            r["white"],
            r["quality"],
            "是" if r["same_group"] else "",
            "是" if r["double_deputy"] else "",
            "是" if r["double_main"] else ""
        ])
print(f"\nCSV 已保存：{out_csv}")
