$("#basic-button").click(function() {
    $("#basic").removeClass("hiddendiv");
    $("#advanced").addClass("hiddendiv");
});
$("#advanced-button").click(function() {
    $("#advanced").removeClass("hiddendiv");
    $("#basic").addClass("hiddendiv");
});