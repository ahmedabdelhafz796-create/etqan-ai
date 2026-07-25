import { chromium } from "playwright";
const EXE = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const b = await chromium.launch({ executablePath: EXE, args: ["--no-sandbox"] });
const pg = await b.newPage({ viewport: { width: 1280, height: 900 } });
await pg.goto("http://localhost:3123", { waitUntil: "networkidle" });
await pg.waitForTimeout(1200);
await pg.screenshot({ path: "shot_hero.png" });
// scroll to marketplace
await pg.evaluate(() => document.getElementById("courses")?.scrollIntoView());
await pg.waitForTimeout(1000);
await pg.screenshot({ path: "shot_courses.png" });
await b.close();
console.log("shots done");
