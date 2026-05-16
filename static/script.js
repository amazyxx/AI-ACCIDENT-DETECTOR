const logBox = document.getElementById('logs');
const statusBadge = document.querySelector('.status-badge');

// 🔹 Connect to the FastAPI WebSocket
const socket = new WebSocket("ws://localhost:8000/ws");

function addLog(msg, isAlert = false) {
    const entry = document.createElement('div');
    entry.className = isAlert ? 'log-entry log-alert' : 'log-entry';
    const time = new Date().toLocaleTimeString();
    entry.innerText = `[${time}] ${msg}`;
    logBox.appendChild(entry);
    logBox.scrollTop = logBox.scrollHeight;
}

socket.onmessage = function(event) {
    if (event.data === "ACCIDENT_DETECTED") {
        addLog("🚨 CRITICAL: ACCIDENT DETECTED", true);
        
        // Visual feedback on the dashboard
        statusBadge.innerText = "STATUS: ACCIDENT";
        statusBadge.style.background = "rgba(239, 68, 68, 0.2)";
        statusBadge.style.color = "#ef4444";
        statusBadge.style.borderColor = "#ef4444";

        // Reset status after 3 seconds
        setTimeout(() => {
            statusBadge.innerText = "System: Active";
            statusBadge.className = "status-badge status-ready";
            statusBadge.style = ""; // Clear custom styles
        }, 3000);
    }
};

socket.onopen = () => addLog("WebSocket Connection Established.");
socket.onclose = () => addLog("WebSocket Connection Lost.", true);

// Slider Control Setup
const slider = document.getElementById('confSlider');
const output = document.getElementById('confValue');

slider.oninput = function() {
    let val = (this.value / 100).toFixed(2);
    output.innerHTML = val;
    
    // This hits the FastAPI route we need to create in main.py
    fetch(`/set_confidence?value=${val}`)
        .then(response => response.json())
        .then(data => console.log("Confidence updated:", data.value))
        .catch(err => console.error("Error updating confidence:", err));
}