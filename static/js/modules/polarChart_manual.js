var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);


const trackingCircle = document.getElementById('tracking-circle');
const canvas = document.getElementById('drawing-canvas');
const ctx = canvas.getContext('2d');

let canDraw = true;
let lastSystemState = { pauseStatus: false, patterningStatus: false, clearingStatus: false };

socket.on("systemStates", ({ pauseStatus, patterningStatus, clearingStatus }) => {
    lastSystemState = { pauseStatus, patterningStatus, clearingStatus };
    canDraw = !pauseStatus && !patterningStatus && !clearingStatus;

    if (!canDraw) {
        console.log("Drawing disabled due to system state.");
    }
});


// Resize canvas
function resizeCanvas() {
    const width = trackingCircle.clientWidth;
    const height = trackingCircle.clientHeight;
    canvas.width = width;
    canvas.height = height;
    ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset any transforms
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Create red dot cursor
const redDot = document.createElement('div');
redDot.style.position = 'absolute';
redDot.style.width = '10px';
redDot.style.height = '10px';
redDot.style.backgroundColor = 'red';
redDot.style.borderRadius = '50%';
redDot.style.pointerEvents = 'none';
redDot.style.transform = 'translate(-50%, -50%)';
redDot.style.display = 'none';
document.body.appendChild(redDot);

// Track drawing state
let drawing = false;
let lastX, lastY;



function clearDrawing() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    console.log("Clearing canvas!")
}

socket.on("clearPlot", function (data) {
    clearDrawing()
});

// Mouse events
canvas.addEventListener('mousedown', (e) => {
    drawing = true;
    const rect = canvas.getBoundingClientRect();
    lastX = e.clientX - rect.left;
    lastY = e.clientY - rect.top;
});

canvas.addEventListener('mouseup', () => {
    drawing = false;
});

canvas.addEventListener('mouseleave', () => {
    drawing = false;
    redDot.style.display = 'none';
});

canvas.addEventListener('mouseenter', () => {
    redDot.style.display = 'block';
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Move red dot
    redDot.style.left = `${e.clientX}px`;
    redDot.style.top = `${e.clientY}px`;

    if (drawing && canDraw) {
        // Draw trail
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(x, y);
        ctx.stroke();
        lastX = x;
        lastY = y;

        // Emit polar coordinates
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const dx = x - centerX;
        const dy = y - centerY;
        const rawRho = Math.sqrt(dx * dx + dy * dy);
        const maxRadius = Math.min(rect.width, rect.height) / 2;
        const normalizedRho = Math.min(rawRho / maxRadius, 1.0); // Clamp to 1.0
        const thetaDegrees = (Math.atan2(-dy, dx) * 180 / Math.PI + 360) % 360; // [0, 360)

        socket.emit('sendPolarCoordinates', {
            rho: normalizedRho,
            theta: thetaDegrees
        });
    }
});

const plotDot = (rho, theta, color) => {
    const rect = canvas.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const maxRadius = Math.min(rect.width, rect.height) / 2;

    const radius = rho * maxRadius;
    const angleRad = theta * Math.PI / 180;
    const x = centerX + radius * Math.cos(angleRad);
    const y = centerY - radius * Math.sin(angleRad); // y is inverted in canvas


    dotRadius = 1;
    ctx.beginPath();
    ctx.arc(x, y, dotRadius, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
};

//Auto draw real positions
socket.on("updatePosition", function (data) {
    //if canDraw is false, means auto operation in progress
    if (!canDraw) {
        plotDot(data.currPosition.rhoCurr/data.rhoMax, data.currPosition.thetaCurr, 'blue');   // Current in blue
        plotDot(data.reqPosition.rhoReq/data.rhoMax, data.reqPosition.thetaReq, 'green');      // Requested in green
    }
});