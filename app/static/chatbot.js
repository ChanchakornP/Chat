async function* readChunks(reader) {
    const decoder = new TextDecoder();
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield decoder.decode(value, { stream: true });
    }
}

async function* textStreaming(url, messageText) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: 'llama3',
            messages: [
                { role: 'user', content: messageText }
            ]
        })
    });

    const reader = response.body.getReader();
    for await (const chunk of readChunks(reader)) {
        yield chunk;
    }
}

