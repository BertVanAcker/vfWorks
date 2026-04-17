from Font import putTTFText
from ultralytics import YOLO
import cv2
import time
import numpy as np
import torch
import pyrealsense2 as rs
import threading


class ScrewSegmentation:

    def __init__(self, main_folder, camera_width=1920, camera_height=1080, exposure_time=250):
        # Set the main folder where the calibration files are stored
        self.main_folder = main_folder
        # Check if GPU is available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # print("Using device: ", self.device)
        # Load the trained detection model
        self.model_1 = self.load_model('models/best.pt')
        self.model_2 = self.load_model('models/best_red.pt')
        self.model_3 = self.load_model('models/diff_exposure.pt')
        self.active_model = 1
        # Load the intrinsic matrix and cam2gripper transformation matrix from calibration
        # self.intrinsic_matrix = self.load_intrinsic()

        # Initialize the realsense camera
        self.camera_width = 640  # 640
        self.camera_height = 480  # 480
        self.exposure_time = exposure_time
        self.camera_pipeline_running = False
        self.pipeline, self.config, self.align = self.init_realsense(aligned=True)

        # init flags
        self.running = True
        self.max_area_threshold = 0.6
        self.show_detections = True

        # Synchronization: use locks and in-memory storage
        self.detection_lock = threading.Lock()
        self.detected_pc_screen_image = None
        self.detected_holders_image = None
        self.detected_screws_image = None


    @property
    def model(self):
        if self.active_model == 1:
            model = self.model_1
        elif self.active_model == 2:
            model = self.model_2
        else:
            model = self.model_3
        return model

    def load_model(self, model_path, model_type="yolo"):
        if model_type == "yolo":
            # Load the trained object detection model
            model = YOLO(model_path)
            model.fuse()
        return model

    def init_realsense(self, aligned=True):
        # Create a pipeline for realsense camera
        pipeline = rs.pipeline()
        # Create a config object
        config = rs.config()

        # Enable the color and depth streams frm the camera
        #config.enable_stream(rs.stream.color, self.camera_width, self.camera_height, rs.format.bgr8, 30)
        #config.enable_stream(rs.stream.depth, self.camera_width, self.camera_height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, self.camera_width, self.camera_height, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, self.camera_width, self.camera_height, rs.format.z16, 30)
        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        if aligned:
            align_to = rs.stream.color
            align = rs.align(align_to)
        else:
            align = None

        # Start the pipeline
        pipeline.start(config)
        try:
            # Get frames and images
            pipeline.wait_for_frames(100)
        except RuntimeError:
            # Reset device and try again

            pipeline.stop()
            ctx = rs.context()
            devices = ctx.query_devices()
            for dev in devices:
                dev.hardware_reset()

            time.sleep(2)
            pipeline = rs.pipeline()
            pipeline.start(config)
            self.camera_pipeline_running = True
            print("Device reset")

        return pipeline, config, align

    def run(self):
        # Start the camera feed in a separate thread
        camera_thread = threading.Thread(target=self.predict_real_time)
        camera_thread.start()

    def predict_real_time(self):
        save_img_counter = 0
        sensor = self.pipeline.get_active_profile().get_device().query_sensors()[1]
        # sensor.set_option(rs.option.enable_auto_exposure, False)
        sensor.set_option(rs.option.exposure, self.exposure_time)
        color_image_with_detections = None
        default_conf_score = 0.7

        while self.running:
            # Get frames and images
            self.aligned_frames_and_images()

            # Check if screws are detected through the trained segmentation model
            results = self.predict(self.color_image, conf_score=default_conf_score)
            if self.show_detections:
                default_conf_score = 0.7
                color_image_with_detections, bbox_center_holders, bbox_center_screws, bbox_center_no_screws = self.plot_bboxes(
                    results, self.color_image)

            if color_image_with_detections is not None:
                # Show camera feed
                cv2.imshow('Camera Feed', color_image_with_detections)
            else:
                cv2.imshow('Camera Feed', self.color_image.copy())
            # Create a larger canvas to hold the 2x2 matrix of images
            canvas_height = int(self.camera_height * 1.3)
            canvas_width = int(self.camera_width * 1.3)
            canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
            resized_img_width = int(canvas_width / 2)
            resized_img_height = int(canvas_height / 2)

            # Get the latest detection images (thread-safe)
            with self.detection_lock:
                pc_screen_img = self.detected_pc_screen_image
                holders_img = self.detected_holders_image
                screws_img = self.detected_screws_image

            # Place the detected PC screen image in the top left corner of the canvas
            if pc_screen_img is not None:
                pc_screen_resized = cv2.resize(pc_screen_img, (resized_img_width, resized_img_height))
                canvas[0:resized_img_height, 0:resized_img_width] = pc_screen_resized
                cv2.putText(canvas, 'PC Screen Detection', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Place the detected holders image in the bottom left corner of the canvas
            if holders_img is not None:
                holders_resized = cv2.resize(holders_img, (resized_img_width, resized_img_height))
                canvas[resized_img_height:, 0:resized_img_width] = holders_resized
                cv2.putText(canvas, 'Holders Detection', (10, resized_img_height + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2)

            # Place the detected screws image in the top right corner of the canvas
            if screws_img is not None:
                screws_resized = cv2.resize(screws_img, (resized_img_width, resized_img_height))
                canvas[0:resized_img_height, resized_img_width:] = screws_resized
                cv2.putText(canvas, 'Zoom-in Detection', (resized_img_width + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2)
            # Display timers in the bottom-left corner
            x_offset = resized_img_width + 50
            y_offset = resized_img_height + 50
            # Display the elapsed time for each process
            y_offset += 50

            # Show the canvas with the detected images
            cv2.imshow('Detection results', canvas)

            # Free GPU memory
            torch.cuda.empty_cache()

            # Break the loop if 'q' is pressed
            pressed_key = cv2.waitKey(1) & 0xFF
            if pressed_key == ord('q'):
                print("q pressed, closing camera feed")
                break
                # change the active model if 'c' is pressed
            elif pressed_key == ord('c'):
                self.change_active_model(0)
            # set the exposure time if 'e' is pressed
            elif pressed_key == ord('e'):
                print("Enter the exposure time: ")
                self.exposure_time = int(input())
                sensor.set_option(rs.option.exposure, self.exposure_time)
            # Set the max area threshold if 't' is pressed
            elif pressed_key == ord('t'):
                print("Enter the threshold: ")
                threshold = float(input())
                self.max_area_threshold = threshold
            # Auto exposure if 'a' is pressed
            elif pressed_key == ord('a'):
                self.auto_exposure()
            elif pressed_key == ord('w'):
                self.show_detections = not self.show_detections

        self.pipeline.stop()
        self.camera_pipeline_running = False
        cv2.destroyAllWindows()

    def aligned_frames_and_images(self):
        # Get frameset of color and depth
        self.frames = self.pipeline.wait_for_frames(5000)

        # Align the depth frame to color frame
        aligned_frames = self.align.process(self.frames)

        # Get aligned frames
        self.depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a self.camera_width x self.camera_height depth image
        self.color_frame = aligned_frames.get_color_frame()

        if not self.depth_frame or not self.color_frame:
            raise RuntimeError("Could not acquire depth or color frame.")

        # Convert images to numpy arrays
        self.color_image = np.asanyarray(self.color_frame.get_data())
        self.depth_image = np.asanyarray(self.depth_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        self.depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(self.depth_image, alpha=0.5), cv2.COLORMAP_JET)
        # img_undist = cv2.undistort(color_image)

        # Get realsense camera intrinsic
        self.color_intrinsic = self.color_frame.profile.as_video_stream_profile().intrinsics
        self.depth_intrinsic = self.depth_frame.profile.as_video_stream_profile().intrinsics

    def predict(self, frame, conf_score=0.75):
        # Predict the segmentation results
        results = self.model.predict(frame, conf=conf_score, verbose=False, iou=0.1)
        return results

    def plot_bboxes(self, results, frame_input, show_class=[True, True, True]):
        bbox_center_holders = []
        bbox_center_screws = []
        bbox_center_no_screws = []

        frame = frame_input.copy()
        # show bounding boxes on images - if class = 0 then write class name on top of bounding box else write class name under bounding box
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                class_name = self.model.names[class_id]
                confidence = box.conf[0]  # Get the confidence score
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                bbox_center = [x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2]

                # Put label and confidence on the image
                label = f"{class_name}: {confidence:.1f}"
                if class_name == "holder" and show_class[0]:
                    bbox_center_holders.append(bbox_center)
                    cv2.putText(frame, label, (int(x1), int(y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # Draw bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                elif class_name == "screw" and show_class[1]:
                    bbox_center_screws.append(bbox_center)
                    cv2.putText(frame, label, (int(x1), int(y2 + 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # Draw bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                elif class_name == "noscrew" and show_class[2]:
                    bbox_center_no_screws.append(bbox_center)
                    cv2.putText(frame, label, (int(x1), int(y2 + 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                    # Draw bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
        return frame, bbox_center_holders, bbox_center_screws, bbox_center_no_screws

    def change_active_model(self, model_number):
        if model_number not in [1, 2, 3]:
            # self.active_model = 1 if self.active_model == 2 else 2
            if self.active_model == 1:
                self.active_model = 2
            elif self.active_model == 2:
                self.active_model = 3
            else:
                self.active_model = 1
        else:
            self.active_model = model_number
        print(f"\nModel {self.active_model} is active")

    def auto_exposure(self, threshold=200, decrement=50):
        sensor = self.pipeline.get_active_profile().get_device().query_sensors()[1]
        while True:
            # Get frames and images
            self.aligned_frames_and_images()

            # Calculate the histogram
            hist = self.calculate_histogram()
            print("Histogram calculated ", np.average(hist[200:]))
            if hist is not None:
                avg_hist_value = np.average(hist[200:])
                print(f"Average histogram value: {avg_hist_value}")

                # Check if the average histogram value is above the threshold
                if avg_hist_value > threshold:
                    # Decrease the exposure time
                    self.exposure_time = max(1, self.exposure_time - decrement)
                    sensor.set_option(rs.option.exposure, self.exposure_time)
                    print(f"Exposure time decreased to: {self.exposure_time}")
                    time.sleep(0.1)
                else:
                    break

    def calculate_histogram(self):
        if self.color_image is not None:
            # Convert the image to grayscale
            frame = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2GRAY)

            # Calculate the histogram for the grayscale image
            hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
            return hist
        else:
            print("No color image available to calculate histogram.")
            return None


if __name__ == "__main__":
    screw_detector = ScrewSegmentation("screw_folder")

    screw_detector.run()


