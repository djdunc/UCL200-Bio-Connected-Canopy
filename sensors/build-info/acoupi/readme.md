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