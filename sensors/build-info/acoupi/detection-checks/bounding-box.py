import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import json
import os

audio_file = '20260120_174433.wav'
detection_file = 'detection-20260120.json'

def plot_bat_detections(wav_file, json_file, output_image='bat_detections_output.png'):
    # Load detection data from JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Load the audio file
    sample_rate, audio_data = wavfile.read(wav_file)
    
    # If the file is stereo, use only the first channel
    if len(audio_data.shape) > 1:
        audio_data = audio_data[:, 0]
        
    # Create the Plot
    plt.figure(figsize=(14, 7))
    
    # Generate the spectrogram - convert raw audio signal into a visual heat map of sound. 
    # Using a Short-Time Fourier Transform (STFT) to analyze how frequencies change over time
    # NFFT=1024 provides a good balance between time and frequency resolution for 192kHz audio
    # Pxx (Spectrum): A 2D array representing the power of each frequency at each time point (the actual "heat" data).
    # freqs: A 1D array of the frequency values (the Y-axis labels).
    # bins (or t): A 1D array of the time points (the X-axis labels).
    # cmap options:
    # magma / inferno	Spotting faint calls	Black → Purple → Yellow
    # viridis	Long hours of screen review	Purple → Blue → Green
    # jet / turbo	Finding "hidden" harmonics	Full Rainbow
    # gray_r	Academic papers / Printing	White background, Black calls
    Pxx, freqs, bins, im = plt.specgram(audio_data, NFFT=1024, Fs=sample_rate, noverlap=512, cmap='viridis')
    
    plt.title(f'Spectrogram: {os.path.basename(wav_file)} with BatDetect2 Annotations')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.colorbar(label='Intensity (dB)')
    plt.ylim(0, sample_rate / 2) # Show up to the Nyquist frequency (96kHz)
    
    # Draw bounding boxes from the JSON detections
    for det in data.get('detections', []):
        # Extract coordinates [t_min, f_min, t_max, f_max]
        coords = det.get('location', {}).get('coordinates', [])
        
        if len(coords) == 4:
            t_min, f_min, t_max, f_max = coords
            
            # Create a rectangle patch: (x, y), width, height
            rect = plt.Rectangle((t_min, f_min), t_max - t_min, f_max - f_min,
                                 linewidth=1, edgecolor='cyan', facecolor='none', alpha=0.8)
            plt.gca().add_patch(rect)
            
            # Extract species name for labeling
            species_name = "Unknown"
            conf_score = 0
            
            for tag_info in det.get('tags', []):
                if tag_info.get('tag', {}).get('key') == 'species':
                    species_name = tag_info['tag']['value'].split(' ')[-1] # e.g., "pipistrellus"
                    conf_score = tag_info.get('confidence_score', 0)
                    break
            
            # Create the label string (e.g., "pipistrellus (74%)")
            label_text = f"{conf_score:.0%} {species_name}"

            # Apply the label to the plot
            # plt.text(t_min, f_max + 1500, label_text, color='cyan', fontsize=8, alpha=0.8, fontweight='bold')
            # Apply the label vertically above the call
            plt.text(
                t_min + (t_max - t_min) / 2,  # X: Center of the box
                f_max + 2000,                 # Y: Slightly above the box
                label_text, 
                color='cyan', 
                fontsize=8, 
                alpha=0.8, 
                fontweight='bold',
                rotation=90,                  # Rotate 90 degrees
                verticalalignment='bottom',   # Align from the bottom of the text
                horizontalalignment='center'  # Center the text horizontally
            )

    plt.tight_layout()
    plt.savefig(output_image)
    print(f"Spectrogram with detections saved to {output_image}")

# Run the script
plot_bat_detections(audio_file, detection_file)