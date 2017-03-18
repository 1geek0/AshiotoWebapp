$("#graph-oneday").click(function () {
    $("#date-end-p").attr("hidden", "hidden");
    $("#date-start-label").text("Date");
    $("#date-start-p").attr("class", "col s12");
    $("#hour-div").removeAttr("hidden");
});
$("#graph-multiday").click(function () {
    $("#date-end-p").removeAttr("hidden");
    $("#date-start-label").text("Start Date");
    $("#date-start-p").attr("class", "col s6");
    $("#hour-div").attr("hidden", "hidden");
});
