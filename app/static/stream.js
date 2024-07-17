// test function
async function* readChunks(reader) {
    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            break;
        }
        yield value;
    }
}

async function* textStreaming(url) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Context-Type': 'application/json',
        },
        body: JSON.stringify({
            model: 'llama3',
            messages: [
                { role: 'user', context: 'why is the sky blue?' }
            ]
        })
    });
    const reader = response.body.getReader()
    const decoder = new TextDecoder();
    for await (const chunk of readChunks(reader)) {
        const text = decoder.decode(chunk, { stream: true });
        yield text;
    }
}

async function callTextStreaming(url) {
    const stream = textStreaming(url);

    for await (const text of stream) {
        console.log(text); // You can replace this with any other processing logic
    }

}

callTextStreaming('http://localhost:11434/api/chat')