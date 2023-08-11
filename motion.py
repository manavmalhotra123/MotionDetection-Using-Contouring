import cv2
import numpy as np
import pygame
import time
import threading

class MotionDetector:
    def __init__(self, video_source=0, audio_file="alarm.mp3"):
        self.cap = cv2.VideoCapture(video_source)
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.audio_file = audio_file
        self.audio_duration = 5

        # Initialize Pygame and load the alarm sound
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_file)

        self.min_contour_area = 1000
        self.motion_detected = False
        self.motion_start_time = None

    def play_audio(self):
        pygame.mixer.music.play()
        time.sleep(self.audio_duration)
        pygame.mixer.music.stop()

    def detect_motion(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Preprocessing
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
            fg_mask = self.bg_subtractor.apply(blurred_frame)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            
            # Find contours in the foreground mask
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.min_contour_area:
                    if not self.motion_detected:
                        self.motion_detected = True
                        self.motion_start_time = time.time()
                        threading.Thread(target=self.play_audio).start()  # Play the alarm sound in a separate thread
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            cv2.imshow('Motion Detector', frame)
            cv2.imshow('Foreground Mask', fg_mask)  # Display the foreground mask
            
            if self.motion_detected and (time.time() - self.motion_start_time > self.audio_duration):
                self.motion_detected = False

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = MotionDetector(video_source=0, audio_file="alarm.mp3")
    detector.detect_motion()