# Acoupi Device Build

# Data Sample

An example data packet sent via MQTT is in the file `sample-detection.json`. Below is the key information for a single detection (there could be multiple detections in a single 3 second recording):

```json
  "detections": [
    {
      "id": "267e2ee9-48dd-4d8d-8ac0-a6171cc51533",
      "location": {
        "type": "BoundingBox",
        "coordinates": [
          0.7655,
          46953,
          0.7706,
          61637
        ]
      },
      "detection_score": 0.759,
      "tags": [
        {
          "tag": {
            "key": "species",
            "value": "Pipistrellus pipistrellus"
          },
          "confidence_score": 0.746
        }
      ]
    }
  ]
```

The coordinates identify where the detection is located in the spectrogram image. The values represent:
- Xmin: 0.7655 - number of seconds into the 3 second recording
- Ymin: 46953 - frequency value in the spectrogram image (0-96kHz)
- Xmax: 0.7706 - number of seconds into the 3 second recording
- Ymax: 61637 - frequency value in the spectrogram image (0-96kHz)

detection_score is the confidence score for the detection overall.

confidence_score is the confidence score for the specific tag (species in this case).

# Maintenance helpers

To view logs (recording, beat, default):

`tail -f /home/pi/.acoupi/log/default.log`

`acoupi deployment status`

`acoupi check`

`sudo nano .acoupi/config/program.json`


# Setup Notes for Batdetect2 version

RPi5 installed 64 bit OS

Setup Audiomoth as USB device using Audio-Moth Mic app v 1.2.4:
https://www.openacousticdevices.info/usb-microphone
First update firmware using `AudioMoth-Flash` (app used v1.7, select USB, firmware v1.31)
Then ran AudioMoth-Config app and used default settings 384kHz
Set switch on audimoth to default

Plugged into RPi and tested connection using `lsusb` on terminal and `arecord -l` to see the device number. In my case:
```
**** List of CAPTURE Hardware Devices ****
card 2: Microphone [384kHz AudioMoth USB Microphone], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

Installed Audacity to check microphone settings:
`sudo apt install audacity`

Also tried a dodotronic ultramic for comparison:
```
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 05ac:1006 Apple, Inc. Hub in Aluminum Keyboard
Bus 001 Device 003: ID 05ac:0221 Apple, Inc. Aluminum Keyboard (ISO)
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 006: ID 0869:0308 DODOTRONIC Technology . UltraMic 192K 16 bit r4
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
```

Then followed instructions to install acoupi_batdetect2 at:
https://acoupi.github.io/acoupi_batdetect2/tutorials/installation/

At step 2 realised the default install on RPi was 3.13 so need to set up a virtual environment for this python project. Ran: `sudo apt update` and `sudo apt upgrade`

Download the ARM64 installer for Miniconda (Miniforge):
`wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh`

Ran the installer using default locations:
`bash Miniforge3-Linux-aarch64.sh`

Create Bat Detection environment:
`conda create -n bat_env python=3.11`
`conda activate bat_env` 

Then return to Step 2 in installation instructions:
`pip install acoupi_batdetect2`

Once installed I couldnt use CLI to edit values so edited directly at
`sudo nano .acoupi/config/program.json`

Used the following to prettify the JSON for easier editing with nano
`python3 -m json.tool ~/.acoupi/config/program.json > temp.json && mv temp.json ~/.acoupi/config/program.json`

Tip for moving files to / from mac via iterm:
`scp pi@192.168.1.159:~/.acoupi/config/program.json ~/Desktop/`
`scp ~/Desktop/program.json pi@192.168.1.159:~/.acoupi/config/program.json`

Setup UCL_IoT access:
get mac address of device: `ip link show wlan0` and then add them to manage-my-devices via import route to set password to `UCL200-sensor-devices-ucjtdjw`
acoupi-bat: 2c:cf:67:e5:1b:f8
acoupi-bird: 2c:cf:67:e5:1c:01
then add to network manager:
```
sudo nmcli connection add type wifi con-name "UCL_IoT" ifname wlan0 ssid "UCL_IoT"

sudo nmcli connection modify "UCL_IoT" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "xxxx"
```
note: password is on manage-my-devices page and in lastpass

and then check it had registered:
`nmcli -s -f 802-11-wireless-security.psk connection show "UCL_IoT"`

# Setup Notes for Birdnet version

First set up the audiomoth as USB mic using AudioMoth-mic app.
used settings 48kHz, medium gain.

1. RPi5 64 build
2. setup VNC
3. `sudo apt install audacity`
4. Ran: `sudo apt update` and `sudo apt upgrade`
5. `wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh`
6. `bash Miniforge3-Linux-aarch64.sh`
7. `conda create -n bird_env python=3.11`
8. `conda activate bird_env`
9. `curl -sSL https://github.com/acoupi/acoupi/raw/main/scripts/setup.sh | bash`
10. `pip install acoupi_birdnet`
11. `acoupi setup --program acoupi_birdnet.program`
12. `python3 -m json.tool ~/.acoupi/config/program.json > temp.json && mv temp.json ~/.acoupi/config/program.json`
13. On mac: `scp pi@192.168.1.190:~/.acoupi/config/program.json ~/Desktop/`
14. On mac: `scp ~/Desktop/program.json pi@192.168.1.190:~/.acoupi/config/program.json`
15. added in wifi creds for UCL_IoT and got mac address
16. `acoupi deployment start` acoupi-bird-gordon-street, 51.52539844678313, -0.13259666228703001
17. `acoupi deployment status`

Tweaks made to stop human voice detections:
edit the file at `/home/pi/miniforge3/envs/bird_env/lib/python3.11/site-packages/acoupi_bird ` to both set `common_name: bool = False` to true and add in the following at bottom of file (line: 84) `if predicted_tag.tag.value != "Human vocal"`  - this last line only builds data. Detection object if the value is not human.

Test via `grep "Human vocal" /home/pi/.acoupi/log/default.log`


# Telegraf configuration

to be added - current prototype is in DW notebook