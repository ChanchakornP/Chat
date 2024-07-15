function sendMessage() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const messageText = userInput.value;

    if (messageText.trim() === '') {
        return;
    }

    // Display the user's message
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = messageText;
    chatBox.appendChild(userMessage);

    // Clear the input field
    userInput.value = '';

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send the user's message to the Flask server for processing
    fetch(endpointChat, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chat_completion: messageText })
    })
        .then(response => response.json())
        .then(data => {
            // Display the processed response from the server
            const botResponse = data.response;

            // Create a new div for bot's message
            const botMessage = document.createElement('div');
            botMessage.className = 'message bot-message';

            // Split the bot's response by lines
            const lines = botResponse.split('\n');

            // Create a span element for each line and append to botMessage
            lines.forEach(line => {
                const lineElement = document.createElement('span');
                lineElement.textContent = line;
                botMessage.appendChild(lineElement);

                // Add a line break after each line (except the last one)
                if (lines.indexOf(line) !== lines.length - 1) {
                    botMessage.appendChild(document.createElement('br'));
                }
            });

            // Append the bot's message to the chat box
            chatBox.appendChild(botMessage);

            // Scroll to the bottom of the chat box after displaying bot's response
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}