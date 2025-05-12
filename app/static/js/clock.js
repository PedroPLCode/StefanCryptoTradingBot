const serverTimeString = document.getElementById('server-time').textContent.trim();
const serverTime = new Date(serverTimeString);

if (isNaN(serverTime)) {
  console.error("Invalid server time:", serverTimeString);
}

let currentTime = new Date(serverTime.getTime());

function updateClock() {
  const hours = String(currentTime.getHours()).padStart(2, '0');
  const minutes = String(currentTime.getMinutes()).padStart(2, '0');
  const seconds = String(currentTime.getSeconds()).padStart(2, '0');
  document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;

  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  
  const date = new Date();
  const options = { timeZoneName: "short" };
  const shortTimezone = new Intl.DateTimeFormat("en-US", options).format(date);
  
  document.getElementById('timezone').textContent = `${shortTimezone}`;

  currentTime.setSeconds(currentTime.getSeconds() + 1);
}

updateClock();
setInterval(updateClock, 1000);
