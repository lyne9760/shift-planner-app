import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright";

const bundledChromium = path.join(
  process.env.LOCALAPPDATA || "",
  "ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe",
);
const browser = await chromium.launch({ headless: true, executablePath: bundledChromium });
const page = await browser.newPage();
await page.goto(pathToFileURL(path.resolve("ICU排班助手.html")).href);

const result = await page.evaluate(() => {
  const makePerson = (name, role, group) => ({
    name, role, group, active: true, level: 2, certified: false,
    unavailableDates: [], oldICU: false,
  });
  const friday = new Date("2026-08-07T00:00:00");
  const thursday = new Date("2026-08-06T00:00:00");
  data.people = [makePerson("甲", "主班类型", "A组"), makePerson("乙", "副班类型", "A组")];
  data.continuity.recent = [];
  data.continuity.oldICU = [];
  const fridayFallback = solveBalancedFirstLine([friday]);
  const thursdayRejected = solveBalancedFirstLine([thursday]);

  data.people = [
    makePerson("甲", "主班类型", "A组"),
    makePerson("乙", "副班类型", "B组"),
    makePerson("丙", "主班类型", "C组"),
  ];
  data.cycle.saturdayDayShifts = ["2026-08-08"];
  const rows = [{
    date: "2026-08-08", main: "甲", mainGroup: "A组",
    secondary: "乙", secondaryGroup: "B组", extraSecondary: "",
  }];
  const white = assignWeekendDayShifts(rows);
  const nightSnapshot = rows.map(row => `${row.date}|${row.main}|${row.secondary}`).join(";");
  const candidateTier = rows[0].dayShiftTier;
  const exceptionLabels = scheduleExceptionLabels({
    date: "2026-08-07", main: "甲", secondary: "乙", mainGroup: "A组", secondaryGroup: "A组",
    sameGroup: true, doubleDeputy: true, doubleMain: false, temporaryMain: true, extraSecondary: "",
  });
  const roster = [
    ["A01", "主班类型", "A组", [21, 22, 23]], ["A02", "副班类型", "A组", [21, 22, 23]],
    ["A03", "副班类型", "A组", [21, 22, 23]], ["A04", "主班类型", "A组", []],
    ["B01", "主班类型", "B组", []], ["B02", "主班类型", "B组", []],
    ["B03", "副班类型", "B组", []], ["B04", "副班类型", "B组", [21, 22, 23]],
    ["B05", "副班类型", "B组", []], ["C01", "副班类型", "C组", [21, 22, 23]],
    ["C02", "主班类型", "C组", [21, 22, 23]], ["C03", "副班类型", "C组", [21, 22, 23]],
    ["C04", "主班类型", "C组", []], ["C05", "副班类型", "C组", [21, 22, 23]],
    ["C06", "主班类型", "C组", []],
  ];
  data.people = roster.map(([name, role, group, unavailable]) => ({
    ...makePerson(name, role, group),
    certified: ["B02", "B03", "B05", "C04", "C06"].includes(name),
    unavailableDates: unavailable.map(day => `2026-08-${String(day).padStart(2, "0")}`),
  }));
  const fullDates = Array.from({ length: 29 }, (_, index) => new Date(2026, 7, 3 + index));
  const full = solveBalancedFirstLine(fullDates);
  let fullSummary = { ok: full.ok, message: full.message || "" };
  if (full.ok) {
    const fullRows = full.rows.map(row => ({ ...row, extraSecondary: "", extraSecondaryGroup: "" }));
    data.cycle.saturdayDayShifts = fullDates
      .filter(date => [0, 6].includes(date.getDay()))
      .map(date => iso(date));
    const fullWhite = assignWeekendDayShifts(fullRows);
    const counts = Object.fromEntries(data.people.map(person => [person.name, 0]));
    const qualities = Object.fromEntries(data.people.map(person => [person.name, 0]));
    const burdens = Object.fromEntries(data.people.map(person => [person.name, 0]));
    for (const row of fullRows) {
      const date = parseDate(row.date);
      for (const name of [row.main, row.secondary]) {
        counts[name]++;
        qualities[name] += qualityScore(date);
        if ([0, 5, 6].includes(date.getDay())) burdens[name]++;
      }
      if (row.extraSecondary) burdens[row.extraSecondary]++;
    }
    fullSummary = {
      ok: true,
      nonFriSatSameGroup: fullRows.filter(row => row.mainGroup === row.secondaryGroup && ![5, 6].includes(parseDate(row.date).getDay())).length,
      sameGroup: fullRows.filter(row => row.mainGroup === row.secondaryGroup).length,
      countGap: Math.max(...Object.values(counts)) - Math.min(...Object.values(counts)),
      qualityGap: Math.max(...Object.values(qualities)) - Math.min(...Object.values(qualities)),
      whiteCount: fullRows.filter(row => row.extraSecondary).length,
      weekendBurdenGap: Math.max(...Object.values(burdens)) - Math.min(...Object.values(burdens)),
      whiteOk: fullWhite.ok,
      nightSchedulePreserved: fullRows.map(row => `${row.date}|${row.main}|${row.secondary}`).join(";") ===
        full.rows.map(row => `${row.date}|${row.main}|${row.secondary}`).join(";"),
      allDayShiftsClassified: fullRows.filter(row => row.extraSecondary).every(row => ["理想", "普通", "例外"].includes(row.dayShiftTier)),
    };
  }
  return {
    weights: [1, 2, 3, 4, 5, 6, 0].map(day => {
      const d = new Date("2026-08-03T00:00:00");
      d.setDate(d.getDate() + ((day + 6) % 7));
      return qualityScore(d);
    }),
    fridayFallback: fridayFallback.ok && fridayFallback.rows[0].sameGroup,
    fridayFallbackMarked: fridayFallback.crossGroupFallback && fridayFallback.sameGroupCount === 1,
    thursdayRejected: !thursdayRejected.ok,
    whiteAssigned: white.ok && rows[0].extraSecondary === "丙",
    stagedDayShift: nightSnapshot === rows.map(row => `${row.date}|${row.main}|${row.secondary}`).join(";") && ["理想", "普通", "例外"].includes(candidateTier),
    personalPreferenceRemoved: !document.getElementById("p-preferred") && !document.getElementById("b-preferred") && !document.getElementById("p-note") && !document.getElementById("b-note"),
    stagedButtonPresent: Boolean(document.getElementById("day-shift-button")),
    exceptionWorkflowPresent: exceptionLabels.includes("同组兜底") && exceptionLabels.includes("双副班") && exceptionLabels.includes("临时主班") &&
      typeof editScheduleException === "function" && typeof toggleScheduleException === "function",
    fullSummary,
  };
});

await browser.close();
const passed = JSON.stringify(result.weights) === JSON.stringify([5, 5, 5, 6, 4, 1, 2]) &&
  result.fridayFallback && result.fridayFallbackMarked && result.thursdayRejected && result.whiteAssigned &&
  result.stagedDayShift && result.personalPreferenceRemoved && result.stagedButtonPresent && result.exceptionWorkflowPresent &&
  result.fullSummary.ok && result.fullSummary.nonFriSatSameGroup === 0 && result.fullSummary.countGap <= 1 &&
  result.fullSummary.qualityGap <= 6 && result.fullSummary.whiteOk && result.fullSummary.whiteCount === 8 &&
  result.fullSummary.weekendBurdenGap <= 1 && result.fullSummary.nightSchedulePreserved && result.fullSummary.allDayShiftsClassified;
if (!passed) {
  throw new Error(`网页排班测试失败：${JSON.stringify(result)}`);
}
console.log("Web scheduler tests OK", JSON.stringify(result));
