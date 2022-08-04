# threading
from threading import Thread

# mqtt 
import random
from paho.mqtt import client as mqtt_client
import json

# taking screenshot
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# for liveStreaming
import cv2
import numpy as np
import time
import subprocess as sp
import os
from datetime import datetime

# for liveStreaming backup in local storage

#from cv2 import VideoWri


# global variablef

flag = True
camera_url = "rtsp://192.168.29.254:2000/h264_pcm.sdp"  # camera hosted
http_cam = "http://192.168.29.254:2000/video"
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(width, height, fps)

ffmpeg_sub_process = None
browser_driver = None
match_id = 3316490
yt_stream_key = None
ticker_image = cv2.imread("ticker.png", cv2.IMREAD_UNCHANGED)
ticker_crop_size = 965
resized_ticker = ticker_image
#resized_ticker = cv2.resize(ticker_image, (width, height))
updated_ticker = resized_ticker[ticker_crop_size:height, 0:width, 0:3]
resolution = (width, height)
# fourcc = cv2.VideoWriter_fourcc('M', 'S', 'V', 'C')
#print(cv2.VideoWriter_fourcc(*'h264'))
# video_backup = cv2.VideoWriter('match_local_backup.avi', fourcc, fps, resolution)

print("start recording")

command_for_ffmpeg_to_send_stream_to_yt =  ['ffmpeg',
                                            '-f', 'rawvideo',
                                            '-pix_fmt', 'bgr24',
                                            '-s','{}x{}'.format(width, height),
                                            '-i','-',
                                            '-f', 'lavfi',
                                            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',                                                                             
                                            '-vcodec','libx264',
                                            '-preset', 'ultrafast',
                                            #'-qp', '0',
                                            '-b:v', '1200k',                                  
                                            '-pix_fmt','yuv420p',                                                                                                                                                                                              
                                            '-g', '60', # fps = 30
                                            '-acodec','aac',
                                            '-b:a','128k',
                                            '-f', 'flv', 
                                            'rtmp://a.rtmp.youtube.com/live2/{}'.format(yt_stream_key)
                                            ]

testing_command_for_ffmpeg_to_send_stream_to_yt =  ['ffmpeg',
                                                    '-f', 'rawvideo',
                                                    '-pix_fmt', 'bgr24',
                                                    '-s','{}x{}'.format(960, 720),
                                                    '-i','-',
                                                    '-f', 'lavfi',
                                                    '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',   
                                                    '-acodec','aac',
                                                    '-ab','128k',
                                                    # apply constant bitrate CBR
                                                    #'-b:v', '1000k', '-maxrate', '1000k', '-minrate', '1000k', '-bufsize', '1000k',
                                                    #'-strict','experimental',
                                                    '-vcodec','libx264',
                                                    '-pix_fmt','yuv420p',
                                                    #'-profile:v', 'baseline',
                                                    '-preset', 'ultrafast',
                                                    #'-r', '30',
                                                    '-g', '60',
                                                    '-b:v','1100k',
                                                    #'-threads', '4',
                                                    #'-qscale:3',
                                                    #'-buffsize', '512k',
                                                    '-f', 'flv', 
                                                    'rtmp://a.rtmp.youtube.com/live2/{}'.format("u17x-hecx-sqtj-fgfb-c6vg")
                                                    ]


ch_mqtt_broker = 'ajpqtrpkadas99.cricheroes.in'
ch_mqtt_port = 8883
ch_mqtt_topic = "tickerscore-3316490"
ch_startup_listner = "stream-info"
# generate client ID with pub prefix randomly
pi_client_id = f'python-mqtt-{random.randint(0, 1000)}'  # python literal string
username = 'Rishi_1'
password = 'password'


def live_streaming_to_yt():
    global ffmpeg_sub_process
    global command_for_ffmpeg_to_send_stream_to_yt
    global resized_ticker
    global cap
    global updated_ticker
    global testing_command_for_ffmpeg_to_send_stream_to_yt
    global flag
    global yt_stream_key
    #global video_backup
    
    testing_command = ['ffmpeg',
                   '-f', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s','{}x{}'.format(width, height),
                   '-i','-',
                   '-f', 'lavfi',
                   '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                   '-vcodec','libx264',
                   '-pix_fmt','yuv420p',
                   '-preset', 'ultrafast',
                   #'-qp', '0',
                   '-b:v', '5000k',                                  
                   
                   '-g', '60', # fps = 30
                   '-f', 'flv', 
                   'rtmp://a.rtmp.youtube.com/live2/{}'.format("u17x-hecx-sqtj-fgfb-c6vg")
                  ]
    
    h , w ,ch = updated_ticker.shape
    
    print("testing command : ", w, h, ch)
    print(testing_command_for_ffmpeg_to_send_stream_to_yt)
    
    ffmpeg_sub_process = sp.Popen(testing_command, stdin=sp.PIPE)
    
    print("live Streaming started", ffmpeg_sub_process)
    
    while True:
        _, result = cap.read()
        
        #result = overlay_png(result, resized_ticker, [0, 0])
        #result[0:50, 0:1280] = updated_ticker
        #result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        #result[:,:,1] = 0
        #result[:,:,2] = 0
        #cv2.imshow("Frame", result)
        result[965:height, 0:w] = updated_ticker

        # video_backup.write(result)
        #q = cv2.waitKey(1)
        #if q == ord("q"):
        #    break
        
        ffmpeg_sub_process.stdin.write(result.tobytes())
    
    video_backup.release()
    ffmpeg_sub_process.terminate()



# settings for browser to get ready for screenshot
def send(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    return driver.command_executor._request('POST', url, body)


def start_web_browser():
    global browser_driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("disable-infobars")
    browser_driver = webdriver.Chrome(chrome_options=chrome_options)
    browser_driver.get("https://cricheroes.in/live-video-scorecard-ios/{}".format(match_id))
    browser_driver.set_window_size(1920, 1080)
    send(browser_driver, "Emulation.setDefaultBackgroundColorOverride", {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}})
    print("chrome running in background")
        

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(pi_client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(ch_mqtt_broker, ch_mqtt_port) #connection made here 
    return client

def save_ticker_screenshot():
    global browser_driver
    global ticker_image
    global resized_ticker
    global updated_ticker
    global ticker_crop_size
    
    print(str(datetime.now()) + " message received")
            
    browser_driver.save_screenshot('ticker.png')
            
    print(str(datetime.now())  + " ticker saved")

    ticker_image = cv2.imread("ticker.png", cv2.IMREAD_UNCHANGED)
    resized_ticker = cv2.resize(ticker_image, (width, height))
    updated_ticker = resized_ticker[ticker_crop_size:height, 0:width, 0:3]
    

def set_credentials_for_livestream(stream_config):
    global ch_mqtt_topic
    global match_id
    global flag
    flag = True
    stream_key = stream_config['stream_key']
    match_id = stream_config['match_id']
    stream_fps = stream_config['stream_fps']
    stream_resolution = stream_config['stream_resolution']
    ch_mqtt_topic = "tickerscore-{}".format(match_id)
    

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg): 
        save_ticker_screenshot()
        print("overlay saved")

    def on_message2(client, userdata, msg):
        print("messaged recived form : ",msg.topic)
        
        # mqtt ticker/score listener
        if(msg.topic == ch_mqtt_topic):
            save_ticker_screenshot()
            print("overlay saved")
        
        # mqtt listener for 
        else:
            stream_config = json.loads(msg.payload.decode())
            
            # for ending stream 
            if(stream_config['isLive'] == False):
                global browser_driver
                global flag
                global ffmpeg_sub_process
                
                flag = False
                browser_driver.quit()
                ffmpeg_sub_process.terminate()
                print("Stream is going to end soon")
                client.disconnect()
                
            # for starting stream
            else:
                # setting credentials for starting live stram
                set_credentials_for_livestream(stream_config)
                print("stream credentials set")
                client.disconnect()
                
                #print("message recieved", json.loads(msg.payload.decode()))
                #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
                #print(stream_config)
    
    #if(match_id is None):
     #   client.subscribe(ch_startup_listner, 0)
     #   client.on_message = on_message
     #   print("subscribed to : ", ch_startup_listner)
    
    #else:
    #client.subscribe([(ch_startup_listner, 1), (ch_mqtt_topic, 1)])
    client.subscribe([(ch_mqtt_topic, 1)])
    client.on_message = on_message
    print("subscribed to topic : ", ch_mqtt_topic)


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

#run()

#print("this is what we do exited form loop forever")

#start_web_browser()
#live_streaming_to_yt()
#start_mqtt()

#ch_mqtt_thread = Thread(target=run)
ch_live_streaming_thread = Thread(target=live_streaming_to_yt)

#ch_mqtt_thread.start()
#time.sleep(2)
ch_live_streaming_thread.start()
print("mqtt stated")

#ch_mqtt_thread.join()
ch_live_streaming_thread.join()
#ffmpeg_sub_process.terminate()
#cv2.destroyAllWindows()
print("mqtt end")
