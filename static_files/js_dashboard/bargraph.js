var slider = document.getElementById('slider');
var slider_overall_step = document.getElementById('slider_overall_step');
var slider_overall_range = document.getElementById('slider_overall_range');

noUiSlider.create(slider, {
    start: [ 15, 1 ], // Handle start position
    step: 1, // Slider moves in increments of '10'
    margin: 10, // Handles must be more than '20' apart
    connect: true, // Display a colored bar between the handles
    direction: 'ltr', // Put '0' at the bottom of the slider
    orientation: 'horizontal', // Orient the slider vertically
    behaviour: 'tap-drag', // Move handle on tap, bar is draggable
    range: { // Slider can select '0' to '100'
        'min': 1,
        'max': 3599
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

$("#barPlot_btn").click(function(){
    socket.send(JSON.stringify({
        type : 'bar_range_register',
        event_code : eventCode,
        delay1 : $("#input_low").text().replace(" Minutes", ""),
        delay2 : $("#input_high").text().replace(" Minutes", "")}));
}
);

noUiSlider.create(slider_overall_step, {
    start: 15, // Handle start position
    step: 15, // Slider moves in increments of '10'
    orientation: 'horizontal', // Orient the slider vertically
    animate : true,
    behaviour: 'tap', // Move handle on tap, bar is draggable
    range: { // Slider can select '0' to '100'
        'min': 15,
        'max': 150
    },
});
var value_step = document.getElementById('input_step');
slider_overall_step.noUiSlider.on('update', function(value){value_step.innerHTML = parseInt(value) + " Minutes";});

noUiSlider.create(slider_overall_range, {
    start: 1, // Handle start position
    step: 1, // Slider moves in increments of '10'
    animate : true,
    orientation: 'horizontal', // Orient the slider vertically
    behaviour: 'tap', // Move handle on tap, bar is draggable
    range: { // Slider can select '0' to '100'
        'min': 1,
        'max': 4
    },
});
var value_range = document.getElementById('input_range');
slider_overall_range.noUiSlider.on('update', function(value){value_range.innerHTML = parseInt(value) + " Hours";});
                                  
$("#barPlot_overall_btn").click(function(){
    socket.send(JSON.stringify({
        type : 'bar_overall_register',
        event_code : eventCode,
        time_range : $("#input_range").text().replace(" Hours", ""),
        time_step : $("#input_step").text().replace(" Minutes", "")
    }))
});