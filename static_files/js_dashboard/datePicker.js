$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 15 // Creates a dropdown of 15 years to control year
  });
$("#radio_time_day_one").click(function(){
    $("#date_one").attr("placeholder", "Select Date To Show Stats Of");
    $("#date_one").show();
    $("#date_two").hide();
    $("#card_step").show();
    $("#card_range").hide();
    $("#slider_overall_range").hide();
});
$("#radio_time_day_between").click(function(){
    $("#date_one").attr("placeholder", "Select Start Date");
    $("#date_one").show();
    $("#date_two").show();
    $("#card_step").hide();
    $("#card_range").hide();
    $("#slider_overall_range").hide();
    $("#slider_overall_step").hide();
});
$("#radio_time_start").click(function(){
    $("#date_one").hide();
    $("#date_two").hide();
    $("#card_step").show();
    $("#card_range").show();
    $("#slider_overall_range").show();
});
$("#radio_event_start").click(function(){
    $("#date_one").hide();
    $("#date_two").hide();
    $("#card_step").show();
    $("#card_range").show();
    $("#slider_overall_range").show();
});