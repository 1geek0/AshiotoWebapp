$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 15 // Creates a dropdown of 15 years to control year
  });
$("#radio_time_day_one").click(function(){
    $("#date_one").show();
    $("#card_range").hide();
    $("#slider_overall_range").hide();
});
$("#radio_time_day_between").click(function(){
    $("#date_one").attr("placeholder", "Select Start Date");
    $("#date_one").show();
    $("#date_two").show();
    $("#card_range").hide();
    $("#slider_overall_range").hide();
})