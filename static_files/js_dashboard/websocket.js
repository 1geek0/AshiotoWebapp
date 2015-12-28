var socket = new WebSocket("ws://localhost/websock");

socket.onopen = function(){
    socket.send("Hello Ashioto!");
};

socket.onmessage = function(evt){
    console.log(evt);
};