document.addEventListener('DOMContentLoaded', () => {
  const chartContainer = document.getElementById('chart-container');
  const updateButton = document.getElementById('update-chart-button');
  const botSelect = document.getElementById('bot-select');
  let chart;

fetch(`/get_df/`)
    .then(response => response.json())
    .then(data => {
        const allBotsData = data.all_bots_df;

        console.log(typeof allBotsData)
        console.log(Object.keys(allBotsData));
        console.log(JSON.stringify(allBotsData, null, 2));

        console.log(allBotsData);

        if (Array.isArray(allBotsData)) {
            allBotsData.forEach((botData, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = `Bot ${index + 1}`;
                botSelect.appendChild(option);
            });

            updateChart(0, ['close'], allBotsData);
        } else {
            console.error('all_bots_df is not an array:', allBotsData);
        }
    })
    .catch(error => {
        console.error('Error fetching bot data:', error);
    });

    function updateChart(botIndex, selectedIndicators, allBotsData) {
      const botData = allBotsData[botIndex];
      console.log('Bot data:', botData);
  
      if (botData && Array.isArray(botData.data)) {
          const timestamps = botData.data.map(item => new Date(item.open_time));
          const datasets = selectedIndicators.map(indicator => ({
              label: indicator,
              data: botData.data.map(item => item[indicator]),
              borderColor: getRandomColor(),
              borderWidth: 2,
              fill: false,
          }));
  
          if (chart) {
              chart.data.labels = timestamps;
              chart.data.datasets = datasets;
              chart.update();
          } else {
              chart = new Chart(chartContainer, {
                  type: 'line',
                  data: {
                      labels: timestamps,
                      datasets: datasets,
                  },
                  options: {
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                          x: { 
                              type: 'time',
                              time: { unit: 'minute' }
                          },
                          y: { 
                              beginAtZero: false
                          },
                      },
                  },
              });
          }
      } else {
          console.error('Expected botData to contain a data array:', botData);
      }
  }
  
  function getRandomColor() {
      return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
  }
});