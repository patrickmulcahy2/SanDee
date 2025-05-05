document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    // === Initialize Charts ===
    function createImpulseChart(ctx, labelSuffix, opacity) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: `Rho Position${labelSuffix}`,
                        borderColor: `rgba(0, 255, 174, ${opacity})`,
                        backgroundColor: `rgba(0, 255, 174, ${opacity * 0.15})`,
                        data: [],
                        fill: false,
                    },
                    {
                        label: `Theta Position${labelSuffix}`,
                        borderColor: `rgba(100, 149, 237, ${opacity})`,
                        backgroundColor: `rgba(100, 149, 237, ${opacity * 0.15})`,
                        data: [],
                        fill: false,
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Time (s)' } },
                    y: { title: { display: true, text: 'Position (°/")' } }
                }
            }
        });
    }

    const currentImpulseChart = createImpulseChart(
        document.getElementById('currentImpulseChart').getContext('2d'),
        '',
        0.7
    );

    const lastImpulseChart = createImpulseChart(
        document.getElementById('lastImpulseChart').getContext('2d'),
        ' (Last)',
        0.4
    );

    // === Update Charts with Received Data ===
    socket.on('plotData', data => {
        // Update charts
        currentImpulseChart.data.labels = data.timeData.map(t => t.toFixed(2));
        currentImpulseChart.data.datasets[0].data = data.rhoPosition;
        currentImpulseChart.data.datasets[1].data = data.thetaPosition;
        currentImpulseChart.update();

        lastImpulseChart.data.labels = data.timeData_last.map(t => t.toFixed(2));
        lastImpulseChart.data.datasets[0].data = data.rhoPosition_last;
        lastImpulseChart.data.datasets[1].data = data.thetaPosition_last;
        lastImpulseChart.update();


        // Update parameter table values
        document.getElementById('currentRiseTime').textContent = data.riseTime.current.toFixed(2);
        document.getElementById('lastRiseTime').textContent = data.riseTime.last.toFixed(2);

        document.getElementById('currentSettlingTime').textContent = data.settlingTime.current.toFixed(2);
        document.getElementById('lastSettlingTime').textContent = data.settlingTime.last.toFixed(2);

        document.getElementById('currentOvershoot').textContent = data.overshoot.current.toFixed(2) + '%';
        document.getElementById('lastOvershoot').textContent = data.overshoot.last.toFixed(2) + '%';

        document.getElementById('currentPeak').textContent = data.peak.current.toFixed(2);
        document.getElementById('lastPeak').textContent = data.peak.last.toFixed(2);
    });


    // === Provide Impulse Button Logic ===
    document.getElementById('impulseButton').addEventListener('click', () => {
        const axis = document.getElementById('modeSelect').value;
        const startPoint = parseFloat(document.getElementById('startPos').value);
        const moveMagnitude = parseFloat(document.getElementById('impulseMag').value);
        const recordLength = parseFloat(document.getElementById('recordLength').value);

        if (!isNaN(startPoint) && !isNaN(moveMagnitude)) {
            socket.emit('check_tune', { axis, startPoint, moveMagnitude, recordLength });
        } else {
            alert("Please enter valid numbers for Starting Position and Impulse Magnitude.");
        }
    });

    document.getElementById("zieglerNicholsButton").addEventListener("click", function() {
        const axis = document.getElementById('modeSelect').value;
        const startPoint = parseFloat(document.getElementById('startPos').value);
        const moveMagnitude = parseFloat(document.getElementById('impulseMag').value);
        const recordLength = parseFloat(document.getElementById('recordLength').value);

        if (!isNaN(startPoint) && !isNaN(moveMagnitude)) {
            socket.emit('zieglerNichols', { axis, startPoint, moveMagnitude, recordLength });
        } else {
            alert("Please enter valid numbers for Starting Position and Impulse Magnitude.");
        }

    });

    // === Setup Sliders & Value Boxes ===
    const sliders = [
        { id: 'thetaKp', setting: 'kp_Theta' },
        { id: 'thetaKi', setting: 'ki_Theta' },
        { id: 'thetaKd', setting: 'kd_Theta' },
        { id: 'rhoKp', setting: 'kp_Rho' },
        { id: 'rhoKi', setting: 'ki_Rho' },
        { id: 'rhoKd', setting: 'kd_Rho' }
    ];

    sliders.forEach(({ id, setting }) => {
        const slider = document.getElementById(id);
        const valueBox = document.getElementById(id + "Value");

        if (slider && valueBox) {
            valueBox.textContent = slider.value;
            slider.addEventListener('input', () => {
                valueBox.textContent = slider.value;
                socket.emit('update_pid', { setting, value: parseFloat(slider.value) });
            });
        }
    });


    document.getElementById("disableMotorsButton").addEventListener("click", () => {
            socket.emit("disable_motors");
        });

    document.getElementById("enableMotorsButton").addEventListener("click", () => {
            socket.emit("enable_motors");
        });

    socket.on('updatePID-gains', data => {
        const pidSettings = data.settingsPID;

        sliders.forEach(({ id, setting }) => {
            const slider = document.getElementById(id);
            const valueBox = document.getElementById(id + "Value");

            if (slider && valueBox && pidSettings.hasOwnProperty(setting)) {
                const value = pidSettings[setting];
                slider.value = value;
                valueBox.textContent = value.toFixed(3);
            }
        });
    });

});
