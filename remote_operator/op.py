import json
import socket
import subprocess
import sys
import time
import threading
import keyboard
import pygame
import os

# ============ USER CONFIG ============
PI_IP = "192.168.50.204"    # Your Pi's IP on IC2026 network
PI_PORT = 5005

AUTO_LAUNCH_GSTREAMER = True
GST_RECEIVER_CMD = (
    'gst-launch-1.0 -v udpsrc port=5600 caps='
    '"application/x-rtp,media=video,encoding-name=H264,payload=96,clock-rate=90000,packetization-mode=1" '
    '! rtpjitterbuffer latency=50 ! rtph264depay ! h264parse ! d3d11h264dec ! autovideosink sync=false'
)
GST_RECEIVER_CMD_AVD = (
    'gst-launch-1.0 -v udpsrc port=5600 caps="'
    'application/x-rtp,media=video,encoding-name=H264,payload=96,clock-rate=90000,packetization-mode=1" '
    '! rtpjitterbuffer latency=50 ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false'
)

SEND_HZ = 30

### Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UPD/datagram socket
addr = (PI_IP, PI_PORT)
### Video Stream
def open_stream():
    global gst_proc

    if AUTO_LAUNCH_GSTREAMER:
        try:
            gst_proc = subprocess.Popen(GST_RECEIVER_CMD, shell=True) # run the command we wrote in the shell
            print("[Video] GStreamer started")
        except Exception as e:
            print(f"[Video] Failed: {e}")
### Clean Up
def cleanup():
    if gst_proc and gst_proc.poll() is None:
        gst_proc.terminate() # terminate the subprocess

    sock.close() # stop the socket from running

input_thread = None
### Input Loop
def input_loop():
    vx = 0
    vy = 0
    if keyboard.is_pressed("w"):
        vy = 1
    elif keyboard.is_pressed("s"):
        vy = 1

    if keyboard.is_pressed("a"):
        vx += 1
    if keyboard.is_pressed("d"):
        vx -= 1

    rot = 0
    if keyboard.is_pressed("right"):
        rot = 1
    elif keyboard.is_pressed("left"):
        rot = -1
    payload = {
        "vx": float(vx),
        "vy": float(vy),
        "rot": float(rot)
        }
    input_thread = threading.Thread(target=input_loop, daemon=True)

#input_thread = threading.Thread(target=input_loop, daemon=True)
### Main Loop
def main():
    ### Open Stream
    open_stream()

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    ### Start Input Thread
    input_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ### Start Cleanup
                cleanup()
                running = False
                pygame.quit()
            screen.fill("black")

            pygame.display.flip()
        clock.tick(SEND_HZ)
        
if __name__ == "__main__":
    main()