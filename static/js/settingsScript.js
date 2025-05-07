document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    // Access the settings data passed from the server
    const settingsData = window.settingsData || {};
    const settingsPID = window.settingsPID || {};



// Helper to assign values if they exist
const assignValueIfExists = (id, value) => {
    if (value !== undefined && document.getElementById(id)) {
        document.getElementById(id).value = value;
    }
};

// Populate form fields from settingsData
[
    ["feedrateMax", settingsData.feedrateMax],
    ["feedrateMax_rho", settingsData.feedrateMax_rho],
    ["feedrateMax_theta", settingsData.feedrateMax_theta],
    ["feedrateDefault", settingsData.feedrateDefault],
    ["rhoMax", settingsData.rhoMax],
    ["maxStepover", settingsData.maxStepover],
    ["ballSize", settingsData.ballSize],
    ["clearingStepover", settingsData.clearingStepover],
    ["clearingType", settingsData.clearingType],
].forEach(([id, value]) => assignValueIfExists(id, value));

// Populate PID gains from settingsPID
[
    ["kp-rho", settingsPID.kp_Rho],
    ["ki-rho", settingsPID.ki_Rho],
    ["kd-rho", settingsPID.kd_Rho],
    ["kp-theta", settingsPID.kp_Theta],
    ["ki-theta", settingsPID.ki_Theta],
    ["kd-theta", settingsPID.kd_Theta],
].forEach(([id, value]) => assignValueIfExists(id, value));



    // Cancel button can optionally reset the form or navigate
    document.querySelector(".cancel-button").addEventListener("click", () => {
        location.reload(); // simple way to reset fields to original server values
    });

    document.querySelector(".PID-button").addEventListener("click", () => {
        window.location.href = "/PID_tuner";
    });

    document.querySelector(".home-button").addEventListener("click", () => {
        socket.emit("homeMotors")
    });

    window.reboot = function() {
        const proceed = confirm("⚠️ Warning: Do you wish to reboot the control system?");
        if (!proceed) return

        socket.emit("reboot");
    }


    // Save button handler
    document.querySelector(".save-button").addEventListener("click", () => {
        const updatedSettings = {
            feedrateMax: parseFloat(document.getElementById("feedrateMax").value),
            feedrateMax_rho: parseFloat(document.getElementById("feedrateMax_rho").value),
            feedrateMax_theta: parseFloat(document.getElementById("feedrateMax_theta").value),
            feedrateDefault: parseFloat(document.getElementById("feedrateDefault").value),
            rhoMax: parseFloat(document.getElementById("rhoMax").value),
            maxStepover: parseFloat(document.getElementById("maxStepover").value),
            ballSize: parseFloat(document.getElementById("ballSize").value),
            clearingStepover: parseFloat(document.getElementById("clearingStepover").value),
            clearingType: document.getElementById("clearingType").value,

            kp_Rho: parseFloat(document.getElementById("kp-rho").value),
            ki_Rho: parseFloat(document.getElementById("ki-rho").value),
            kd_Rho: parseFloat(document.getElementById("kd-rho").value),
            kp_Theta: parseFloat(document.getElementById("kp-theta").value),
            ki_Theta: parseFloat(document.getElementById("ki-theta").value),
            kd_Theta: parseFloat(document.getElementById("kd-theta").value),
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
