var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);


const trackingCircle = document.getElementById('tracking-circle');
const canvas = document.getElementById('drawing-canvas');
const ctx = canvas.getContext('2d');

let canDraw = true;
let lastSystemState = { pauseStatus: false, patterningStatus: false, clearingStatus: false };

let showLines = false;

function drawCenterCross() {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const size = 10;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Central blue cross
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 1;

    // Solid center cross
    ctx.beginPath();
    ctx.moveTo(centerX - size, centerY);
    ctx.lineTo(centerX + size, centerY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(centerX, centerY - size);
    ctx.lineTo(centerX, centerY + size);
    ctx.stroke();

    if (showLines) {
        // Dotted horizontal and vertical lines
        ctx.strokeStyle = 'blue';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]); // Dotted style

        // Horizontal line
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(canvas.width, centerY);
        ctx.stroke();

        // Vertical line
        ctx.beginPath();
        ctx.moveTo(centerX, 0);
        ctx.lineTo(centerX, canvas.height);
        ctx.stroke();

        ctx.setLineDash([]); // Reset to solid
    }
}
document.getElementById('show-lines-checkbox').addEventListener('change', function () {
    showLines = this.checked;
    drawCenterCross();
});

// Resize canvas
function resizeCanvas() {
    const width = trackingCircle.clientWidth;
    const height = trackingCircle.clientHeight;
    canvas.width = width;
    canvas.height = height;
    ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset any transforms
    drawCenterCross();
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


document.getElementById("clear-canvas").addEventListener("click", () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCenterCross()
    socket.emit("clear_canvas")
    console.log("Canvas cleared");
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

    if (currentPath.length > 0) {
        socket.emit("new_path_sent", currentPath);
        console.log("Emitted new path:", currentPath);

        // Clear the trail
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawCenterCross()

        // Re-plot each (rho, theta) as a small dot
        currentPath = [];
    }
});

socket.on("plot_path", (path) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCenterCross()
    path.forEach(({ rho, theta }) => {
        plotDot(rho, theta, 'red');
    });
});

canvas.addEventListener('mouseleave', () => {
    drawing = false;
    redDot.style.display = 'none';
});

canvas.addEventListener('mouseenter', () => {
    redDot.style.display = 'block';
});

let currentPath = [];

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    redDot.style.left = `${e.clientX}px`;
    redDot.style.top = `${e.clientY}px`;

    if (drawing && canDraw) {
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(x, y);
        ctx.stroke();
        lastX = x;
        lastY = y;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const dx = x - centerX;
        const dy = y - centerY;
        const rawRho = Math.sqrt(dx * dx + dy * dy);
        const maxRadius = Math.min(rect.width, rect.height) / 2;
        const normalizedRho = Math.min(rawRho / maxRadius, 1.0);
        const thetaDegrees = (Math.atan2(-dy, dx) * 180 / Math.PI + 360) % 360;

        currentPath.push({ rho: normalizedRho, theta: thetaDegrees });
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