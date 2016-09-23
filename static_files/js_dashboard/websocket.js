var socket = new WebSocket("ws://ashioto.in/websock");
var delay_list = ["1-5"];
var color_pallete = ["rgba(96,125,139,", "rgba(0,150,136,", "rgba(0,151,167,", "rgba(198,40,40,"];
socket.onopen = function(){
    socket.send(JSON.stringify({
        type : "browserClient_register",
        event_code : eventCode}));
};

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
      console.log(message);
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
