import json

import websocket


def on_message(ws, message):
    print(f"Received: {message}")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("Closed")


def on_open(ws):
    print("Connected")
    ws.send(json.dumps({"message": "Test WebSocket Connection"}))


url = "ws://localhost/ws/notifications/"
ws = websocket.WebSocketApp(
    url, on_message=on_message, on_error=on_error, on_close=on_close
)
ws.on_open = on_open
ws.run_forever()
