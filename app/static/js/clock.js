function getFormattedDate(date) {
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
  const formattedDate = new Intl.DateTimeFormat('en-CA', options).format(date);
  const [year, month, day] = formattedDate.split('-');
  return `${year}-${month}-${day}`;
}

function getShortTimezone() {
  const options = { timeZoneName: "short" };
  const formatter = new Intl.DateTimeFormat("en-US", options);
  const parts = formatter.formatToParts(new Date());
  return parts.find(p => p.type === "timeZoneName")?.value || "";
}

function updateClock() {
  const hours = String(currentTime.getHours()).padStart(2, '0');
  const minutes = String(currentTime.getMinutes()).padStart(2, '0');
  const seconds = String(currentTime.getSeconds()).padStart(2, '0');
  document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;

  const formattedDateISO = getFormattedDate(currentTime);
  document.getElementById('date').textContent = formattedDateISO;

  const shortTimezone = getShortTimezone();
  document.getElementById('timezone').textContent = shortTimezone;

  currentTime.setSeconds(currentTime.getSeconds() + 1);
}

const serverTimeString = document.getElementById('server-time').textContent.trim();
const serverTime = new Date(serverTimeString);

if (isNaN(serverTime)) {
  console.error("Invalid server time:", serverTimeString);
}

let currentTime = new Date(serverTime.getTime());

updateClock();
setInterval(updateClock, 1000);
