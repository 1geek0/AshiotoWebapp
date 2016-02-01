slider = document.getElementById('slider');
var slider_overall_step = document.getElementById('slider_overall_step');
var slider_overall_range = document.getElementById('slider_overall_range');




noUiSlider.create(slider_overall_step, {
    start: 30, // Handle start position
    step: 5, // Slider moves in increments of '10'
    orientation: 'horizontal', // Orient the slider vertically
    animate : true,
    connect : "lower",
    behaviour: 'tap', // Move handle on tap, bar is draggable
    range: { // Slider can select '0' to '100'
        'min': 15,
        'max': 180
    },
});
var value_step = document.getElementById('input_step');
slider_overall_step.noUiSlider.on('update', function(value){value_step.innerHTML = parseInt(value) + " Minutes";});

noUiSlider.create(slider_overall_range, {
    start: 5, // Handle start position
    step: 1, // Slider moves in increments of '10'
    animate : true,
    connect : "lower",
    orientation: 'horizontal', // Orient the slider vertically
    behaviour: 'tap', // Move handle on tap, bar is draggable
    range: { // Slider can select '0' to '100'
        'min': 1,
        'max': 24
    },
});
var value_range = document.getElementById('input_range');
slider_overall_range.noUiSlider.on('update', function(value){value_range.innerHTML = parseInt(value)>1 ? parseInt(value) + " Hours" : parseInt(value) + " Hour";});
                                  
$("#barPlot_overall_btn").click(function(){
    var selected = $("input[type='radio'][name='group1']:checked").val();
    console.log("VAL: " + selected);
    if(selected.search("day") == -1){
        socket.send(JSON.stringify({
            type : 'bar_overall_register',
            event_code : eventCode,
            time_range : $("#input_range").text().replace(/\D/g,''),
            time_step : $("#input_step").text().replace(/\D/g,''),
            time_type : selected
        }));
    } else{
        switch(selected){
            case "day_one":
                socket.send(JSON.stringify({
                    type : 'bar_overall_register',
                    event_code : eventCode,
                    time_range : $("#input_range").text().replace(/\D/g,''),
                    time_step : $("#input_step").text().replace(/\D/g,''),
                    time_type : selected,
                    time_day : parseInt(new Date(moment($("#date_one").val().toString(), "DD MMMM, YYYY")._d).getTime())/1000
                }));
                break;
            case "day_between":
                socket.send(JSON.stringify({
                    type : 'bar_overall_register',
                    event_code : eventCode,
                    time_range : $("#input_range").text().replace(/\D/g,''),
                    time_step : $("#input_step").text().replace(/\D/g,''),
                    time_type : selected,
                    time_one : parseInt(new Date(moment($("#date_one").val().toString(), "DD MMMM, YYYY")._d).getTime())/1000+std_time_offset,
                    time_two : parseInt(new Date(moment($("#date_two").val().toString(), "DD MMMM, YYYY")._d).getTime())/1000+std_time_offset,
                }));
        }
    }
});

//Graphs collapsible
$(document).ready(function(){
    $('#collapsible_graphs').collapsible({
      accordion : false // A setting that changes the collapsible behavior to expandable instead of the default accordion style
    });
  });
function scrollToRange(){
    $('html, body').animate({
        scrollTop: $("#range_graph_div").offset().top
    }, 500);
}
function scrollToOverall(){
    $("html, body").animate({ scrollTop: $(document).height() }, 1000);
}