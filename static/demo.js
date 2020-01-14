// Called after form input is processed
function startConnect() {
    // Generate a random client ID
    clientID = "clientID-" + parseInt(Math.random() * 100);

    // Fetch the hostname/IP address and port number from the form
    host = document.getElementById("host").value;
    port = document.getElementById("port").value;

    // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Connecting to: ' + host + ' on port: ' + port + '</span><br/>';
    document.getElementById("messages").innerHTML += '<span>Using the following client value: ' + clientID + '</span><br/>';

    // Initialize new Paho client connection
    client = new Paho.MQTT.Client(host, Number(port), clientID);

    // Set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // Connect the client, if successful, call onConnect function
    client.connect({ 
        onSuccess: onConnect,
    });
}


// Called when the client connects
function onConnect() {
    // Fetch the MQTT topic from the form
    topic = document.getElementById("topic").value;

    // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Subscribing to: ' + topic + '</span><br/>';

    // Subscribe to the requested topic
    client.subscribe(topic);

   // show something on the page to show status\
   document.getElementById("status").innerHTML = '<span class="badge badge-success">Connected</span>';
}

// Called when the client loses its connection
function onConnectionLost(responseObject) {
    console.log("onConnectionLost: Connection Lost");
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost: " + responseObject.errorMessage);
    }
    document.getElementById("status").innerHTML = '<span class="badge badge-danger">Connection Lost</span>';
}

// Called when a message arrives
function onMessageArrived(message) {
    console.log("onMessageArrived: " + message.payloadString);
    var d = new Date();
    var n = d.toLocaleTimeString();
	if (message.destinationName == "home/cputemp") {
	    console.log("cputemp");
	    document.getElementById("cpudiv").innerHTML = '<span>' + message.payloadString + '&deg;<br><br><h5>' + n + '</h5></span>';
    }
	else if (message.destinationName == "home/cathouse") {
            console.log("sensor2");
            document.getElementById("sensor2").innerHTML = "<span>" + message.payloadString + "&deg;<br><br><h5>" + n + "</h5></span>";
    }
	else if (message.destinationName == "home/hottub") {
            console.log("sensor1");
            document.getElementById("sensor1").innerHTML = '<span>' + message.payloadString + "&deg;<br><br><h5>" + n + '</h5></span>';
    }

        else if (message.destinationName == "home/sparesensor") {
            console.log("livingroom");
            document.getElementById("sparesensor").innerHTML = '<span>' + message.payloadString + "&deg;<br><br><h5>" + n + '</h5></span>';
    }   
	
	// document.getElementById("data").innerHTML = '<span>' + message.destinationName + '  = ' + message.payloadString + '</span><br/>';
//    updateScroll(); // Scroll to bottom of window
}

// Called when the disconnection button is pressed
function startDisconnect() {
    client.disconnect();
    document.getElementById("messages").innerHTML = '<span>Disconnected</span><br/>';
    document.getElementById("status").innerHTML = '<span class="badge badge-danger">Not Connected</span>';
    //    updateScroll(); // Scroll to bottom of window
}

// Updates #messages div to auto-scroll
function updateScroll() {
    var element = document.getElementById("data");
    element.scrollTop = element.scrollHeight;
}
