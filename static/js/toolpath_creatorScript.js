var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

document.addEventListener("DOMContentLoaded", function () {

    document.getElementById("delete-toolpath").addEventListener("click", () => {
        const dropdown = document.getElementById("toolpath-dropdown");
        const selected = dropdown.value;

        if (selected) {
            // Show the confirmation prompt
            const confirmDelete = window.confirm(`Are you sure you want to delete ${selected}?`);

            if (confirmDelete) {
                // User confirmed, emit the delete request
                console.log(`User confirmed deletion of: ${selected}`);
                socket.emit("delete_file", selected);
            } else {
                // User canceled the deletion
                console.log(`User canceled deletion of: ${selected}`);
            }
        } else {
            console.log("No toolpath selected.");
        }
    });

    socket.on("file_deleted", (filename) => {
        socket.emit("requestToolpathList");
        
        // After deleting the file, clear the image preview
        const toolpathImage = document.getElementById("toolpath-image");
        if (toolpathImage.src.includes(filename)) {
            toolpathImage.style.display = "none"; // Hide the image
            toolpathImage.src = ""; // Clear the image source
        }
    });

    socket.emit("request_path");


    function setupToggleBox(id) {
        const box = document.getElementById(id);
        const states = ["Origin", "Edge", "N/A"];

        box.textContent = "Origin";
        box.classList.add("active");
        box.classList.remove("na");

        box.addEventListener('click', () => {
            const current = box.textContent.trim();
            const currentIndex = states.indexOf(current);
            const nextIndex = (currentIndex + 1) % states.length;
            const newValue = states[nextIndex];

            socket.emit("snap_path", newValue, id)

            box.textContent = newValue;

            box.classList.remove("active", "na");
            if (newValue === "Origin" || newValue === "Edge") {
                box.classList.add("active");
            }
            if (newValue === "N/A") {
                box.classList.add("na");
            }

            console.log(`${id} toggled to`, newValue);

            // Example emit if needed
            // socket.emit("toggleRho", { id, value: newValue });
        });
    }
    setupToggleBox("rho-start-toggle");
    setupToggleBox("rho-end-toggle");

    //Modifier listeners
    const multiplyInput = document.getElementById("multiply-input");
    multiplyInput.addEventListener("input", () => {
        const value = parseInt(multiplyInput.value, 10);
        if (!isNaN(value)) {
            socket.emit("pattern_path", value);
            console.log("Multiply value emitted:", value);
        }
    });

    const smoothingSlider = document.getElementById("smoothing-slider");
    smoothingSlider.addEventListener("input", () => {
        const value = parseInt(smoothingSlider.value, 10);
        socket.emit("smooth_path", value);
        console.log("Smoothing value emitted:", value);
    });

    document.querySelector("#save-canvas").addEventListener("click", () => {
        const filename = prompt("Enter a filename to save the path:");
        if (filename && filename.trim() !== "") {
            socket.emit("save_path", filename);
            console.log("Saved filename:", filename.trim());
            socket.emit("requestToolpathList");
        } else {
            console.log("Save canceled or empty filename.");
        }
    });

    function setupMirrorToggle(id, eventName) {
        const box = document.getElementById(id);
        let isActive = false;

        box.addEventListener('click', () => {
            isActive = !isActive;
            box.classList.toggle("active", isActive);
            box.textContent = isActive ? "On" : "Off";
            socket.emit(eventName, isActive);
            console.log(`${id} toggled:`, isActive);
        });
    }
    setupMirrorToggle("mirror-x", "mirror_x");
    setupMirrorToggle("mirror-y", "mirror_y");

});
