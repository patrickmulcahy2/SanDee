document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    // Access the settings data passed from the server
    const settingsData = window.settingsData || {};

    // Populate form fields
    if (settingsData.feedrate !== undefined) {
        document.getElementById("feedrate").value = settingsData.feedrate;
    }

    //Rho Gains
    if (settingsPID.kp_Rho !== undefined) {
        document.getElementById("kp-rho").value = settingsData.kp_Rho;
    }

    if (settingsPID.ki_Rho !== undefined) {
        document.getElementById("ki-rho").value = settingsData.ki_Rho;
    }

    if (settingsPID.kd_Rho !== undefined) {
        document.getElementById("kd-rho").value = settingsData.kd_Rho;
    }

    //Theta  Gains
    if (settingsPID.kp_Theta !== undefined) {
        document.getElementById("kp-theta").value = settingsData.kp_Theta;
    }

    if (settingsPID.ki_Theta !== undefined) {
        document.getElementById("ki-theta").value = settingsData.ki_Theta;
    }

    if (settingsPID.kd_Theta !== undefined) {
        document.getElementById("kd-theta").value = settingsData.kd_Theta;
    }


    // Cancel button can optionally reset the form or navigate
    document.querySelector(".cancel-button").addEventListener("click", () => {
        location.reload(); // simple way to reset fields to original server values
    });

    document.querySelector(".PID-button").addEventListener("click", () => {
        window.location.href = "/PID-tuner";
    });

    window.reboot = function(command) {
        const proceed = confirm("⚠️ Warning: Do you wish to reboot the control system?");
        if (!proceed) return

        socket.emit("reboot");
    }

    // Save button handler
    document.querySelector(".save-button").addEventListener("click", () => {
        const updatedSettings = {
            feedrate: parseInt(document.getElementById("feedrate").value),

            kp_Rho: parseInt(document.getElementById("kp-rho").value),
            ki_Rho: parseInt(document.getElementById("ki-rho").value),
            kd_Rho: parseInt(document.getElementById("kd-rho").value),
            kp_Theta: parseInt(document.getElementById("kp-theta").value),
            ki_Theta: parseInt(document.getElementById("ki-theta").value),
            kd_Theta: parseInt(document.getElementById("kd-theta").value),
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
