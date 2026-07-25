import httpx

STREAM_URL = "http://127.0.0.1:8000/stream"


def main():
    payload = {
        "prompt": "Write a 4 sentence explanation of why streaming improves chat UX."
    }

    # stream() keeps the HTTP response open so we can print chunks as they arrive.
    with httpx.stream("POST", STREAM_URL, json=payload, timeout=60) as response:
        response.raise_for_status()

        print("Streaming from server:")
        for line in response.iter_lines():
            if not line:
                continue

            # The server sends SSE lines: data chunks plus a final done event.
            if line.startswith("data: "):
                print(line.removeprefix("data: "), end="", flush=True)
            elif line.startswith("event: done"):
                print()
        print()


if __name__ == "__main__":
    main()
