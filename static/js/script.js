var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

// ================================
// Hyperlinks with warnings if system is active
// ================================
let stopCheck = true;  // Moved outside of the DOMContentLoaded event listener

socket.on("stopCheck", function (value){
    stopCheck = value;

    let goButton = document.querySelector(".go-button");
    let flowButton = document.querySelector(".flow-button");

    if (!stopCheck) {
        goButton.style.backgroundColor = 'silver';
        flowButton.style.backgroundColor = 'silver';
    } else {
        goButton.style.backgroundColor = 'green';
        flowButton.style.backgroundColor = 'blue';
    }
});

function navigateWithWarning(url) {
    if (!stopCheck) {
        const proceed = confirm("⚠️ Warning: continuing this link will cancel the active cycle.\n\nDo you want to continue?");
        if (!proceed) return;
    }
    window.location.href = url;
}

function new_testID(){
        socket.emit("new_testID");
        socket.emit("check_testID");
    }

document.addEventListener("DOMContentLoaded", function () {
    // Preload images to prevent flickering
    const images = {
        dumpEnabled: "/static/images/dump-enabled.png",
        dumpDisabled: "/static/images/dump-disabled.png",
        chargeEnabled: "/static/images/charge-enabled.png",
        chargeDisabled: "/static/images/charge-disabled.png",
        hvEnabled: "/static/images/hv-enabled.png",
        hvDisabled: "/static/images/hv-disabled.png",
        pressureEnabled: "/static/images/pressure-enabled.png",
        pressureDisabled: "/static/images/pressure-disabled.png",
        safe: "/static/images/safe.png",
        danger: "/static/images/danger.png"
    };

    function updateImage(elementId, newSrc) {
        const imgElement = document.getElementById(elementId);
        if (imgElement.src !== newSrc) {
            imgElement.src = newSrc;
        }
    }

    window.sendCommand = function(command) {
        socket.emit("controlCommand", { command: command });
        console.log(`Sent command: ${command}`);
    }

    function sendPresets() {
        socket.emit("updatePresets", {
            altitude: document.getElementById("altitude").value || 0,
            voltage: document.getElementById("voltage").value || 0,
            pulses: document.getElementById("pulses").value || 0,
            pressureOffset: document.getElementById("pressureOffset").value || 0,
            purgeTime: document.getElementById("purgeTime").value || 0,
            armingCode: document.getElementById("armingCode").value || ""
        });
    }

    socket.on("updateData", function (data) {
        document.getElementById("altitude").value = data.altitudeCurr || 0;
        document.getElementById("voltage").value = data.vSetpoint || 0;
        document.getElementById("pulses").value = data.pulsesRequested || 0;
        document.getElementById("pressureOffset").value = data.pressureOffset || 0;
        document.getElementById("purgeTime").value = data.purgeTime || 0;
        document.getElementById("pressureCurr").innerText = data.currPressureGauge_AltAdj || 0;
        document.getElementById("armingCode").value = data.armingCode || "";

        updateImage("dumpStateImg", data.dumpCurrState ? images.dumpEnabled : images.dumpDisabled);
        updateImage("chargeStateImg", data.chargeCurrState ? images.chargeEnabled : images.chargeDisabled);
        updateImage("hvStateImg", data.hvToggleCurrState ? images.hvEnabled : images.hvDisabled);
        updateImage("pressureStateImg", data.pressureCurrState ? images.pressureEnabled : images.pressureDisabled);
        updateImage("safetyStateImg", data.safetyCurrState ? images.safe : images.danger);

        document.getElementById("triggerCountdown").innerText = data.triggerCountdown || 0;
        document.getElementById("pulseCounter").innerText = data.pulsesCompleted || 0;

        checkCodeColor();
    });
    
    ////////////////////////////////////////////////////
    ///////////////// TEST ID HANDLERS /////////////////
    let testIDPrompted = false;

    socket.emit("check_testID");  // Ask backend on load

    socket.on("testID_status", (data) => {
        if (!data.received) {
            document.getElementById("testIDModal").style.display = "flex";
            testIDPrompted = true;
        }
    });

    document.getElementById("submitTestID").addEventListener("click", () => {
        const testID = document.getElementById("testIDInput").value;
        const timestamp = new Date().toLocaleString();
        if (testID) {
            const timestamped_testID = `[${timestamp}] Test ID: ${testID}`;
            socket.emit("saveLog", timestamped_testID);
            logToConsole(timestamped_testID);
            document.getElementById("testIDModal").style.display = "none";
        } else {
            alert("Please enter a test ID");
        }
    });
    ////////////////////////////////////////////////////
    ////////////////////////////////////////////////////

    function logToConsole(message) {
        const consoleDiv = document.getElementById("console-log");
        const newMessage = document.createElement("div");
        newMessage.textContent = message;
        consoleDiv.appendChild(newMessage);
        consoleDiv.scrollTop = consoleDiv.scrollHeight; // Auto-scroll
    }

    socket.on("logMessage", function (data) {
        const timestamp = new Date().toLocaleString();
        let logEntry = "";

        if (data.type === "go") {
            logEntry = `[${timestamp}] Beginning ${data.pulsesRequested} Pulses, Voltage: ${data.vSetpoint} kV`;
        }
        else if (data.type === "stopped") {
            logEntry = `[${timestamp}] Pulses canceled, ${data.pulsesCompleted} completed`;
        }
        else if (data.type === "individualPulse") {
            logEntry = `[${timestamp}] Pulse number ${data.pulsesCompleted} completed with cycle time of ${data.currentCycleTime} Seconds`;
        }
        else if (data.type === "completed") {
            logEntry = `[${timestamp}] ${data.pulsesCompleted} pulses completed with average cycle time of ${data.avgCycleTime} Seconds`;
        }
        else if (data.type === "flow"){
            logEntry = `[${timestamp}] 5' Flow Started`;
        }
        else if (data.type === "flowDone"){
            logEntry = `[${timestamp}] 5' Flow Completed`;
        }
        else if (data.type === "flowCancelled"){
            logEntry = `[${timestamp}] Flow Cancelled after ${data.timeCompleted} Seconds`;
        }
        else if(data.type === "error"){
            logEntry = `[${timestamp}] ${data.errorMessage}`;
        }


        if (logEntry) {
            logToConsole(logEntry);
            socket.emit("saveLog", logEntry);  
        }
    });


    ////////////////////////////////////////////////////
    ///////////////// COUNTDOWN AUIDO //////////////////
    const audioPath = new Audio("/static/audio/countdown.mp3");

    socket.on("threeSecondAudio", function(){
        audioPath.play()
    });

    ////////////////////////////////////////////////////////
    ///////////////// ARMING CODE HANDLERS /////////////////
    let armingCodeInput = document.getElementById("armingCode");
    function checkCodeColor(){
        const currCode = armingCodeInput.value;

        if (currCode.length === 0 ) {
            armingCodeInput.style.backgroundColor = "yellow";
        } else {
            socket.emit("validateArmingCode", {
                code: currCode,
            });
        }
    }

    socket.on("armingCodeValid", function(isValid){
        if (isValid == 1){
            armingCodeInput.style.backgroundColor = "green";
        } else {
            armingCodeInput.style.backgroundColor = "red";
        }

    });
    socket.on("armingCodeIncorrect", function() {
        let button = document.querySelector(".go-button");
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                button.classList.add("flash-red");
                setTimeout(() => {
                    button.classList.remove("flash-red");
                }, 500);
            }, i * 550); // 1000ms (1s) interval between flashes
        }
    });

    armingCodeInput.addEventListener("input", function () {
        checkCodeColor();
    });

    document.querySelectorAll(".presets input, #armingCode").forEach(input =>
        input.addEventListener("input", sendPresets)
    );

});