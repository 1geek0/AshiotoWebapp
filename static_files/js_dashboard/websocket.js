var socket = new WebSocket("ws://localhost/websock");

socket.onmessage = function(evt){
    if(evt.data === "Reload"){
        console.log(evt.data);
        location.reload(true);
    }
};

socket.onopen = function(){
    setTimeout(function(){
        socket.send("Refresh");
    }, 2000);
}

setInterval(refresh_function, 5000);

var refresh_function = new function(){
    socket.send("Refresh");
};