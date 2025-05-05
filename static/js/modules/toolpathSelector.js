var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.getElementById("toolpath-dropdown");
    const imageBox = document.getElementById("toolpath-image");

    // Request toolpath list from server
    socket.emit("requestToolpathList");

    // Populate dropdown based on toolpath list
    socket.on("toolpathlist", function (data) {
        dropdown.innerHTML = '<option disabled selected>Select toolpath...</option>';

        data.forEach(filename => {
            const label = filename.replace(".TP", "").replace("_", " ");
            const option = document.createElement("option");

            option.value = `/toolpaths/${filename.replace(".TP", ".png")}`; // adjust if needed
            option.textContent = label;
            dropdown.appendChild(option);
        });
    });

    // Handle selection change to show corresponding image
    dropdown.addEventListener("change", () => {
        const selectedImage = dropdown.value;
        imageBox.src = selectedImage;
        imageBox.style.display = "block";

        socket.emit("newSelected_TP", dropdown.value)
    });
});
