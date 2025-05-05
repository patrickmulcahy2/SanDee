var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);


socket.on("updateInputs", function (data){
    document.getElementById("feedrateOffset").value = data.userInputs.feedrateOffset || 0
    document.getElementById("feedrate").value = data.userInputs.feedrate || 0

});

socket.on("statusPercent", percent => {
    // Clamp percent between 0 and 100 just in case
    const clampedPercent = Math.max(0, Math.min(100, percent));
    document.getElementById("status-fill").style.width = clampedPercent + "%";
});

function sendCommand(command) {
    if (command === "go") {
        const dropdown = document.getElementById("toolpath-dropdown");
        if (!dropdown || dropdown.selectedIndex <= 0) {
            alert("No toolpath selected!");
            return;
        }
    }
    socket.emit(command);
}

socket.on("systemStates", ({ pauseStatus, patterningStatus, clearingStatus }) => {
    const goBtn = document.querySelector(".go-button");
    const pauseBtn = document.querySelector(".pause-button");
    const clearBtn = document.querySelector(".clear-button");

    // Update button text for pause state
    if (pauseStatus) {
        goBtn.textContent = "RESUME";
        pauseBtn.textContent = "CANCEL";
    } else {
        goBtn.textContent = "GO";
        pauseBtn.textContent = "PAUSE";
    }


    // Disable buttons based on state 
    if (clearingStatus && pauseStatus){
        goBtn.disabled = false;
        clearBtn.disabled = true;
        goBtn.classList.remove('disabled');
        clearBtn.classList.add('disabled');
    }
     else if (clearingStatus) {
        goBtn.disabled = true;
        clearBtn.disabled = true;
        goBtn.classList.add('disabled');
        clearBtn.classList.add('disabled');
    } else if (patterningStatus) {
        clearBtn.disabled = true;
        clearBtn.classList.add('disabled');
        goBtn.disabled = false;
        goBtn.classList.remove('disabled');
    } else if (pauseStatus) {
        clearBtn.disabled = true;
        clearBtn.classList.add('disabled');
        goBtn.disabled = false;
        goBtn.classList.remove('disabled');
    } else {
        goBtn.disabled = false;
        clearBtn.disabled = false;
        goBtn.classList.remove('disabled');
        clearBtn.classList.remove('disabled');
    }
});

document.addEventListener("DOMContentLoaded", function () {

    function sendPresets() {
        socket.emit("updatePresets", {
            feedrateOffset: document.getElementById("feedrateOffset").value || 0,
        });
    }

    document.querySelectorAll(".presets input, #armingCode").forEach(input =>
        input.addEventListener("input", sendPresets)
    );
});
