import sensor
import time
import network
import socket
from machine import UART

# UART setup
uart = UART(9, 115200)  # Initialize UART at 115200 baud rate

SSID = "Shibin_Nicla"  # Network SSID
KEY = "1234567890"  # Network key (must be 10 chars)
HOST = ""  # Use first available interface
PORT = 8080  # Arbitrary non-privileged port

# Reset sensor
sensor.reset()
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

# Init wlan module in AP mode.
wlan = network.WLAN(network.AP_IF)
wlan.config(ssid=SSID, key=KEY, channel=2)
wlan.active(True)

print("AP mode started. SSID: {} IP: {}".format(SSID, wlan.ifconfig()[0]))

def handle_button_press(button_id):
    if button_id == "button1":
        print("Button 1 pressed \n")
        uart.write("Forward\n")
    elif button_id == "button2":
        print("Button 2 pressed \n")
        uart.write("Reverse\n")
    elif button_id == "button3":
        print("Button 3 pressed \n")
        uart.write("Left\n")
    elif button_id == "button4":
        print("Button 4 pressed \n")
        uart.write("Right\n")
    elif button_id == "button5":
        print("Button 5 pressed \n")
        uart.write("Stop\n")

def serve_html(client):
    html = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n\r\n"
        "<html><head><title>OpenMV MJPEG Streaming</title>"
        "<style>"
        "body { font-family: Arial, sans-serif; text-align: center; }"
        "h1 { color: #333; }"
        ".container { display: flex; justify-content: center; align-items: center; flex-direction: column; }"
        ".button-container { display: flex; justify-content: space-around; width: 60%; }"
        "button { padding: 10px 20px; margin: 10px; font-size: 16px; cursor: pointer; }"
        "</style>"
        "</head>"
        "<body><h1>MJPEG Stream</h1>"
        "<img id='videoStream' src='/stream' width='480' height='720' />"
        "<div class='container'>"
        "<h2>Motor Controls</h2>"
        "<div class='button-container'>"
        "<button onclick=\"sendRequest('button1')\">Forward</button>"
        "<button onclick=\"sendRequest('button2')\">Reverse</button>"
        "<button onclick=\"sendRequest('button3')\">Left</button>"
        "<button onclick=\"sendRequest('button4')\">Right</button>"
        "<button onclick=\"sendRequest('button5')\">Stop</button>"
        "</div></div>"
        "<script>"
        "function sendRequest(buttonId) {"
        "fetch('/' + buttonId, { method: 'POST' })"
        ".then(response => console.log(buttonId + ' pressed'))"
        ".catch(error => console.error('Error:', error));"
        "}"
        "function refreshImage() {"
        "const image = document.getElementById('videoStream');"
        "image.src = '/stream?' + new Date().getTime();"
        "}"
        "setInterval(refreshImage, 1);"
        "</script>"
        "</body></html>\r\n"
    )
    client.send(html)
    client.close()

def start_streaming(client, server):
    clock = time.clock()
    client.send(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    while True:
        clock.tick()
        print(clock)
        frame = sensor.snapshot()
        cframe = frame.to_jpeg(quality=35, copy=True)
        header = (
            "\r\n--openmv\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
        )

        try:
            client.sendall(header)
            client.sendall(cframe)
        except OSError:
            break  # Exit the loop if the client disconnects

        # Time-slice: check for new connections or commands
        server.settimeout(0.01)  # Brief timeout to prevent blocking
        try:
            new_client, addr = server.accept()
            # If a new client connects, break the loop to handle the new client
            client.close()
            handle_client(new_client, server)
            time.sleep(1)
            continue
        except OSError:
            pass  # No new connection, continue streaming

def handle_client(client, server):
    try:
        data = client.recv(1024)
        if "GET / " in data or "GET /HTTP" in data:
            serve_html(client)
        elif "POST /" in data:
            if "POST /button1" in data:
                handle_button_press("button1")
            elif "POST /button2" in data:
                handle_button_press("button2")
            elif "POST /button3" in data:
                handle_button_press("button3")
            elif "POST /button4" in data:
                handle_button_press("button4")
            elif "POST /button5" in data:
                handle_button_press("button5")
            client.close()
        else:  # elif "GET /stream" in data:
            start_streaming(client, server)
    except OSError as e:
        client.close()
        print("Client socket error:", e)

server = None

while True:
    if server is None:
        # Create server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        server.bind([HOST, PORT])
        server.listen(5)
        print("Server started. Waiting for connections...")

    try:
        client, addr = server.accept()
        print("Connected to " + addr[0] + ":" + str(addr[1]))
        handle_client(client, server)
    except OSError as e:
        server.close()
        server = None
        print("Server socket error:", e)
