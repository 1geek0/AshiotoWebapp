var slider = document.getElementById('slider');

noUiSlider.create(slider, {
    start: [ 20, 80 ], // Handle start position
    step: 1, // Slider moves in increments of '10'
    margin: 1, // Handles must be more than '20' apart
    connect: true, // Display a colored bar between the handles
    direction: 'ltr', // Put '0' at the bottom of the slider
    orientation: 'horizontal', // Orient the slider vertically
    behaviour: 'tap-drag', // Move handle on tap, bar is draggable
    range: { // Slider can select '0' to '100'
        'min': 1,
        'max': 3600
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
        type : 'barchart_register',
        event_code : eventCode,
        delay1 : $("#input_low").text().replace(" Minutes", ""),
        delay2 : $("#input_high").text().replace(" Minutes", "")}));
}
);