var socket = new WebSocket("ws://localhost/websock");

socket.onopen = function(){
    socket.send("{{event_code}}");
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

var rightNow = new Date();
var jan1 = new Date(rightNow.getFullYear(), 0, 1, 0, 0, 0, 0);
var temp = jan1.toGMTString();
var jan2 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));
var std_time_offset = (jan1 - jan2) / (1000 * 60 * 60);

socket.onmessage = function(evt){
    console.log(evt);
    var message = jQuery.parseJSON(evt.data);
    //If message is count update
    if(message.hasOwnProperty('gateID')){
        var gateID = message.gateID;
        var count = commaSeparateNumber(parseInt(message.count));
        var oldCount = parseInt(removeCommas($("#count"+gateID).text()));
        console.log("Old Count: ", oldCount);
        var timestamp = message.timestamp+Math.round(std_time_offset);
        var date = new Date(timestamp*1000).format("d M Y h:i:s A");
        
        $("#count"+gateID).text(count);
        $("#timestamp"+gateID).text(date);
        
        var currentTotal = parseInt(removeCommas($("#totalCount").text()));
        console.log("Current: ", currentTotal);
        var newTotal = currentTotal-oldCount+parseInt(message.count);
        console.log("New: ", newTotal);
        $("#totalCount").text(commaSeparateNumber(newTotal));
    }
};