var event = new String(window.location.host).split(".")[0];
var gates_top = $.get("http://ashioto.xyz/per_gate", {
    eventCode: event
}, function (data) {
    console.log(data);
    $("#basic-content").removeClass("hiddendiv");
    $("#preload-basic").addClass("hiddendiv");
    setTotal();
    setGates();
});

var baseCountCard = "<div class=\"card counts-card-ind ashioto-color tab-item\"><div class=\"row\"><div class=\"col s8 count-gate\"><div class=\"card-content center\"><span class=\"stat-title\">NAME</span></div></div><div class=\"col s4 ashioto-green\"><div class=\"card-content-gate center\"><span class=\"stat-huge\">COUNT</span></div></div></div></div>";

function setGates() {
    var data = gates_top.responseJSON.Gates;
    for (var i = 0; i < data.length; i++) {
        var cardFinal = baseCountCard.replace("NAME", data[i].name).replace("COUNT", data[i].count);
        $("#countHolder").append(cardFinal);
    }
}

function setTotal() {
    var totalCount = 0;
    var data = gates_top.responseJSON.Gates;
    for (var i = 0; i < data.length; i++) {
        totalCount += data[i].count;
    }
    $("#totalcount-figure").text(totalCount);
}
