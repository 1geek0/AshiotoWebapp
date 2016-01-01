var socket = new WebSocket("ws://localhost/websock");
var delay_list = [];
socket.onopen = function(){
    socket.send(JSON.stringify({
        type : "browserClient_register", 
        event_code : eventCode}));
    delay_list.forEach(function(range){
        var ranges = range.split("-");
        socket.send(JSON.stringify({
            type : "barchart_register",
            event_code : eventCode,
            delay1 : ranges[0],
            delay2 : ranges[1],
        }));
        console.log("SENDING REQ");
    });
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


var rightNow = new Date();
var jan1 = new Date(rightNow.getFullYear(), 0, 1, 0, 0, 0, 0);
var temp = jan1.toGMTString();
var jan2 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));
var std_time_offset = (jan1 - jan2) / (1000 * 60 * 60);

data = {
    labels : [],
    datasets: [
    ]
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
        case "bargraph_data":
            data.labels = [];
            data.datasets = [];
            if (message.hasOwnProperty('error')){
                console.log("Error: ", message.error);
            }
            else{
                console.log("Message", message);
                colorString = "rgba("+
                                    getRandomInt(0,255).toString()+","+
                                    getRandomInt(0,255).toString()+","+
                                    getRandomInt(0,255).toString();
                var current_dataset = {
                        label : (message.data.time_start-message.data.time_stop).toString,
                        fillColor : colorString+",0.5)",
                        strokeColor : colorString+",0.8)",
                        highlightFill : colorString+",0.75)",
                        highlightStroke : colorString+",1)",
                        data : [],
                    };
                gates = message.data.gates;
                console.log("Gates: ", gates);
                gates_number = gates.length;
                console.log("Number: ", gates_number);
                if (gates_number==gates_names_list.length){
                    for(var i=0;i<gates_number;i++){
                        var current_gate = gates[i];
                        console.log("Current Gate: ", current_gate);
                        var current_gate_last = current_gate.last;
                        var current_gate_last_count = current_gate_last.outcount;
                        var current_gate_last_timestamp = current_gate_last.timestamp;

                        var current_gate_secondLast = current_gate.secondLast;
                        var current_gate_secondLast_count = current_gate_secondLast.outcount;
                        var current_gate_secondLast_timestamp = current_gate_secondLast.timestamp;

                        var time_difference = current_gate_last_timestamp-current_gate_secondLast_timestamp;
                        var count_difference = current_gate_secondLast_count-current_gate_last_count;

                        current_dataset.data.push(count_difference);
                        data.labels.push("Gate "+(i+1).toString())
                    }
                } else {
                    $("#barChart").remove();
                    $("#alertCard").remove();
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
                console.log("Current Dataset: ", current_dataset);
                data.datasets.push(current_dataset);
                $("#barChart").remove();
                var bar_chart = document.createElement('div');
                $(bar_chart).html('<canvas id="barChart" width="700px" height="400px"></canvas>').appendTo("#graph_div");
                var ctx = document.getElementById("barChart").getContext("2d");
                options = {
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
                    
                        //responsive : true,
                        
                        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                    }
                var ashiotoBarChart = new Chart(ctx).Bar(data, options);
                $('#barChart').css('background-color', 'rgba(255, 255, 255, 1)');
            }
    }
};