# rtsp.camera.recorder
A python project to record your IP camera through the rtsp protocol

## Config values

```yml
log_file: `specify the log file you wish to keep the logs`
cameras:
  - name: `specify a name of your choice`
    ip: `the IP of your camera`
    username: `username to authenticate to the camera`
    password: `password to authenticate to the camera`
    stream_path: `specify the path in which the camera provides the stream through the rtsp protocol`
    storage_path: `specify the path in which you wish to store your daily recordings`
    retention: `max_number of the recordings in the storage_path`
  - name: `specify a name of your second device`
    ip: `the IP of your second camera`
    username: `username to authenticate to the camera`
    password: `password to authenticate to the camera`
    stream_path: `specify the path in which the camera provides the stream through the rtsp protocol`
    storage_path: `specify the path in which you wish to store your daily recordings`
    retention: `max_number of the recordings in the storage_path`
```

> **Notes:**

* You can find the `stream_path` of your camera by opening a PC that is already connected to the camera device, and run `tcpdump` or `wireshark` to get the url which contains the `stream_path`. See below how the python script expects the `stream_path`:

  ```
  rtsp://{username}:{password}@{ip}:554/{stream_path}
  ```

## Next Steps

* Ability to configure the period of each file for example daily, or hourly. Currently it is hardcoded to make daily `avi` files.
* Compressing the video files before writing.

## References

[rtsp protocol](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol)
