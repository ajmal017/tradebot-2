var container = document.getElementById('chart-container');

var chartWidth = 600;
var chartHeight = 300;

var chart = LightweightCharts.createChart(container, {
    width: chartWidth,
    height: chartHeight,
    priceScale: {
        scaleMargins: {
            top: 0.2,
            bottom: 0.1,
        },
    },
    timeScale: {
        rightOffset: 1,
    },
});

var areaSeries = chart.addAreaSeries({
  topColor: 'rgba(245, 124, 0, 0.4)',
  bottomColor: 'rgba(245, 124, 0, 0.1)',
  lineColor: 'rgba(245, 124, 0, 1)',
  lineWidth: 2,
});

// Get data
const url = "https://paper-api.alpaca.markets/v2/account/portfolio/history"
const API_KEY_ID='PK5WM1SLZKYEA4B8IM98'
const API_SECRET_KEY='lMhBVSeTo2FCSGsuQTvWqqHB6zG1dqbcxqVOwSaV'

const auth_headers = {
    'APCA-API-KEY-ID': API_KEY_ID, 
    'APCA-API-SECRET-KEY': API_SECRET_KEY
}

const res = fetch(url, {headers:auth_headers})
.then(res => res.json())
.then(data => {
    const chart = []
    const timestamps = data['timestamp']
    const equity = data['equity']
    let i = 0;
    for (i = 0; i < timestamps.length; i++){
        // Parse date
        var newDate = new Date();
        newDate.setTime(timestamps[i]*1000);
        var dd = String(newDate.getDate()).padStart(2, '0');
        var mm = String(newDate.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = newDate.getFullYear();
        dateString = yyyy + '-' + mm + '-' + dd;

        // Add date:equity to chart
        chart.push({
            time: dateString,
            value: equity[i]
        })
    }
    console.log(chart)
    areaSeries.setData(chart); // Add data to line
})

chart.timeScale().scrollToPosition(-1, false);

var width = 27;
var height = 27;

var button = document.createElement('div');
button.className = 'go-to-realtime-button';
button.style.left = (chartWidth - width - 60) + 'px';
button.style.top = (chartHeight - height - 30) + 'px';
button.style.color = '#4c525e';
button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14" width="14" height="14"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M6.5 1.5l5 5.5-5 5.5M3 4l2.5 3L3 10"></path></svg>';
document.body.appendChild(button);

var timeScale = chart.timeScale();
chart.subscribeVisibleTimeRangeChange(function() {
    var buttonVisible = timeScale.scrollPosition() < 0;
    button.style.display = buttonVisible ? 'block' : 'none';
});

button.addEventListener('click', function() {
    timeScale.scrollToRealTime();
});

button.addEventListener('mouseover', function() {
    button.style.background = 'rgba(250, 250, 250, 1)';
    button.style.color = '#000';
});

button.addEventListener('mouseout', function() {
    button.style.background = 'rgba(250, 250, 250, 0.6)';
    button.style.color = '#4c525e';
});

