# RPi Camera Sensor Build Info

Hybrid Pipeline - wanted to be able to stream camera view to allow ofor offline analysis and also run local Edge AI. Instead of having MediaMTX and YOLOv11 "fight" over the camera hardware, intention is to use the **MediaMTX RTSP stream as the source** for YOLO script. This allows the camera to be shared between the server and the AI models.

UCL200-rpi5-cam1 setup

1. RPi5 64 build
2. setup VNC
3. `ip link show wlan0`  then add to network manager:
```bash
sudo nmcli connection add type wifi con-name "UCL_IoT" ifname wlan0 ssid "UCL_IoT"

sudo nmcli connection modify "UCL_IoT" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "xxxxx"
```
and check it had registered:
```bash
nmcli -s -f 802-11-wireless-security.psk connection show "UCL_IoT"
```
4. Ran: `sudo apt update` and `sudo apt upgrade`

### MediaMTX setup

Download and extract

`cd ~`

`wget https://github.com/bluenviron/mediamtx/releases/download/v1.15.6/mediamtx_v1.15.6_linux_arm64.tar.gz`

`tar -xvzf mediamtx_v1.15.6_linux_arm64.tar.gz`

Move Binary and Set Permissions

`sudo mv mediamtx /usr/local/bin/`

`sudo chmod +x /usr/local/bin/mediamtx`

Initialize the Configuration

`sudo mkdir -p /etc/mediamtx/`

`sudo mv mediamtx.yml /etc/mediamtx/mediamtx.yml`

Open the config file to add the camera logic `sudo nano /etc/mediamtx/mediamtx.yml` and add this at bottom :

```yml
paths: 
	cam: 
		runOnInit: bash -c 'rpicam-vid -t 0 -n --width 1280 --height 720 --framerate 15 --codec libav --libav-format mpegts --inline --autofocus-mode continuous --profile baseline --bitrate 2000000 -o - | ffmpeg -i - -c copy -f rtsp rtsp://localhost:$RTSP_PORT/cam' 
		runOnInitRestart: yes
```

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

stream then visible at `rtsp://192.168.1.169:8554/cam`

### setup yolo ultralytics environment
Download the ARM64 installer:
`wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh`

Ran the installer using default locations:
`bash Miniforge3-Linux-aarch64.sh`

used notes here: https://core-electronics.com.au/guides/raspberry-pi/how-to-set-up-yolo-computer-vision-on-a-raspberry-pi-conda-and-ultralytics/

(Note- hours of challenges with trixie, picamera and numpy v1.2 / 2.2 issues - ended up creating a camera stream with mediamtx and then using that as the source rather than picamera2 for projects on this device.)

Prepare Conda (System level) 

`conda install conda-libmamba-solver -y`

`conda config --set solver libmamba`

Create the Env 

`conda create --name ultralytics-env python=3.11 -y` 

`conda activate ultralytics-env` 

Install AI Stack. This forces the solver to find a version of Ultralytics that is happy with NumPy 1.x 

`conda install -c conda-forge ultralytics "numpy<2.0" -y pytorch pytorch torchvision cpuonly -y`

This version does NOT force a NumPy 2.0 upgrade 

`pip install ncnn opencv-python-headless==4.10.0.84`

`pip install requests tqdm`

Check for Hidden Paths - If it still crashes, it means your PYTHONPATH variable is set to include the system folders. Run this to check:

`echo $PYTHONPATH`

If it prints anything containing **/usr/lib/python3/dist-packages** you must clear it

`unset PYTHONPATH`

now if you try:

`PYTHONNOUSERSITE=1 python -c "import numpy; print(f'Location: {numpy.__file__}'); print(f'Version: {numpy.__version__}')"`

should get version 1.26.4

Conda allows you to set variables that only exist when a specific environment is active:

`conda env config vars set PYTHONNOUSERSITE=1`

### Final Stable Stack
* **Video Source:** MediaMTX (Handles the hardware lock and libcamera drivers).
* **Video Transport:** RTSP Stream (rtsp://localhost:8554/cam).
* **AI Environment:** Isolated Conda (ultralytics-env).
* **Compatibility Lock:** PYTHONNOUSERSITE=1 (Forces Python to ignore the system's NumPy 2.2.4).
* **Inference Engine:** YOLOv11 exported to **NCNN** (Optimized for Pi 5 CPU).

look at this video for setting up ultralytics: https://www.youtube.com/watch?v=ALsH6zU4TVM