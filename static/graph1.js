URL = "http://127.0.0.1:5000/api1"

$(function () {
  $('#submit').bind('click', function () {
    $.getJSON(URL, {
      symbol: $('input[name="symbol"]').val(),
      start: $('input[name="start"]').val(),
      end: $('input[name="end"]').val()
    }, function (data) {
      console.log(data.result["nse_data"]);
      var nseData = data.result["nse_data"];
      renderGraph(nseData);
    });
    return false;
  });
});


function renderGraph(nseData) {
  var div = document.getElementById("graph-div");

  var graphHeading = document.createElement("h3");
  graphHeading.innerHTML = "Graph for " + nseData['Symbol']
  div.appendChild(graphHeading);

  var graphDiv = document.createElement("div");
  graphDiv.id = "graph";
  div.appendChild(graphDiv);


  var trace1 = {

    x: nseData["Dates"],
    close: nseData["Close"],
    decreasing: { line: { color: '#7F7F7F' } },
    high: nseData["High"],
    increasing: { line: { color: '#17BECF' } },
    line: { color: 'rgba(31,119,180,1)' },
    low: nseData["Low"],
    open: nseData["Open"],
    type: 'ohlc',
    xaxis: 'x',
    yaxis: 'y'
  };

  var data = [trace1];

  var layout = {
    dragmode: 'zoom',
    margin: {
      r: 10,
      t: 25,
      b: 40,
      l: 60
    },
    showlegend: false,
    xaxis: {
      autorange: true,
      rangeslider: { visible: false },
      title: "Graph for " + nseData['Symbol'],
      type: 'date'
    },
    yaxis: {
      autorange: true,
      type: 'linear'
    }
  };

  Plotly.newPlot('graph', data, layout);
}