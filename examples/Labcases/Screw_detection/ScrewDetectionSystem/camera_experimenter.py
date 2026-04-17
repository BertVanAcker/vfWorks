import os
import time
import pyrealsense2 as rs
import cv2
import numpy as np
import yaml
from pathlib import Path
from vfworks.utils.auxiliary import *


class ScrewDetectionSystem:
    def __init__(self, name,VERBOSE=True, DEPLOYED=False, monitorPeriod=0.5):
        self.model = None
        self.models = []
        self.MODELLOADED = False
        self.monitorActive = False
        self.timeStamps = []
        self.timestamp = 0.0
        self.name = name
        self.measurement = None
        self.VERBOSE = VERBOSE
        self.config = self.load_config("config.yaml")
        config = self.config['dp_config']

        self.monitorPeriod = monitorPeriod
        #self.t_monitor = perpetualTimer(self.monitorPeriod, self.monitor)

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def run_camera_experimenter(self, conditions, output_folder="dataset\images", num_images=100, resolution=(640, 480), fps=30):
        train_folder = os.path.join(output_folder, "train")
        validation_folder = os.path.join(output_folder, "val")
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(train_folder, exist_ok=True)
        os.makedirs(validation_folder, exist_ok=True)
        # Configure depth and color streams
        pipeline = rs.pipeline()
        config = rs.config()
        width, height = resolution
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)

        # Start streaming
        pipeline.start(config)
        try:
            # Let camera auto-exposure settle a bit
            for _ in range(30):
                pipeline.wait_for_frames()
            for i in range(num_images):
                # Wait for a coherent pair of frames
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                if not color_frame:
                    print(f"Warning: no color frame received at index {i}, skipping.")
                    continue
                # Convert image to numpy array
                color_image = np.asanyarray(color_frame.get_data())
                # Build filename: img_0001.png, img_0002.png, ...
                if i >= 0.67 * num_images:
                    filename = os.path.join(validation_folder, f"img_{i:04d}.png")
                else:
                    filename = os.path.join(train_folder, f"img_{i:04d}.png")
                # Save using OpenCV
                cv2.imwrite(filename, color_image)
                print(f"Saved {filename}")
                # Small delay so filenames are nicely spaced in time (optional)
                time.sleep(0.05)
        finally:
            # Stop streaming
            pipeline.stop()
            print("Capture finished and pipeline stopped.")
            dataset_location = Path(__file__).parent / "dataset"
            dataset_metadata = dict(names = {1:"noscrew", 0:"screw"}, val="images/val", train="images/train", path=str(dataset_location))
            with open("dataset_metadata.yaml", "w") as f:
                yaml.dump(dataset_metadata, f)



if __name__ == "__main__":
    #TODO automate conditions regarding the actual LED settings
    #TODO check content of conditions.yaml what info is needed, what can be autmatically determined, does metadata originate in DSL or from experimenter, integration with MLFlow?
    num_images = 100
    system = ScrewDetectionSystem(name="screwDetectionSystem")
    conditions = dict(colorRed = "0", colorGreen = "0", colorBlue = "255", brightness = "114", imageCount = num_images)

    system.run_camera_experimenter(conditions=conditions, num_images=num_images)

    with open("conditions.yaml", 'w') as outfile:
        yaml.dump(conditions, outfile)
