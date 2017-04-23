var event_ashioto = getParameterByName('eventCode');
var graphSocket = new WebSocket("ws://" + event_ashioto + "." + window.location.host + "/websock");
graphSocket.onclose = function() {
    graphSocket = new WebSocket("ws://" + event_ashioto + "." + window.location.host + "/websock");
};
// Set the onClick listener for the button
$("#fetch-graph-btn").click(function() {
    getData();
});

function checkHour() {
    var startDate = Date.parse($("#date-start").pickadate().get()[0].value);
    var endDate = Date.parse($("#date-end").pickadate().get()[0].value);
    if (startDate == endDate) {
        var startHour = $('select[name=start-hour-selector]').val();
        var endHour = $('select[name=end-hour-selector]').val();
        if (endHour < startHour) {
            return false;
        } else {
            return true;
        }
    } else {
        return true;
    }
}

function checkDate() {
    var startDate = Date.parse($("#date-start").pickadate().get()[0].value);
    var endDate = Date.parse($("#date-end").pickadate().get()[0].value) + 86400000;
    if (endDate < startDate) {
        return false;
    } else {
        return true;
    }
}

function checkConditions() {
    if (checkDate() && checkHour()) {
        return true;
    } else {
        return false;
    }
}

function getStartTimestamp() {
    var startDate = Date.parse($("#date-start").pickadate().get()[0].value);
    var startHour = $('select[name=start-hour-select]').val();
    return startDate + (startHour * 3600000);
}

function getEndTimestamp() {
    var endDate;
    var endHour;
    if (isMultiDay()) {
        endDate = Date.parse($("#date-end").pickadate().get()[0].value);
        endHour = 23;
    } else {
        endDate = Date.parse($("#date-start").pickadate().get()[0].value);
        endHour = $('select[name=end-hour-select]').val();
    }
    return (endDate + 86400000) - ((24 - endHour) * 3600000);
}

function isMultiDay() {
    if ($('input[name=graphytypeRadio]')[0].checked === true) {
        return false;
    } else {
        return true;
    }
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

function dataSize(data) {
    var maxSize = 0;
    for (var i = 0; i < data.length; i++) {
        var seriesLength = data[i].data.length;
        if (seriesLength > maxSize) {
            maxSize = seriesLength;
        }
    }
    return maxSize;
}

function plotTimeGraph(data) {
    var options = {
        axisX: {
            type: Chartist.AutoScaleAxis,
            scaleMinSpace: 40,
            labelInterpolationFnc: function(value) {
                if (isMultiDay()) {
                    return moment(value).format('hh:mm a MMM D');
                } else {
                    return moment(value).format('hh:mm a');
                }
            }
        },
        axisY: {
            type: Chartist.AutoScaleAxis
        },
        low: 0,
        showPoint: true,
        fullWidth: true,
        showGrid: false,
        showLabel: true,
        chartPadding: {
            right: 40
        },
        plugins: [
            Chartist.plugins.ctPointLabels({
                textAnchor: 'middle',
                labelInterpolationFnc: function(value) {
                    return value.split(", ")[1];
                }
            }),
        ]
    };
    var timeChart = new Chartist.Line("#countChart", data, options);
    timeChart.on('draw', function(data) {
        if (data.type === 'line' || data.type === 'area') {
            data.element.animate({
                d: {
                    begin: 200 * data.index,
                    dur: 800,
                    from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
                    to: data.path.clone().stringify(),
                    easing: Chartist.Svg.Easing.easeOutQuint
                }
            });
        }
    });
}


graphSocket.onmessage = function(evt) {
    var data = JSON.parse(evt.data);
    console.log(data);
    // var dataPointNumber = dataSize(data);
    // var maxDataPoints = 24;
    // var chartData = {
    //     series: [

    //     ]
    // };
    // for (var i = 0; i < data.length; i++) {
    //     var seriesItem = {};
    //     seriesItem.name = data[i].name;
    //     seriesItem.data = [];
    //     var gateDataLength = data[i].data.length;
    //     var dataPointSkip = Math.round(gateDataLength / maxDataPoints);
    //     for (var j = 0; j < gateDataLength; j++) {
    //         var k = j === 0 ? 0 : j * dataPointSkip;
    //         if (k > gateDataLength) {
    //             break;
    //         } else {
    //             seriesItem.data.push({
    //                 x: data[i].data[k][0],
    //                 y: data[i].data[k][1]
    //             });
    //         }
    //     }
    //     chartData.series.push(seriesItem);
    // }
    // plotTimeGraph(chartData);
};


graphSocket.onopen = function(evt) {
    graphSocket.send(JSON.stringify({
        type: "day-hourly",
        startTimestamp: 1492885800000,
        event: "disq"
    }));
};