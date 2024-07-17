import json
import os

import requests

url = os.getenv("ENDPOINT_LLAMA3", "http://localhost:11434/api/chat")


def llama3(prompt):
    data = {
        "model": "llama3",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,  # Set stream to True for streaming output
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=data, stream=True)

    # Check if the response was successful
    if response.status_code == 200:
        # Process each chunk of data received from the server
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                # Assuming the response is JSON format, extract content from chunks
                content = chunk.decode("utf-8")
                message = json.loads(content)["message"]["content"]
                print(
                    message, end=""
                )  # Output or process each chunk of the streamed response
    else:
        print(f"Error: {response.status_code}")


# Example usage
prompt = "Why is the sky blue?"
llama3(prompt)
