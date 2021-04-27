#!/usr/bin/env python

import os
import datetime 
import cv2
import yaml
import sys
import time
import threading
import logging
from pathlib import Path
import atexit
from enum import Enum

class LoggingType(Enum):
    INFO = 1
    ERROR = 2
    

def exit_handler():
    logging.info("Stopped")
    
def log(message, logging_type, config):
    if logging_type == LoggingType.INFO:
        logging.info("Camera: {camera}: {message}".format(camera=config["name"], message=message))
    elif logging_type == LoggingType.ERROR:
        logging.error("Camera: {camera}: {message}".format(camera=config["name"], message=message))

def retention(dirpath, config):
    paths = sorted(Path(dirpath).iterdir(), key=os.path.getmtime)
    for i in range(0, len(paths) - config["retention"]):
        log("Retention: removing {}".format(paths[i]), LoggingType.INFO, config)
        os.remove(paths[i])

def get_dates():
    source_datetime = datetime.datetime.now()
    eod = datetime.datetime(
        year=source_datetime.year,
        month=source_datetime.month,
        day=source_datetime.day
    ) + datetime.timedelta(days=1, microseconds=-1)
    return source_datetime, eod

def read_configuration():
    with open(sys.argv[1]) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

def str_to_datetime(str_datetime):
    return datetime.datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S.%f')

def start_streaming(config):
    connection_refused = False
    lost_frames = 0
    starting, eod = get_dates()
    directory = "{storage_path}/{name}/".format(storage_path=config["storage_path"], name=config["name"])

    if not os.path.exists(directory):
        os.makedirs(directory)
        
    file_name = '{storage_path}/{name}/{name}-{date}.avi'.format(storage_path=config["storage_path"], name=config["name"], date=str(starting).replace(":", "."))
    log("Started streaming: {}".format(file_name), LoggingType.INFO, config)
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    cap = cv2.VideoCapture("rtsp://{username}:{password}@{ip}:554/{stream_path}".format(username=config["username"], password=config["password"], ip=config["ip"], stream_path=config["stream_path"]))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(file_name,fourcc, fps, (1280,720))
    while True:
        retention(directory, config)
        starting, _ = get_dates()
        if(cap.isOpened()):
            if starting > eod or connection_refused:
                log("Finished {}".format(file_name), LoggingType.INFO, config)
                file_name = '{storage_path}/{name}/{name}-{date}.avi'.format(storage_path=config["storage_path"], name=config["name"], date=str(starting).replace(":", "."))
                out = cv2.VideoWriter(file_name,fourcc, fps, (1280,720))
                log("Started {}".format(file_name), LoggingType.INFO, config)
                _, eod = get_dates() 
            ret, frame = cap.read()
            connection_refused = False
            if ret == True:
                out.write(frame)
                lost_seconds = 0
                lost_frames = 0
            else:
                lost_frames += 1
                lost_seconds = int(lost_frames / fps)
                if lost_seconds > 5:
                    log("Found 5 seconds gap. Re-connecting to {ip}".format(ip=config["ip"]), LoggingType.ERROR, config)
                    cap = cv2.VideoCapture("rtsp://{username}:{password}@{ip}:554/{stream_path}".format(username=config["username"], password=config["password"], ip=config["ip"], stream_path=config["stream_path"]))
                    connection_refused = True
                #cv2.imshow(config["name"],frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
                #break
        else:
            log("Connection refused. Sleeping 5 seconds", LoggingType.ERROR, config)
            time.sleep(5)
            cap = cv2.VideoCapture("rtsp://{username}:{password}@{ip}:554/{stream_path}".format(username=config["username"], password=config["password"], ip=config["ip"], stream_path=config["stream_path"]))
            connection_refused = True

    cap.release()
    out.release()

def configure_logs(config):
    print("Starting logs at: {}".format(config["log_file"]))
    logging.basicConfig(filename=config["log_file"], format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)

def checks(config):
    for i in config:
        if not os.path.exists(i["storage_path"]):
            logging.error("Storage path missing. Exiting")
            exit(1)

def main():
    atexit.register(exit_handler)
    abstract_config = read_configuration()
    config = abstract_config["cameras"]
    configure_logs(abstract_config)
    checks(config)
    cameras = list()
    #start_streaming(config[0])
    for i in config:
        current_index = config.index(i)
        cameras.append(threading.Thread(target=start_streaming, args=(config[current_index],)))
        cameras[current_index].start()

if __name__ == "__main__":
   main()

