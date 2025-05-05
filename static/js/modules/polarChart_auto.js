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

function clearDrawing() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    console.log("Clearing canvas!");
}

socket.on("clearPlot", function () {
    clearDrawing();
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

    const dotRadius = 1;
    ctx.beginPath();
    ctx.arc(x, y, dotRadius, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
};

// Auto draw real positions
socket.on("updatePosition", function (data) {
    if (!canDraw) {
        plotDot(data.currPosition.rhoCurr / data.rhoMax, data.currPosition.thetaCurr, 'blue');
        plotDot(data.reqPosition.rhoReq / data.rhoMax, data.reqPosition.thetaReq, 'green');
    }
});
