var socket = new WebSocket("ws://localhost/websock");

ws.onopen = function(){
    ws.send("Hello Ashioto!");
};

ws.onmessage = function(evt){
    alert(evt.data);
};