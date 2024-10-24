document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userId = 1111; // Generate a unique user ID for the session

    function addMessage(content, className, image = null) {
    const message = document.createElement('div');
    message.classList.add('chat-message', className);

    if (image) {
        // If an image is provided, create an image element and append it
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${image}`; // Base64-encoded image data
        img.alt = "Generated Image";
        img.classList.add('generated-image');  // Optional class for styling
        message.appendChild(img);
    } else {
        // Otherwise, treat it as a text message
        message.textContent = content;
    }

    // Append the message (text or image) to the chat box
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the bottom
}

    function showLoadingDots() {
        const loadingDots = document.createElement('div');
        loadingDots.classList.add('loading-dots');
        loadingDots.innerHTML = '<span></span><span></span><span></span>';
        loadingDots.setAttribute('id', 'loading-dots');
        chatMessages.appendChild(loadingDots);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    function loadPreviousMessages() {
    fetch(`/load_messages/${userId}`)
        .then(response => response.json())
        .then(messages => {
            console.log("Messages received:", messages);
            if (messages.length === 0) {
                console.log("No previous messages found. Showing introductory messages.");
                showIntroMessages();
            } else {
                console.log("Previous messages found. Displaying them.");
                messages.forEach(msg => addMessage(msg.message, msg.sender));
            }
        })
        .catch(error => {
            console.error("Error loading previous messages:", error);
        });
    }

    function showIntroMessages() {

        setTimeout(function() {
            addBotMessageWithDelay('Hello! I’m an AI and my name is Ember, and I’m here to chat with you about your thoughts, dreams, and maybe even some worries about the future. Together, we can explore these ideas and turn them into visual art using AItools. After that, if you’re in South Carolina, I will submit your creation to the the South Carolina AI Highschool Art competition', 2000);
        }, 2000);

        setTimeout(function() {
            addBotMessageWithDelay('Let me tell you a bit about how I work. As an artificial intelligence, I process and learn from large amounts of data to simulate conversations like this one. My goal is to understand your thoughts and help express them creatively. AI can analyze patterns and make predictions, which is why I can chat with you about a wide range of topics.', 2000);
        }, 8000);

        setTimeout(function() {
            addBotMessageWithDelay('As we chat, I’ll be taking note of your answers to create a detailed prompt for an AI image generator. These generators use algorithms to transform text descriptions into images. They’ve been trained on millions of images to understand different styles and concepts, allowing them to create unique artwork based on the prompts I generate from our conversation.', 2000);
        }, 10000);

        setTimeout(function() {
            addBotMessageWithDelay('I want to assure you that your privacy is important. Our conversation will only be used to create the art prompts and will not be released to the public. Your responses won’t be stored longer than necessary to generate the image prompt.', 2000);
        }, 14000);

        setTimeout(function() {
            addBotMessageWithDelay('Ok, let\'s get started!', 2000);
        }, 16000);

        setTimeout(function() {
            addBotMessageWithDelay('What is your name', 2000);
        }, 18000);
    }
    let images = [];  // This will hold the image URLs
    let imageIndex = 0;  // Index to track the current image

    function sendMessageToServer(message) {
        showLoadingDots();  // Show loading dots before sending the message

        return fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, user_id: userId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.image) {
                // If the response contains an image (URL), display it
                addMessage("Here is the image generated from your answers:", 'bot');
                images = [data.image];  // Assume data.image is a single URL now
                imageIndex = 0;  // Reset index to show the first image
                displayImage();  // Function to show the image
            } else {
                // Otherwise, display the normal bot text response
                addMessage(data.response, 'bot');
            }
        })
        .finally(() => {
            hideLoadingDots();  // Hide loading dots after the message is processed
        });
    }

// Function to display the current image
    function displayImage() {
    if (images.length > 0) {
        const chatWindow = document.getElementById('chat-messages');

        const imageWrapper = document.createElement('div');
        imageWrapper.classList.add('chat-message', 'bot');

        const img = document.createElement('img');
        img.src = images[imageIndex];
        img.alt = 'Generated Image';


        img.style.width = '150%';  // Take up 100% of the available width
        img.style.maxWidth = '600px';  // Limit maximum width for larger screens
        img.style.height = 'auto';  // Let the height scale automatically to maintain aspect ratio
        img.style.aspectRatio = '16 / 9';  // Set the aspect ratio explicitly
        img.style.imageRendering = 'crisp-edges';
        img.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';

        imageWrapper.appendChild(img);
        chatWindow.appendChild(imageWrapper);

        // Scroll to the bottom of the chat to show the new message
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

    function hideLoadingDots() {
        const loadingDots = document.getElementById('loading-dots');
        if (loadingDots) {
            chatMessages.removeChild(loadingDots);
        }
    }

    function addBotMessageWithDelay(message, delay) {
        showLoadingDots();
        setTimeout(() => {
            hideLoadingDots();
            addMessage(message, 'bot');
        }, delay);
    }
    // Load previous messages
    loadPreviousMessages();

    document.getElementById('send-button').addEventListener('click', function() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (message !== '') {
            addMessage(message, 'user');

            sendMessageToServer(message).then(data => {
                addMessage(data.response, 'bot');
            });

            input.value = '';
        }
    });

    document.getElementById('chat-input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default action (e.g., new line in a text area)
            const input = document.getElementById('chat-input');
            const message = input.value.trim();

            if (message !== '') {
                addMessage(message, 'user');

                sendMessageToServer(message).then(data => {
                    addMessage(data.response, 'bot');
                });

                input.value = ''; // Clear the input field
            }
        }
    });
});
