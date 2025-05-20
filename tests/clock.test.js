import { getFormattedDate, getShortTimezone, updateClock } from "../src/clock";

describe("Clock functions", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="clock"></div>
      <div id="date"></div>
      <div id="timezone"></div>
      <div id="server-time">2025-05-20T10:30:45Z</div>
    `;
  });

  test("getFormattedDate formats date as YYYY-MM-DD", () => {
    const date = new Date("2025-05-20T10:30:45Z");
    const formatted = getFormattedDate(date);
    expect(formatted).toBe("2025-05-20");
  });

  test("getShortTimezone returns a short timezone string", () => {
    const tz = getShortTimezone();
    expect(typeof tz).toBe("string");
    expect(tz.length).toBeGreaterThan(0);
  });

  test("updateClock updates DOM with time, date, timezone and increments seconds", () => {
    const currentTime = new Date("2025-05-20T10:30:45Z");

    updateClock(currentTime, document);

    expect(document.getElementById("clock").textContent).toBe("10:30:45");
    expect(document.getElementById("date").textContent).toBe("2025-05-20");
    expect(document.getElementById("timezone").textContent.length).toBeGreaterThan(0);

    expect(currentTime.getSeconds()).toBe(46);
  });
});
