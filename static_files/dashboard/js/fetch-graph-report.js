var event_ashioto = (window.location.host).split(".")[0];
var graphSocket = new WebSocket("ws://" + window.location.host + "/websock");
graphSocket.onclose = function() {
    graphSocket = new WebSocket("ws://" + window.location.host + "/websock");
};

function getStartTimestamp() {
    var startDate = Date.parse($("#date-start").pickadate().get()[0].value);
    var startHour = $('select[name=start-hour-select]').val();
    return startDate + (startHour * 3600000);
}

function getData() {
    if (checkConditions()) {
        var startTime = getStartTimestamp();
        var args = JSON.stringify({
            'type': "time-range",
            'event': event_ashioto,
            'time-range': {
                'start': startTime,
                'end': getEndTimestamp()
            }
        });
        graphSocket.send(args);
    } else {
        Materialize.toast("Please check graph configuration");
    }
}

graphSocket.onmessage = function(evt) {
    var data = JSON.parse(evt.data);
    console.log(data);
    var dataPointNumber = dataSize(data);
    var maxDataPoints = 25;
    var chartData = {
        series: [

        ]
    };
    for (var i = 0; i < data.length; i++) {
        var seriesItem = {};
        seriesItem.name = data[i].name;
        seriesItem.data = [];
        var gateDataLength = data[i].data.length;
        var dataPointSkip = Math.round(gateDataLength / maxDataPoints);
        for (var j = 0; j < gateDataLength; j++) {
            var k = j === 0 ? 0 : j * dataPointSkip;
            if (k > gateDataLength) {
                break;
            } else {
                seriesItem.data.push({
                    x: data[i].data[k][0],
                    y: data[i].data[k][1]
                });
            }
        }
        chartData.series.push(seriesItem);
    }
    plotTimeGraph(chartData);
};