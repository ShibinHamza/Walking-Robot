import sensor
import time
import network
import socket
import pyb

# UART setup
uart = pyb.UART(9, 115200)  # Initialize UART at 115200 baud rate

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
    # This function will handle button presses and send data over UART
    if button_id == "button1":
        print("Button 1 pressed \n");
        uart.write("Button 1 pressed\n")
    elif button_id == "button2":
        print("Button 2 pressed \n");
        uart.write("Button 2 pressed\n")
    elif button_id == "button3":
        print("Button 3 pressed \n");
        uart.write("Button 3 pressed\n")
    elif button_id == "button4":
        print("Button 4 pressed \n");
        uart.write("Button 4 pressed\n")

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
        "<img src='/stream' width='320' height='240' />"
        "<div class='container'>"
        "<h2>Motor Controls</h2>"
        "<div class='button-container'>"
        "<button onclick=\"sendRequest('button1')\">Button 1</button>"
        "<button onclick=\"sendRequest('button2')\">Button 2</button>"
        "<button onclick=\"sendRequest('button3')\">Button 3</button>"
        "<button onclick=\"sendRequest('button4')\">Button 4</button>"
        "</div></div>"
        "<script>"
        "function sendRequest(buttonId) {"
        "fetch('/' + buttonId)"
        ".then(response => console.log(buttonId + ' pressed'))"
        ".catch(error => console.error('Error:', error));"
        "}"
        "</script>"
        "</body></html>\r\n"
    )
    client.send(html)

def start_streaming(client):
    # FPS clock
    clock = time.clock()

    # Send multipart header if streaming
    client.send(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    while True:
        clock.tick()
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

        # Non-blocking check for button press requests
        try:
            client.settimeout(0)
            data = client.recv(1024).decode('utf-8')
            if "GET /button1" in data:
                handle_button_press("button1")
            elif "GET /button2" in data:
                handle_button_press("button2")
            elif "GET /button3" in data:
                handle_button_press("button3")
            elif "GET /button4" in data:
                handle_button_press("button4")
        except OSError:
            pass  # Ignore socket errors

    client.close()

server = None

while True:
    if server is None:
        # Create server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # Bind and listen
        server.bind([HOST, PORT])
        server.listen(5)
        print("Server started. Waiting for connections...")

    try:
        client, addr = server.accept()
        print("Connected to " + addr[0] + ":" + str(addr[1]))

        # Read initial request
        data = client.recv(1024).decode('utf-8')
        if "GET / " in data or "GET /HTTP" in data:
            serve_html(client)
        else:   #lif "GET /stream" in data:
            start_streaming(client)
#        else:
#            if "GET /button" in data:
#                if "GET /button1" in data:
#                    handle_button_press("button1")
#                elif "GET /button2" in data:
#                    handle_button_press("button2")
#                elif "GET /button3" in data:
#                    handle_button_press("button3")
#                elif "GET /button4" in data:
#                    handle_button_press("button4")

#            client.close()
    except OSError as e:
        client.close()
        print("client socket error:", e)
