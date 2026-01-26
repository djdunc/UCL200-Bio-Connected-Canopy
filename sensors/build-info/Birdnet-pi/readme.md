# Birdnet-pi setup 
Note: installed with audiomoth and cam module 3

# Data Sample

An example data packet sent via MQTT is in the file `detection-payload.json`.

```json
{
  "name_model": "BirdNET-Pi",
  "recording": {
    "created_on": "2026-01-26T15:44:30",
    "latitude": 51.5963,
    "longitude": -0.1471
  },
  "detections": [
    {
      "detection_score": 0.9108,
      "tags": [
        {
          "tag": {
            "key": "common_name",
            "value": "European Starling"
          },
          "confidence_score": 0.9108
        },
        {
          "tag": {
            "key": "scientific_name",
            "value": "Sturnus vulgaris"
          },
          "confidence_score": 0.9108
        }
      ]
    }
  ]
}
```
# Maintenance helpers

Passwords in LastPass - UCL200 Biocanopy

To view logs 
`systemctl list-units --type=service --state=running` see whats running

`journalctl -u birdnet-log.service -n 50 --no-pager`

`journalctl -u chart_viewer.service -n 50 --no-pager`

`df -h` to check disk usage

To check if MediaMTX is running ok (video stream):

`journalctl -u mediamtx -n 50 --no-pager`


# Setup Notes for Birdnet-pi

1. RPi5 64bit Trixie build - 192.168.1.191 on home network
2. turned on VNC
3. Setup AudioMoth as USB mic with std settings 48k, medium, no filter
4. Ran Birdnet-pi installer from https://github.com/Nachtzuster/BirdNET-Pi 

`curl -s https://raw.githubusercontent.com/Nachtzuster/BirdNET-Pi/main/newinstaller.sh | bash`

5. login to settings page using birdnet user 
6. set password
7. lat long 51.5254, -0.1326
8. disk mgt set to 80% and files to keep = 10
9. apprise setting: `mqtt://CEDevice:xxxxxxxxx@mqtt.cetools.org:1884/UCL/GordonStreet/Birdnet-pi` with payload:

```json
{
  "name_model": "BirdNET-Pi",
  "recording": {
    "created_on": "$dateT$time",
    "latitude": $latitude,
    "longitude": $longitude
  },
  "detections": [
    {
      "detection_score": $confidence,
      "tags": [
        {
          "tag": {
            "key": "common_name",
            "value": "$comname"
          },
          "confidence_score": $confidence
        },
        {
          "tag": {
            "key": "scientific_name",
            "value": "$sciname"
          },
          "confidence_score": $confidence
        }
      ]
    }
  ]
}
```

10. added in wifi creds for UCL_IoT and got mac address

### Camera setup

Also wanted to have camera module 3 working alongside audiomoth usb mic.

Plugged in a cam mod 3 `rpicam-hello --list-cameras`
tested via `rpicam-vid -t 5000 --autofocus-mode continuous -o test.h264`

Ran test rstp feed: 
`rpicam-vid -t 0 -n --codec libav --libav-format mpegts -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/stream1}'`

viewed via vlc : `rtsp://192.168.1.191:8554/stream1`

For more permanent setup used MediaMTX https://github.com/bluenviron/mediamtx/releases

Download and extract

`cd ~`

`wget https://github.com/bluenviron/mediamtx/releases/download/v1.15.6/mediamtx_v1.15.6_linux_arm64.tar.gz`

`tar -xvzf mediamtx_v1.15.6_linux_arm64.tar.gz`

Move Binary and Set Permissions:

`sudo mv mediamtx /usr/local/bin/`

`sudo chmod +x /usr/local/bin/mediamtx`

Initialize the Configuration

`sudo mkdir -p /etc/mediamtx/`

`sudo mv mediamtx.yml /etc/mediamtx/mediamtx.yml`

Open the config file to add the camera logic
`sudo nano /etc/mediamtx/mediamtx.yml`
and add this at bottom :

```yaml
paths: 
	roof: 
		runOnInit: > 
			bash -c 'rpicam-vid -t 0 -n --width 1280 --height 720 --framerate 15 --codec libav --libav-format mpegts --inline --autofocus-mode continuous -o - | ffmpeg -i - -c copy -f rtsp rtsp://localhost:$RTSP_PORT/roof'		
		runOnInitRestart:yes
```

stream then visible at `rtsp://192.168.1.191:8554/roof`

Set up to run automatically:
`sudo nano /etc/systemd/system/mediamtx.service`

```toml
[Unit]
Description=MediaMTX RTSP Server
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/mediamtx /etc/mediamtx/mediamtx.yml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

enable and start

`sudo systemctl daemon-reload` 

`sudo systemctl enable mediamtx` 

`sudo systemctl start mediamtx`

check to see if all looks ok
`journalctl -u mediamtx -n 50 --no-pager`

added in a web view via the Birdnet Caddy web server
note web files in `ls /home/pi/BirdSongs/Extracted/` on Birdnet-pi

`sudo nano /home/pi/BirdSongs/Extracted/roof.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Green Roof Live Feed</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            font-family: sans-serif;
        }
        .video-container {
            width: 95vw;
            height: 95vh;
            max-width: 1280px;
            max-height: 720px;
            border: 2px solid #333;
            box-shadow: 0 0 20px rgba(0,255,0,0.1);
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        .overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="overlay">LIVE | Green Roof Sensor</div>
    <div class="video-container">
        <iframe src="http://192.168.1.191:8889/roof"></iframe>
    </div>
</body>
</html>
```

For Caddy to serve the file, you must ensure the caddy user (or the user BirdNET-Pi uses for the web server) can read it:

`sudo chown caddy:caddy /home/pi/BirdSongs/Extracted/roof.html`

`sudo chmod 644 /home/pi/BirdSongs/Extracted/roof.html`



