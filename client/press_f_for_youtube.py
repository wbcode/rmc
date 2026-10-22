#!/usr/bin/env python3
import json
import sys
import urllib.request
from websocket import create_connection


def trigger_fullscreen():
    try:
        # 1. Fetch active targets from Chrome's Remote Debugging Port
        response = urllib.request.urlopen("http://127.0.0.1:9222/json")
        targets = json.loads(response.read().decode("utf-8"))

        if not targets:
            print("Error: No active Chrome targets found on port 9222.")
            sys.exit(1)

        # 2. Extract the WebSocket debugger URL for the active YouTube tab
        ws_url = targets[0]["webSocketDebuggerUrl"]

        # 3. Connect to Chrome via WebSocket
        ws = create_connection(ws_url)

        # 4. Construct the DevTools Protocol command for the 'f' key press
        key_event = {
            "id": 1,
            "method": "Input.dispatchKeyEvent",
            "params": {
                "type": "keyDown",
                "text": "f",
                "unmodifiedText": "f",
                "code": "KeyF",
                "key": "f",
                "windowsVirtualKeyCode": 70,
            },
        }

        # 5. Send event and close connection
        ws.send(json.dumps(key_event))
        ws.close()
        print("Successfully injected 'f' keystroke via CDP.")

    except Exception as e:
        print(f"Failed to send CDP command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    trigger_fullscreen()
