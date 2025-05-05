document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    // Access the settings data passed from the server
    const settingsData = window.settingsData || {};
    const settingsPID = window.settingsPID || {};

    // Populate form fields
    if (settingsData.feedrateMax !== undefined) {
        document.getElementById("feedrateMax").value = settingsData.feedrateMax;
    }

    if (settingsData.feedrateMax_rho !== undefined) {
        document.getElementById("feedrateMax_rho").value = settingsData.feedrateMax_rho;
    }

    if (settingsData.feedrateMax_theta !== undefined) {
        document.getElementById("feedrateMax_theta").value = settingsData.feedrateMax_theta;
    }

    if (settingsData.feedrateDefault !== undefined) {
        document.getElementById("feedrateDefault").value = settingsData.feedrateDefault;
    }

    if (settingsData.rhoMax !== undefined) {
        document.getElementById("rhoMax").value = settingsData.rhoMax;
    }

    if (settingsData.maxStepover !== undefined) {
        document.getElementById("maxStepover").value = settingsData.maxStepover;
    }

    if (settingsData.ballSize !== undefined) {
        document.getElementById("ballSize").value = settingsData.ballSize;
    }

    if (settingsData.clearingStepover !== undefined) {
        document.getElementById("clearingStepover").value = settingsData.clearingStepover;
    }



    //Rho Gains
    if (settingsPID.kp_Rho !== undefined) {
        document.getElementById("kp-rho").value = settingsPID.kp_Rho;
    }

    if (settingsPID.ki_Rho !== undefined) {
        document.getElementById("ki-rho").value = settingsPID.ki_Rho;
    }

    if (settingsPID.kd_Rho !== undefined) {
        document.getElementById("kd-rho").value = settingsPID.kd_Rho;
    }

    //Theta  Gains
    if (settingsPID.kp_Theta !== undefined) {
        document.getElementById("kp-theta").value = settingsPID.kp_Theta;
    }

    if (settingsPID.ki_Theta !== undefined) {
        document.getElementById("ki-theta").value = settingsPID.ki_Theta;
    }

    if (settingsPID.kd_Theta !== undefined) {
        document.getElementById("kd-theta").value = settingsPID.kd_Theta;
    }


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

    window.reboot = function(command) {
        const proceed = confirm("⚠️ Warning: Do you wish to reboot the control system?");
        if (!proceed) return

        socket.emit("reboot");
    }


    if (settingsData.feedrateMax_rho !== undefined) {
        document.getElementById("feedrateMax_rho").value = settingsData.feedrateMax_rho;
    }

    if (settingsData.feedrateMax_theta !== undefined) {
        document.getElementById("feedrateMax_theta").value = settingsData.feedrateMax_theta;
    }

    if (settingsData.feedrateDefault !== undefined) {
        document.getElementById("feedrateDefault").value = settingsData.feedrateDefault;
    }

    if (settingsData.rhoMax !== undefined) {
        document.getElementById("rhoMax").value = settingsData.rhoMax;
    }

    if (settingsData.maxStepover !== undefined) {
        document.getElementById("maxStepover").value = settingsData.maxStepover;
    }

    if (settingsData.ballSize !== undefined) {
        document.getElementById("ballSize").value = settingsData.ballSize;
    }

    if (settingsData.clearingStepover !== undefined) {
        document.getElementById("clearingStepover").value = settingsData.clearingStepover;
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
