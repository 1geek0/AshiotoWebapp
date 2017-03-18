$("#report-button").click(function() {
    $.get("/genreport", {},
        function(data) {
            console.log(data);
        }
    )
});