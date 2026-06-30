document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("digit-canvas");
    const ctx = canvas.getContext("2d");
    const clearBtn = document.getElementById("clear-btn");
    const predictBtn = document.getElementById("predict-btn");
    const loader = document.getElementById("canvas-loader");
    const digitOut = document.getElementById("pred-digit");
    const percentOut = document.getElementById("pred-percent");
    const barFill = document.getElementById("progress-bar-fill");

    let isDrawing = false;
    
    // Set modern stroke details
    ctx.lineWidth = 14;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#111827"; // Dark charcoal stroke

    // Initialize clean white canvas
    clearCanvas();

    function clearCanvas() {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Reset prediction elements
        digitOut.textContent = "—";
        digitOut.style.transform = "scale(1)";
        percentOut.textContent = "—";
        barFill.style.width = "0%";
    }

    // Capture stroke coordinates
    function getCoordinates(e) {
        let clientX, clientY;
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX;
            clientY = e.clientY;
        }

        const rect = canvas.getBoundingClientRect();
        // Handle resizing/scaling of bounding clients
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        return {
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY
        };
    }

    function startDrawing(e) {
        isDrawing = true;
        const coords = getCoordinates(e);
        ctx.beginPath();
        ctx.moveTo(coords.x, coords.y);
    }

    function draw(e) {
        if (!isDrawing) return;
        const coords = getCoordinates(e);
        ctx.lineTo(coords.x, coords.y);
        ctx.stroke();
    }

    function stopDrawing() {
        isDrawing = false;
        ctx.beginPath();
    }

    // Mouse drawing event listeners
    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseleave", stopDrawing);

    // Mobile/touch drawing support
    canvas.addEventListener("touchstart", (e) => {
        e.preventDefault();
        startDrawing(e);
    });
    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        draw(e);
    });
    canvas.addEventListener("touchend", (e) => {
        e.preventDefault();
        stopDrawing();
    });

    clearBtn.addEventListener("click", clearCanvas);

    // Predict event trigger
    predictBtn.addEventListener("click", () => {
        // Toggle visual loading indicator
        loader.classList.add("active");

        const base64Image = canvas.toDataURL("image/png");

        fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ image: base64Image })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || "HTTP error " + response.status);
                }).catch(() => {
                    throw new Error("HTTP error " + response.status);
                });
            }
            return response.json();
        })
        .then(data => {
            loader.classList.remove("active");
            if (data.prediction !== undefined) {
                // Animate predicted digit scaling/fade
                digitOut.style.transform = "scale(0.8)";
                setTimeout(() => {
                    digitOut.textContent = data.prediction;
                    digitOut.style.transform = "scale(1.1)";
                    setTimeout(() => {
                        digitOut.style.transform = "scale(1)";
                    }, 100);
                }, 100);

                // Animate percent count
                const targetConfidence = Math.round(data.confidence * 1000) / 10;
                animateConfidence(targetConfidence);

            } else if (data.error) {
                digitOut.textContent = "?";
                percentOut.textContent = data.error;
                console.error("Classifier error:", data.error);
            }
        })
        .catch(error => {
            loader.classList.remove("active");
            digitOut.textContent = "?";
            percentOut.textContent = error.message || "Error";
            console.error("Fetch request error:", error);
        });
    });

    // Animate the confidence percent number reveal and fill the progress bar
    function animateConfidence(targetVal) {
        let currentVal = 0;
        const duration = 500; // ms
        const steps = 30;
        const stepTime = duration / steps;
        const increment = targetVal / steps;

        const interval = setInterval(() => {
            currentVal += increment;
            if (currentVal >= targetVal) {
                percentOut.textContent = `${targetVal.toFixed(1)}%`;
                barFill.style.width = `${targetVal}%`;
                clearInterval(interval);
            } else {
                percentOut.textContent = `${currentVal.toFixed(1)}%`;
                barFill.style.width = `${currentVal}%`;
            }
        }, stepTime);
    }
});
