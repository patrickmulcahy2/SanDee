var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

socket.on("updateInputs", function (data){
    document.getElementById("feedrateOffset").value = data.userInputs.feedrateOffset || 0
    document.getElementById("feedrate").value = data.settingsData.feedrate || 0

});


socket.on("updatePosition", function (data){
    document.getElementById("rhoCurrPosVal").value = data.currPosition.rhoCurr || 0
    document.getElementById("thetaCurrPosVal").value = data.currPosition.thetaCurr || 0

    console.log(data.reqPosition.rhoReq)

    document.getElementById("rhoReqPosVal").value = data.reqPosition.rhoReq || 0
    document.getElementById("thetaReqPosVal").value = data.reqPosition.thetaReq|| 0

    document.getElementById("rhoErrorVal").value = (data.currPosition.rhoCurr - data.reqPosition.rhoReq)|| 0
    document.getElementById("thetaErrorVal").value = (data.currPosition.thetaCurr - data.reqPosition.thetaReq) || 0

});

// JavaScript to track the mouse position inside the circle
const trackingCircle = document.getElementById('tracking-circle');

// Red dot element
const redDot = document.createElement('div');
redDot.style.position = 'absolute';
redDot.style.width = '10px';
redDot.style.height = '10px';
redDot.style.backgroundColor = 'red';
redDot.style.borderRadius = '50%';
redDot.style.pointerEvents = 'none'; // allow mouse events to pass through
redDot.style.transform = 'translate(-50%, -50%)';
redDot.style.display = 'none'; // hidden initially
document.body.appendChild(redDot);

trackingCircle.addEventListener('mouseenter', () => {
    redDot.style.display = 'block';
});

trackingCircle.addEventListener('mouseleave', () => {
    redDot.style.display = 'none';
});

// Tracking mouse position within the circle
trackingCircle.addEventListener('mousemove', (e) => {
    const rect = trackingCircle.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Calculate the center of the circle
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    // Calculate the distance (rho) from the center of the circle
    const rho = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));

    // Calculate the angle (theta) in radians
    const theta = Math.atan2(y - centerY, x - centerX); // angle in radians

    // Update red dot position
    redDot.style.left = `${x + rect.left}px`;
    redDot.style.top = `${y + rect.top}px`;

    console.log(`Mouse X: ${x}, Mouse Y: ${y}`);
    console.log(`Polar Coordinates -> r: ${rho}, θ: ${theta}`);

    // Emit the polar coordinates to the backend
    socket.emit('sendPolarCoordinates', { theta, rho });
});

