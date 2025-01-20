// Check if Speech Recognition is supported
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    alert("Browser Anda tidak mendukung Speech Recognition. Coba gunakan Google Chrome.");
} else {
    // Initialize SpeechRecognition
    const recognition = new SpeechRecognition();
    recognition.lang = "id-ID"; // Set language to Indonesian
    recognition.interimResults = false; // Only capture final results

    let isRecognizing = false;

    // Function to start or stop speech recognition
    function startSpeechRecognition() {
        if (isRecognizing) {
            recognition.stop(); // Stop recognition
            document.getElementById("voice-button").classList.remove("active"); // Remove animation
            console.log("Speech recognition stopped.");
        } else {
            recognition.start(); // Start recognition
            document.getElementById("voice-button").classList.add("active"); // Add animation or effect
            console.log("Speech recognition started...");
        }
        isRecognizing = !isRecognizing; // Toggle recognizing state
    }

    // Handle speech recognition result
    recognition.onresult = (event) => {
        const speechResult = event.results[0][0].transcript; // Get recognized speech
        document.getElementById("user-query").value = speechResult; // Set input field value
        sendMessage(); // Automatically send the query
    };

    // Handle speech recognition errors
    recognition.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        alert("Terjadi kesalahan saat mendengarkan. Silakan coba lagi.");
    };

    // When speech recognition ends
    recognition.onend = () => {
        document.getElementById("voice-button").classList.remove("active"); // Remove animation
        console.log("Speech recognition stopped.");
    };

    // Attach event listener to the voice button
    document.getElementById("voice-button").addEventListener("click", startSpeechRecognition);
}

// Function for Text-to-Speech with cancel option
let currentUtterance = null;

function textToSpeech(text) {
    const synth = window.speechSynthesis;

    if (!synth) {
        console.error("Speech Synthesis not supported in this browser.");
        return;
    }

    // If speech is already playing, cancel it
    if (currentUtterance && synth.speaking) {
        synth.cancel(); // Stop the current speech
        console.log("Speech canceled.");
        return;
    }

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = "id-ID"; // Set language to Indonesian
    synth.speak(currentUtterance);
    console.log("Speech started...");
}

// Function to send user query to the server
function sendMessage() {
    const userQuery = document.getElementById("user-query").value.trim();
    if (!userQuery) {
        alert("Mohon masukkan pertanyaan terlebih dahulu.");
        return;
    }

    const responseArea = document.getElementById("response-area");

    // Add user query to chat
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user-message");
    userMessage.textContent = userQuery;

    // Create and add the Text-to-Speech button to user message
    const userTtsButton = document.createElement("button");
    userTtsButton.classList.add("text-to-speech-button");
    userTtsButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3zm6-3a6 6 0 0 1-12 0H4a8 8 0 0 0 16 0h-2zm-6 8a5 5 0 0 0 5-5h2a7 7 0 0 1-14 0h2a5 5 0 0 0 5 5z"></path></svg>`;
    userTtsButton.addEventListener("click", () => textToSpeech(userQuery));
    userMessage.appendChild(userTtsButton);
    
    responseArea.appendChild(userMessage);

    // Send query to server
    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userQuery }),
    })
        .then(response => response.json())
        .then(data => {
            const botMessage = document.createElement("div");
            botMessage.classList.add("message", "bot-message");
            botMessage.textContent = data.answer;

            // Create and add the Text-to-Speech button to bot message
            const botTtsButton = document.createElement("button");
            botTtsButton.classList.add("text-to-speech-button");
            botTtsButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3zm6-3a6 6 0 0 1-12 0H4a8 8 0 0 0 16 0h-2zm-6 8a5 5 0 0 0 5-5h2a7 7 0 0 1-14 0h2a5 5 0 0 0 5 5z"></path></svg>`;
            botTtsButton.addEventListener("click", () => textToSpeech(data.answer));
            botMessage.appendChild(botTtsButton);

            responseArea.appendChild(botMessage);
            responseArea.scrollTop = responseArea.scrollHeight;

            document.getElementById("user-query").value = "";
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Terjadi kesalahan. Coba lagi.");
        });
}

// Function to display welcome message from the bot when page loads
window.onload = () => {
    const responseArea = document.getElementById("response-area");
    const welcomeMessage = document.createElement("div");
    welcomeMessage.classList.add("message", "bot-message");
    welcomeMessage.textContent = "Selamat datang di CornCare! Ada yang bisa saya bantu?";

    // Create and add the Text-to-Speech button to the welcome message
    const welcomeTtsButton = document.createElement("button");
    welcomeTtsButton.classList.add("text-to-speech-button");
    welcomeTtsButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3zm6-3a6 6 0 0 1-12 0H4a8 8 0 0 0 16 0h-2zm-6 8a5 5 0 0 0 5-5h2a7 7 0 0 1-14 0h2a5 5 0 0 0 5 5z"></path></svg>`;
    welcomeTtsButton.addEventListener("click", () => textToSpeech(welcomeMessage.textContent));
    welcomeMessage.appendChild(welcomeTtsButton);

    responseArea.appendChild(welcomeMessage);
    responseArea.scrollTop = responseArea.scrollHeight;  // Scroll to the bottom
};

// Add event listener for send button (if needed)
document.getElementById("send-button").addEventListener("click", sendMessage);
document.getElementById("user-query").addEventListener("keydown", event => {
    if (event.key === "Enter") sendMessage();
});

// Clear chat functionality
document.querySelector(".clear-chat").addEventListener("click", () => {
    const responseArea = document.getElementById("response-area");
    responseArea.innerHTML = ''; // Clears the chat area
    
    // Display the welcome message again
    const welcomeMessage = document.createElement("div");
    welcomeMessage.classList.add("message", "bot-message");
    welcomeMessage.textContent = "Selamat datang di CornCare! Ada yang bisa saya bantu?";

    // Create and add the Text-to-Speech button to the welcome message
    const welcomeTtsButton = document.createElement("button");
    welcomeTtsButton.classList.add("text-to-speech-button");
    welcomeTtsButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3zm6-3a6 6 0 0 1-12 0H4a8 8 0 0 0 16 0h-2zm-6 8a5 5 0 0 0 5-5h2a7 7 0 0 1-14 0h2a5 5 0 0 0 5 5z"></path></svg>`;
    welcomeTtsButton.addEventListener("click", () => textToSpeech(welcomeMessage.textContent));
    welcomeMessage.appendChild(welcomeTtsButton);

    responseArea.appendChild(welcomeMessage);
    responseArea.scrollTop = responseArea.scrollHeight;  // Scroll to the bottom
});
