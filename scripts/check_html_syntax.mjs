import fs from "node:fs";

const html = fs.readFileSync(new URL("../ICU排班助手.html", import.meta.url), "utf8");
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .filter(source => source.trim());

if (!scripts.length) throw new Error("未找到内联 JavaScript");
new Function(scripts.at(-1));
console.log("HTML JavaScript syntax OK");
