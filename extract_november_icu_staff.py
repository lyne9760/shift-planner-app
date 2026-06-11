from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


OUTPUT = Path(__file__).with_name("sample_first_line_staff.xlsx")

STAFF = [
    ("成员A", "培训", 2024, "三年", "专业A", "内部培训", "无", "A001", "可副班", ""),
    ("成员B", "培训", 2022, "一年", "专业B", "轮转人员", "无", "A002", "可副班", ""),
    ("成员C", "培训", 2024, "三年", "专业A", "内部培训", "无", "A003", "可副班", ""),
    ("成员D", "培训", 2023, "三年", "专业C", "内部培训", "有", "A004", "主班候选", "高年资示例人员"),
    ("成员E", "培训", 2024, "三年", "专业A", "内部培训", "无", "A005", "可副班", ""),
    ("成员F", "培训", 2024, "三年", "专业A", "内部培训", "无", "A006", "可副班", ""),
    ("成员G", "培训", 2023, "三年", "专业D", "内部培训", "有", "A007", "主班候选", "关键岗位示例"),
    ("成员H", "培训", 2024, "三年", "专业A", "内部培训", "无", "A008", "可副班", ""),
    ("成员I", "培训", 2022, "一年", "专业B", "轮转人员", "无", "A009", "可副班", ""),
    ("成员J", "培训", 2023, "三年", "专业C", "内部培训", "有", "A010", "主班候选", "高年资示例人员"),
    ("成员K", "培训", 2023, "三年", "专业B", "内部培训", "有", "A011", "主班候选", "高年资示例人员"),
    ("成员L", "培训", 2022, "一年", "专业B", "轮转人员", "无", "A012", "主班候选", "示例互换说明"),
    ("成员M", "培训", "", "", "专业B", "", "", "", "可副班", "仅保留示例字段"),
    ("成员N", "进修", "", "", "", "", "", "", "主班候选", "进修"),
    ("成员O", "进修", "", "", "", "", "", "", "主班候选", "进修"),
    ("成员P", "进修", "", "", "", "", "", "", "主班候选", "进修"),
]

EXCLUDED = [
    ("成员Q", "来源X", "不参与", "示例：本轮不参与值班"),
    ("成员R", "来源Y", "不参与", "示例：原始表中标注不排班"),
]


def build_workbook():
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "一线人员"
    sheet.freeze_panes = "A2"
    sheet.sheet_view.showGridLines = False

    headers = [
        "姓名",
        "来源",
        "届别",
        "培训年限",
        "培训专业",
        "人员类型",
        "处方权",
        "工号",
        "岗位判断",
        "备注",
    ]
    header_fill = PatternFill("solid", fgColor="9FC5E8")
    primary_fill = PatternFill("solid", fgColor="D9EAD3")
    pending_fill = PatternFill("solid", fgColor="FFF2CC")
    thin = Side(style="thin", color="B7B7B7")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for column, header in enumerate(headers, 1):
        cell = sheet.cell(1, column, header)
        cell.fill = header_fill
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
        cell.border = border

    for row, values in enumerate(STAFF, 2):
        for column, value in enumerate(values, 1):
            cell = sheet.cell(row, column, value)
            cell.border = border
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
        if values[8] == "主班候选":
            for cell in sheet[row]:
                cell.fill = primary_fill
        elif values[8] == "待确认":
            for cell in sheet[row]:
                cell.fill = pending_fill

    widths = [12, 10, 10, 12, 24, 22, 10, 14, 14, 35]
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[chr(64 + index)].width = width

    excluded = workbook.create_sheet("不参与人员")
    excluded.append(["姓名", "来源", "状态", "原因"])
    for row in EXCLUDED:
        excluded.append(row)
    for cell in excluded[1]:
        cell.fill = header_fill
        cell.font = Font(bold=True)
    for row in excluded.iter_rows():
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", wrap_text=True)
    excluded.column_dimensions["A"].width = 12
    excluded.column_dimensions["B"].width = 12
    excluded.column_dimensions["C"].width = 12
    excluded.column_dimensions["D"].width = 35

    notes = workbook.create_sheet("提取说明")
    notes.append(["项目", "结果"])
    notes.append(["可参与一线人数", 16])
    notes.append(["培训", 13])
    notes.append(["进修", 3])
    notes.append(["其他来源", 0])
    notes.append(["主班候选（8人）", "成员D、成员G、成员J、成员K、成员L、成员N、成员O、成员P"])
    notes.append(["副班候选（8人）", "成员A、成员B、成员C、成员E、成员F、成员H、成员I、成员M"])
    notes.append(["扩充原则", "优先保留关键岗位、进修与高年资示例人员，使主副班人数达到 8 比 8"])
    notes.append(["排除", "成员Q、成员R：作为演示样例，不参与本轮值班"])
    for cell in notes[1]:
        cell.fill = header_fill
        cell.font = Font(bold=True)
    notes.column_dimensions["A"].width = 28
    notes.column_dimensions["B"].width = 60
    for row in notes.iter_rows():
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=True)
    return workbook


if __name__ == "__main__":
    build_workbook().save(OUTPUT)
    print(OUTPUT)
