const startBtn = document.getElementById("startBtn");
const simulateBtn = document.getElementById("simulateBtn");
const video = document.getElementById("video");
const statusBox = document.getElementById("status");

// TODO: 1. Go to https://teachablemachine.withgoogle.com/train/image
//       2. Train a model with two classes: "Helmet" and "No Helmet"
//       3. Click "Export Model" -> "Upload" -> Copy the URL
//       4. Paste the URL below:
const URL = "https://teachablemachine.withgoogle.com/models/YOUR_MODEL_ID/";

let model, maxPredictions;
let isDetecting = false;

startBtn.addEventListener("click", initSystem);
simulateBtn.addEventListener("click", simulateDetection);

async function initSystem() {
    statusBox.innerHTML = "Loading Model... Please wait.";
    
    try {
        // 1. Load the model
        const modelURL = URL + "model.json";
        const metadataURL = URL + "metadata.json";
        
        // Load the model using the global tmImage variable from the HTML script tag
        model = await tmImage.load(modelURL, metadataURL);
        maxPredictions = model.getTotalClasses();

        // 2. Start the Camera
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        
        // 3. Start Prediction Loop when video is ready
        video.onloadedmetadata = () => {
            isDetecting = true;
            predictLoop();
        };
    } catch (error) {
        statusBox.innerHTML = "Error: Check Model URL in scripthel.js";
        statusBox.className = "status danger";
        console.error("Initialization failed:", error);
        alert("Failed to load. Did you paste your Teachable Machine URL in scripthel.js?");
    }
}

async function predictLoop() {
    if (!isDetecting) return;

    // Predict the frame
    const prediction = await model.predict(video);

    // Check for "Helmet" class probability
    // We assume you named your classes "Helmet" and "No Helmet"
    const helmetClass = prediction.find(p => p.className.toLowerCase() === "helmet");
    const noHelmetClass = prediction.find(p => p.className.toLowerCase() === "no helmet");

    // Logic: If Helmet probability is higher than No Helmet
    if (helmetClass && noHelmetClass) {
        if (helmetClass.probability > 0.8) {
            statusBox.className = "status safe";
            statusBox.innerHTML = `Helmet Detected ✔ (${(helmetClass.probability * 100).toFixed(0)}%)`;
        } else {
            statusBox.className = "status danger";
            statusBox.innerHTML = "No Helmet ❌";
        }
    } else {
        // Fallback if class names don't match exactly, just use the first class as Helmet
        if (prediction[0].probability > 0.5) {
             statusBox.className = "status safe";
             statusBox.innerHTML = "Class 1 Detected (Helmet?)";
        } else {
             statusBox.className = "status danger";
             statusBox.innerHTML = "Class 2 Detected (No Helmet?)";
        }
    }

    // Run again on next frame
    requestAnimationFrame(predictLoop);
}

// Keep simulation for testing without camera/model
function simulateDetection() {
    const random = Math.random();

    if (random > 0.5) {
        statusBox.className = "status safe";
        statusBox.innerHTML = "Helmet Detected ✔";
    } else {
        statusBox.className = "status danger";
        statusBox.innerHTML = "No Helmet ❌";
    }
}
