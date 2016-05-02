var socket = new WebSocket("ws://ashioto.in/websock");
var delay_list = ["1-5"];
var color_pallete = ["rgba(96,125,139,", "rgba(0,150,136,", "rgba(0,151,167,", "rgba(198,40,40,"];
socket.onopen = function(){
    socket.send(JSON.stringify({
        type : "browserClient_register",
        event_code : eventCode}));
};

function downloadCanvas(link, canvasId, filename) {
    canvasId = document.getElementById(canvasId);
    var ctx = canvasId.getContext('2d');
    link.href = canvasId.toDataURL('image/png');
    link.download = filename;
}

document.getElementById('chart_download').addEventListener('click', function() {
    downloadCanvas(this, 'barChart_overall', 'test.png');
}, false);

function arrayMax(arr) {
  var len = arr.length, max = -Infinity;
  while (len--) {
    if (arr[len] > max) {
      max = arr[len];
    }
  }
  return max;
};

function commaSeparateNumber(val){
    while (/(\d+)(\d{3})/.test(val.toString())){
      val = val.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
    }
    return val;
  }

function removeCommas(str) {
    while (str.search(",") >= 0) {
        str = (str + "").replace(',', '');
    }
    return str;
};

function secondsToTime(seconds){
    var hours = Math.floor(seconds/3600);
    seconds -= hours*3600;
    var minutes = Math.floor(seconds/60);
    seconds -= minutes*60;
    var toReturn = hours!=0 ? hours + " Hours\n" + minutes + " Minutes" : minutes + " Minutes";
    return toReturn;
}

// Returns a random integer between min and max

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getColorString(){
    var pallete_length = color_pallete.length-1;
    var colorString = color_pallete[getRandomInt(0, pallete_length)];
    return colorString;
}

function updateSliderRange ( min, max ) {
    slider.noUiSlider.destroy();
    noUiSlider.create(slider,{
        start : [min, max],
        step : 1,
        margin: 10, // Handles must be more than '20' apart
        connect: true, // Display a colored bar between the handles
        direction: 'ltr', // Put '0' at the bottom of the slider
        orientation: 'horizontal', // Orient the slider vertically
        behaviour: 'tap-drag', // Move handle on tap, bar is draggable
		range: {
			'min': [ min],
			'max': [ max]
		}
	});
    var valueLow = document.getElementById('input_low'),
        valueHigh = document.getElementById('input_high');
    slider.noUiSlider.on('update', function( values, handle ) {
                if ( handle ) {
                    valueLow.innerHTML = secondsToTime(parseInt(values[handle]));

                } else {
                    valueHigh.innerHTML = secondsToTime(parseInt(values[handle]));
                }
            });
}

var rightNow = new Date();
var jan1 = new Date(rightNow.getFullYear(), 0, 1, 0, 0, 0, 0);
var temp = jan1.toGMTString();
var jan2 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));
std_time_offset = (jan1 - jan2) / (1000 * 60 * 60);

data_range = {
    labels : [],
    datasets: []
}
data_overall = {
    labels : [],
    datasets: []
}

socket.onmessage = function(evt){
    var message = jQuery.parseJSON(evt.data);
    //If message is count update
    switch(message.type){
        case "count_update":
            var gateID = message.gateID;
            var count = commaSeparateNumber(parseInt(message.count));
            var oldCount = parseInt(removeCommas($("#count"+gateID).text()));

            var timestamp = message.timestamp+Math.round(std_time_offset);
            var date = new Date(timestamp*1000).format("d M Y h:i:s A");

            $("#count"+gateID).text(count);
            $("#timestamp"+gateID).text(date);

            var currentTotal = parseInt(removeCommas($("#totalCount").text()));
            var newTotal = currentTotal-oldCount+parseInt(message.count);
            $("#totalCount").text(commaSeparateNumber(newTotal));
        /*case "bargraph_range_data":
            data_range.labels = [];
            data_range.datasets = [];
            if (message.hasOwnProperty('error')){
                console.log("Error: ", message.error);
            }
            else{
                var colorString = getColorString();
                var current_dataset = {
                        label : (message.data.time_start-message.data.time_stop).toString,
                        backgroundColor : colorString+"0.5)",
                        borderColor : colorString+"0.8)",
                        hoverBackgroundColor : colorString+"0.75)",
                        hoverBorderColor : colorString+"1)",
                        data : [],
                    };
                console.log("END COLOR: ", current_dataset);
                gates = message.data.gates;
                gates_number = gates.length;

                if (gates_number==gates_names_list.length){
                    for(var i=0;i<gates_number;i++){
                        var current_gate = gates[i];
                        var current_gate_last = current_gate.last;
                        var current_gate_last_count = current_gate_last.outcount;
                        var current_gate_last_timestamp = current_gate_last.timestamp;

                        var current_gate_secondLast = current_gate.secondLast;
                        var current_gate_secondLast_count = current_gate_secondLast.outcount;
                        var current_gate_secondLast_timestamp = current_gate_secondLast.timestamp;

                        var time_difference = current_gate_last_timestamp-current_gate_secondLast_timestamp;
                        var count_difference = current_gate_secondLast_count-current_gate_last_count;

                        current_dataset.data.push(count_difference);
                        data_range.labels.push("Gate "+(i+1).toString())
                    }
                } else {
                    $("#barChart").remove();
                    //$("#alertCard").remove();
                    Materialize.toast("Data Insufficient To Plot Graph", 4000);
                    var insufficientData_card = document.createElement('div');
                    $(insufficientData_card)
                        .addClass("card red z-depth-3")
                        .html(
                        '<div id="alertCard" class="card red z-depth-3">\
                            <div class="card-content white-text center">\
                                <p class="card-title center" style="font-size: 30px;">Insufficient Data</p>\
                                <h1 style="font-size:30px" class="card-title">The Data Is Insufficient For Plotting A Graph</h1>\
                            </div>\
                        </div>')
                        .appendTo(".container");
                }
                data_range.datasets.push(current_dataset);
                $("#barChart_range").remove();
                var bar_chart = document.createElement('div');
                $(bar_chart).html('<canvas id="barChart_range" width="700px" height="400px"></canvas>').appendTo("#range_graph_div");
                var ctx = document.getElementById("barChart_range").getContext("2d");
                var options = {
                        //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
                        scaleBeginAtZero : true,

                        //Boolean - Whether grid lines are shown across the chart
                        scaleShowGridLines : true,

                        //String - Colour of the grid lines
                        scaleGridLineColor : "rgba(0,0,0,.05)",

                        //Number - Width of the grid lines
                        scaleGridLineWidth : 1,

                        //Boolean - Whether to show horizontal lines (except X axis)
                        scaleShowHorizontalLines: true,

                        //Boolean - Whether to show vertical lines (except Y axis)
                        scaleShowVerticalLines: true,

                        //Boolean - If there is a stroke on each bar
                        barShowStroke : true,

                        //Number - Pixel width of the bar stroke
                        barStrokeWidth : 2,

                        //Number - Spacing between each of the X value sets
                        barValueSpacing : 1,

                        //Number - Spacing between data sets within X values
                        barDatasetSpacing : 1,

                        responsive : true,

                        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].backgroundColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                    }
                var rangeBarChart = new Chart(ctx).Bar(data_range, options);
                $('#barChart_range').css('background-color', 'rgba(255, 255, 255, 1)');
            }
            break; */
        case "bargraph_overall":
            $("#barChart_overall").remove();
            data_overall.labels = [];
            data_overall.datasets = [];
            var time_start = message.data.time_start;
            var steps = message.data.loop;
            var time_step = message.data.time_step;
            var gates = message.data.gates;
            var prev_colors = []
            for(var i=0;i<gates.length;i++){
                var gate_number = i+1;
                var gate_name = "Gate " + gate_number;
                var colorString = getColorString();
                var index = prev_colors.indexOf(colorString);
                if(index!=-1){
                    colorString = getColorString();
                }
                var current_dataset = {
                    label : gate_name,
                    backgroundColor : colorString+"0.5)",
                    borderColor : colorString+"0.8)",
                    borderWidth : 2,
                    hoverBackgroundColor : colorString+"0.75)",
                    hoverBorderColor : colorString+"1)",
                    data : [],
                };
                console.log("DATASET: ",current_dataset);
                current_dataset.data = gates[i];
                data_overall.datasets.push(current_dataset);
            }
            var dataLengths = [];
            for(var i=0;i<data_overall.datasets.length;i++){
                dataLengths.push(data_overall.datasets[i].data.length);
            }
            for(var i=0;i<arrayMax(dataLengths);i++){
                if(!message.hasOwnProperty("between_days")){
                    var step1 = time_start + time_step*i
                    var difference1 = step1-time_start
                    var time1 = new Date(step1*1000).format("h:i:s A");
                    var step2 = time_start + time_step*(i+1)
                    var difference2 = step2-time_start
                    var time2 = new Date(step2*1000).format("h:i:s A");
                    var labelString = time1 + " - " + time2
                    data_overall.labels.push(labelString);
                } else{
                    var step = time_start + time_step*i
                    console.log("Step", time_step);
                    var difference = step-time_start
                    var time = new Date(step*1000).format("d M Y");
                    data_overall.labels.push(time);
                }
            }

            var bar_chart = document.createElement('div');
                $(bar_chart).html('<canvas id="barChart_overall" width="700px" height="400px"></canvas>').appendTo("#overall_graph_div");
                ctx = document.getElementById("barChart_overall").getContext("2d");
                var options = {
                    type : "bar",
                    //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
                    scaleBeginAtZero : true,

                    //Boolean - Whether grid lines are shown across the chart
                    scaleShowGridLines : true,

                    //String - Colour of the grid lines
                    scaleGridLineColor : "rgba(0,0,0,.05)",

                    //Number - Width of the grid lines
                    scaleGridLineWidth : 1,

                    //Boolean - Whether to show horizontal lines (except X axis)
                    scaleShowHorizontalLines: true,

                    //Boolean - Whether to show vertical lines (except Y axis)
                    scaleShowVerticalLines: true,

                    //Boolean - If there is a stroke on each bar
                    barShowStroke : true,

                    //Number - Pixel width of the bar stroke
                    barStrokeWidth : 2,

                    //Number - Spacing between each of the X value sets
                    barValueSpacing : 10,

                    //Number - Spacing between data sets within X values
                    barDatasetSpacing : 0,

                    responsive : true,
                    showXLabels : arrayMax(data_overall.datasets),
                    multiTooltipTemplate: "<%= datasetLabel %> - <%= value %>",

                    legendTemplate : "<ul id=\"legend\" class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].%>\"></span><%if(datasets[i].label.toString()){%><%=datasets[i].label.toString()%><%}%></li><%}%></ul>",
                }
            overallBarChart = 0;
            barJSON = {
                type: "bar",
                data: data_overall,
                options: options
            }
            overallBarChart = new Chart(ctx, barJSON);
            var legend_overall = overallBarChart.generateLegend();
            //$('#barChart_overall').css('background-color', 'rgba(255, 255, 255, 1)');
            $("#barChart_overall").append(legend_overall);
            $("#chart_download").show();
            $("#chart_loader").hide();
            $("#chart_loader2").hide();
            scrollToOverall();
            break;
        case "time_difference_response":
            console.log("TIME: ",message.difference);
            range_difference = message.difference;
            if(range_difference!=0){
            if(range_difference<59){
                    range_limit = range_difference*60;
                    setTimeout(function(){
                        socket.send(JSON.stringify({
                        type : "time_difference",
                        event_code : eventCode
                    }));
                    slider.noUiSlider.destroy();
                    console.log("QUERIED");
                }, 60000);
                $("#range_graph_ul").show();
            noUiSlider.create(slider, {
                start: [ 1,  parseInt(range_difference)*60], // Handle start position
                step: 1, // Slider moves in increments of '10'
                margin: 10, // Handles must be more than '20' apart
                connect: true, // Display a colored bar between the handles
                direction: 'ltr', // Put '0' at the bottom of the slider
                orientation: 'horizontal', // Orient the slider vertically
                behaviour: 'tap-drag', // Move handle on tap, bar is draggable
                range: { // Slider can select '0' to '100'
                    'min': [ 1],
                    'max': [ parseInt(range_difference)*60]
                },
            });
                var valueLow = document.getElementById('input_low'),
                valueHigh = document.getElementById('input_high');

            // When the slider value changes, update the input and span
            slider.noUiSlider.on('update', function( values, handle ) {
                if ( handle ) {
                    valueLow.innerHTML = secondsToTime(parseInt(values[handle]));

                } else {
                    valueHigh.innerHTML = secondsToTime(parseInt(values[handle]));
                }
            });

            } else{
                range_limit = 3599
                $("#range_graph_ul").show();
            noUiSlider.create(slider, {
                start: [ 1,  parseInt(range_difference)*60], // Handle start position
                step: 1, // Slider moves in increments of '10'
                margin: 10, // Handles must be more than '20' apart
                connect: true, // Display a colored bar between the handles
                direction: 'ltr', // Put '0' at the bottom of the slider
                orientation: 'horizontal', // Orient the slider vertically
                behaviour: 'tap-drag', // Move handle on tap, bar is draggable
                range: { // Slider can select '0' to '100'
                    'min': [ 1],
                    'max': [ range_limit]
                },
            });
                var valueLow = document.getElementById('input_low'),
                valueHigh = document.getElementById('input_high');

            // When the slider value changes, update the input and span
            slider.noUiSlider.on('update', function( values, handle ) {
                if ( handle ) {
                    valueLow.innerHTML = secondsToTime(parseInt(values[handle]));

                } else {
                    valueHigh.innerHTML = secondsToTime(parseInt(values[handle]));
                }
            });

            }

            $("#barPlot_btn").click(function(){
                socket.send(JSON.stringify({
                    type : 'bar_range_register',
                    event_code : eventCode,
                    delay1 : $("#input_low").text().replace(" Minutes", ""),
                    delay2 : $("#input_high").text().replace(" Minutes", "")}));
            }
            );
            } else{
                $("#range_graph_ul").hide();
                setTimeout(function(){
                        socket.send(JSON.stringify({
                        type : "time_difference",
                        event_code : eventCode
                    }));
                    console.log("QUERIED");
                }, 60000);
            }
            break;
    }
};
socket.onclose = function(){
    var socket = new WebSocket("ws://ashioto.in/websock");
}
