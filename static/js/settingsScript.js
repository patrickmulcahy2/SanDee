document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    // Access the settings data passed from the server
    const settingsData = window.settingsData || {};

    // Populate form fields
    if (settingsData.chargeTimeout !== undefined) {
        document.getElementById("timeout").value = settingsData.chargeTimeout;
    }

    if (settingsData.supplyVoltage !== undefined) {
        document.getElementById("supply-voltage").value = settingsData.supplyVoltage;
    }

    if (settingsData.supplyWattage !== undefined) {
        document.getElementById("supply-power").value = settingsData.supplyWattage;
    }

    if (settingsData.plotSampleRate !== undefined) {
        document.getElementById("plot-sample-rate").value = settingsData.plotSampleRate;
    }

    if (settingsData.plotLength !== undefined) {
        document.getElementById("plot-length").value = settingsData.plotLength;
    }

    if (settingsData.pressureMultiplier !== undefined) {
        document.getElementById("pressure-multiplier").value = settingsData.pressureMultiplier;
    }

    if (settingsData.pressureOffset !== undefined) {
        document.getElementById("pressure-offset").value = settingsData.pressureOffset;
    }

    if (settingsData.chargeMultiplier !== undefined) {
        document.getElementById("charge-multiplier").value = settingsData.chargeMultiplier;
    }

    if (settingsData.chargeOffset !== undefined) {
        document.getElementById("charge-offset").value = settingsData.chargeOffset;
    }
    // Save button handler
    document.querySelector(".save-button").addEventListener("click", () => {
        const updatedSettings = {
            chargeTimeout: parseInt(document.getElementById("timeout").value),
            supplyVoltage: parseFloat(document.getElementById("supply-voltage").value),
            supplyWattage: parseFloat(document.getElementById("supply-power").value),
            plotSampleRate: parseInt(document.getElementById("plot-sample-rate").value),
            plotLength: parseInt(document.getElementById("plot-length").value),
            pressureMultiplier: parseFloat(document.getElementById("pressure-multiplier").value),
            pressureOffset: parseFloat(document.getElementById("pressure-offset").value),
            chargeMultiplier: parseFloat(document.getElementById("charge-multiplier").value),
            chargeOffset: parseFloat(document.getElementById("charge-offset").value),
        };

        socket.emit("settings_sent", updatedSettings);
        console.log("Settings sent:", updatedSettings);
    });

    // Cancel button can optionally reset the form or navigate
    document.querySelector(".cancel-button").addEventListener("click", () => {
        location.reload(); // simple way to reset fields to original server values
    });

    document.querySelector(".PID-button").addEventListener("click", () => {
        location.reload(); // simple way to reset fields to original server values
    });

    window.reboot = function(command) {
        const proceed = confirm("⚠️ Warning: Do you wish to reboot the control system?");
        if (!proceed) return

        socket.emit("reboot");
    }

function settingsLink() {
    if (!stopCheck) {
        const proceed = confirm("⚠️ Warning: continuing this link will cancel the active cycle.\n\nDo you want to continue?");
        if (!proceed) return;
    }
    window.location.href = "/settings";
}

    document.querySelector(".save-button").addEventListener("click", () => {
        const updatedSettings = {
            chargeTimeout: parseInt(document.getElementById("timeout").value),
            supplyVoltage: parseFloat(document.getElementById("supply-voltage").value),
            supplyWattage: parseFloat(document.getElementById("supply-power").value),
            plotSampleRate: parseInt(document.getElementById("plot-sample-rate").value),
            plotLength: parseInt(document.getElementById("plot-length").value),
            pressureMultiplier: parseFloat(document.getElementById("pressure-multiplier").value),
            pressureOffset: parseFloat(document.getElementById("pressure-offset").value),
            chargeMultiplier: parseFloat(document.getElementById("charge-multiplier").value),
            chargeOffset: parseFloat(document.getElementById("charge-offset").value),
        };

        socket.emit("settings_sent", updatedSettings);
        console.log("Settings sent:", updatedSettings);

        const statusEl = document.getElementById("status-message");
        statusEl.textContent = "Saving settings...";
        statusEl.classList.add("visible");

        // Simulate delay for saving — replace with a confirmation event from server if needed
        setTimeout(() => {
            statusEl.textContent = "Settings saved!";
            setTimeout(() => {
                statusEl.classList.remove("visible");
            }, 2000);
        }, 1000);
    });
});
