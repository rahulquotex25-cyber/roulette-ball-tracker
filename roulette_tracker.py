import cv2
import numpy as np
from collections import deque
import sys
import os

# Standard European roulette wheel layout (clockwise from 0)
EUROPEAN_WHEEL = [0, 26, 3, 35, 12, 28, 7, 29, 18, 22, 9, 31, 14, 20, 1, 33,
                  16, 24, 5, 10, 23, 8, 30, 11, 36, 13, 27, 6, 34, 17, 25, 2,
                  21, 4, 19, 15, 32]

class RouletteWheelDetector:
    """Advanced wheel detection optimized for various lighting conditions"""
    
    def __init__(self):
        self.wheel_center = None
        self.wheel_radius = None
        self.wheel_mask = None
        
    def detect_wheel_advanced(self, image):
        """Advanced wheel detection with multiple methods"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Hough Circle Detection with adaptive parameters
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Enhance edges
        edges = cv2.Canny(blurred, 50, 150)
        
        # Try with different parameters for robustness
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.0,
            minDist=150,
            param1=80,
            param2=25,
            minRadius=100,
            maxRadius=600
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            # Get the largest circle (usually the wheel)
            c = circles[0][np.argsort(circles[0, :, 2])[-1]]
            self.wheel_center = (int(c[0]), int(c[1]))
            self.wheel_radius = int(c[2])
            
            # Create mask for wheel region
            self.wheel_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.circle(self.wheel_mask, self.wheel_center, self.wheel_radius, 255, -1)
            
            return True
        
        return False
    
    def get_wheel_info(self):
        """Return wheel center and radius"""
        return self.wheel_center, self.wheel_radius
    
    def visualize_wheel(self, image):
        """Draw wheel on image"""
        result = image.copy()
        if self.wheel_center is not None:
            cv2.circle(result, self.wheel_center, self.wheel_radius, (0, 255, 255), 3)
            cv2.circle(result, self.wheel_center, 5, (0, 0, 255), -1)
            # Draw radii
            for angle in range(0, 360, 30):
                rad = np.radians(angle)
                x = int(self.wheel_center[0] + self.wheel_radius * np.cos(rad))
                y = int(self.wheel_center[1] + self.wheel_radius * np.sin(rad))
                cv2.line(result, self.wheel_center, (x, y), (100, 100, 100), 1)
        
        return result


class AdvancedBallTracker:
    """Advanced ball detection with motion tracking"""
    
    def __init__(self, history_size=50):
        self.ball_position = None
        self.ball_radius = None
        self.trajectory = deque(maxlen=history_size)
        self.velocity = None
        self.velocity_magnitude = 0
        self.angle_history = deque(maxlen=10)
        
    def detect_ball_advanced(self, image, wheel_center, wheel_radius):
        """Multi-method ball detection"""
        
        # Method 1: HSV color detection (white/cream ball)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Multiple ranges for different lighting
        lower_white1 = np.array([0, 0, 180], dtype=np.uint8)
        upper_white1 = np.array([180, 30, 255], dtype=np.uint8)
        
        lower_white2 = np.array([0, 0, 150], dtype=np.uint8)
        upper_white2 = np.array([180, 50, 255], dtype=np.uint8)
        
        mask1 = cv2.inRange(hsv, lower_white1, upper_white1)
        mask2 = cv2.inRange(hsv, lower_white2, upper_white2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Restrict to wheel area
        wheel_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(wheel_mask, wheel_center, wheel_radius, 255, -1)
        mask = cv2.bitwise_and(mask, wheel_mask)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False
        
        # Filter by area and circularity
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 10:
                continue
            
            # Check circularity
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity > 0.6:  # Circle-like
                valid_contours.append(contour)
        
        if not valid_contours:
            return False
        
        # Get largest circle
        largest_contour = max(valid_contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        
        if radius > 2 and radius < 50:
            self.ball_position = (int(x), int(y))
            self.ball_radius = int(radius)
            self.trajectory.append(self.ball_position)
            
            # Calculate velocity
            if len(self.trajectory) >= 2:
                prev_pos = self.trajectory[-2]
                curr_pos = self.trajectory[-1]
                self.velocity = (curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1])
                self.velocity_magnitude = np.hypot(self.velocity[0], self.velocity[1])
            
            return True
        
        return False
    
    def get_angle(self, wheel_center):
        """Calculate angle from wheel center to ball"""
        if self.ball_position is None:
            return None
        
        dy = self.ball_position[1] - wheel_center[1]
        dx = self.ball_position[0] - wheel_center[0]
        
        angle = np.degrees(np.arctan2(dy, dx))
        if angle < 0:
            angle += 360
        
        self.angle_history.append(angle)
        return angle
    
    def get_angular_velocity(self):
        """Calculate angular velocity"""
        if len(self.angle_history) < 2:
            return 0
        
        angle_diff = self.angle_history[-1] - self.angle_history[-2]
        
        # Handle wraparound
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
        
        return angle_diff
    
    def is_moving(self, threshold=1.5):
        """Check if ball is moving significantly"""
        return self.velocity_magnitude > threshold
    
    def get_trajectory(self):
        """Return trajectory list"""
        return list(self.trajectory)


class PredictionEngine:
    """Advanced prediction with physics simulation"""
    
    def __init__(self, wheel_layout=None):
        self.wheel_layout = wheel_layout or EUROPEAN_WHEEL
        self.num_pockets = len(self.wheel_layout)
        self.degrees_per_pocket = 360 / self.num_pockets
        
    def get_number_at_angle(self, angle_deg):
        """Get pocket number at given angle"""
        angle_deg = angle_deg % 360
        pocket_index = int((angle_deg / 360) * self.num_pockets)
        pocket_index = pocket_index % self.num_pockets
        return self.wheel_layout[pocket_index]
    
    def predict_with_physics(self, current_angle, angular_velocity, friction=0.96, max_frames=600):
        """Simulate ball deceleration and predict landing"""
        
        if angular_velocity is None or abs(angular_velocity) < 0.05:
            return None, 0.0, []
        
        # Simulate deceleration
        angle = current_angle
        velocity = angular_velocity
        friction_factor = friction
        frames = 0
        
        prediction_history = []
        
        while abs(velocity) > 0.01 and frames < max_frames:
            angle += velocity
            velocity *= friction_factor
            frames += 1
            
            # Record predictions at key points
            if frames % 50 == 0 or frames < 10:
                num = self.get_number_at_angle(angle)
                conf = min(1.0, frames / 200)
                prediction_history.append((num, conf))
        
        if frames == 0:
            return None, 0.0, []
        
        final_number = self.get_number_at_angle(angle)
        confidence = min(1.0, frames / 150)
        
        return final_number, confidence, prediction_history
    
    def get_nearby_predictions(self, current_angle, angular_velocity, friction=0.96, count=7):
        """Get primary prediction and nearby numbers"""
        
        main_pred, main_conf, _ = self.predict_with_physics(current_angle, angular_velocity, friction)
        
        if main_pred is None:
            return []
        
        try:
            pred_idx = self.wheel_layout.index(main_pred)
        except ValueError:
            return [(main_pred, main_conf)]
        
        # Get nearby numbers with decreasing confidence
        nearby = []
        for offset in range(-count, count + 1):
            idx = (pred_idx + offset) % self.num_pockets
            num = self.wheel_layout[idx]
            
            # Confidence decreases with distance
            distance_factor = 1 - (abs(offset) / (count + 1)) * 0.7
            conf = main_conf * max(0.1, distance_factor)
            
            nearby.append((num, conf))
        
        return sorted(nearby, key=lambda x: x[1], reverse=True)


class RouletteVisualizer:
    """Advanced visualization with annotations"""
    
    def __init__(self):
        self.colors = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'white': (255, 255, 255),
            'cyan': (255, 255, 0),
            'magenta': (255, 0, 255)
        }
    
    def draw_full_annotation(self, image, wheel_center, wheel_radius, ball_pos, 
                           ball_radius, trajectory, velocity, angle, predictions, moving):
        """Draw comprehensive annotation"""
        
        result = image.copy()
        h, w = image.shape[:2]
        
        # Draw wheel
        if wheel_center is not None:
            cv2.circle(result, wheel_center, wheel_radius, self.colors['cyan'], 2)
            cv2.circle(result, wheel_center, 5, self.colors['red'], -1)
        
        # Draw trajectory with fade
        if trajectory and len(trajectory) > 1:
            for i in range(1, len(trajectory)):
                pt1 = trajectory[i-1]
                pt2 = trajectory[i]
                alpha = i / len(trajectory)
                
                color = (int(100 * alpha), int(200 * alpha), 255 - int(100 * alpha))
                cv2.line(result, pt1, pt2, color, 2)
        
        # Draw ball
        if ball_pos is not None and ball_radius is not None:
            color = self.colors['yellow'] if moving else self.colors['green']
            cv2.circle(result, ball_pos, ball_radius, color, 2)
            cv2.circle(result, ball_pos, 3, color, -1)
        
        # Draw velocity vector
        if ball_pos is not None and velocity is not None and moving:
            vx, vy = velocity
            scale = 3
            end_pt = (int(ball_pos[0] + vx * scale), int(ball_pos[1] + vy * scale))
            cv2.arrowedLine(result, ball_pos, end_pt, self.colors['cyan'], 2, tipLength=0.3)
        
        # Draw predictions panel
        if predictions:
            panel_h = 30 + len(predictions[:5]) * 30
            cv2.rectangle(result, (10, 10), (350, 10 + panel_h), (20, 20, 20), -1)
            cv2.rectangle(result, (10, 10), (350, 10 + panel_h), self.colors['cyan'], 2)
            
            cv2.putText(result, "PREDICTIONS", (20, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['yellow'], 2)
            
            for i, (num, conf) in enumerate(predictions[:5]):
                y = 60 + i * 28
                
                # Color based on confidence
                if conf > 0.7:
                    color = self.colors['green']
                elif conf > 0.4:
                    color = self.colors['yellow']
                else:
                    color = self.colors['red']
                
                text = f"#{num:2d} [{conf*100:5.1f}%]"
                bar_len = int(conf * 150)
                
                cv2.putText(result, text, (20, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                
                # Draw confidence bar
                cv2.rectangle(result, (200, y - 12), (200 + bar_len, y), color, -1)
                cv2.rectangle(result, (200, y - 12), (350, y), color, 2)
        
        # Draw info panel
        info_y = h - 100
        cv2.rectangle(result, (10, info_y - 10), (400, h - 10), (20, 20, 20), -1)
        cv2.rectangle(result, (10, info_y - 10), (400, h - 10), self.colors['white'], 2)
        
        info_text = [
            f"Status: {'MOVING' if moving else 'STOPPED'}",
            f"Angle: {angle:.1f}°" if angle is not None else "Angle: N/A",
            f"Speed: {np.hypot(velocity[0], velocity[1]):.2f}px" if velocity else "Speed: N/A"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(result, text, (20, info_y + 20 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['white'], 1)
        
        return result


class RouletteSystem:
    """Complete roulette tracking system"""
    
    def __init__(self):
        self.wheel_detector = RouletteWheelDetector()
        self.ball_tracker = AdvancedBallTracker()
        self.predictor = PredictionEngine()
        self.visualizer = RouletteVisualizer()
        
        self.wheel_initialized = False
        
    def process_frame(self, frame):
        """Process single frame"""
        
        # Detect wheel (only once)
        if not self.wheel_initialized:
            if not self.wheel_detector.detect_wheel_advanced(frame):
                return None, frame
            self.wheel_initialized = True
        
        wheel_center, wheel_radius = self.wheel_detector.get_wheel_info()
        
        # Detect ball
        ball_found = self.ball_tracker.detect_ball_advanced(frame, wheel_center, wheel_radius)
        
        if not ball_found:
            annotated = self.visualizer.draw_full_annotation(
                frame, wheel_center, wheel_radius, None, None, [], None, None, [], False
            )
            return None, annotated
        
        # Calculate angle
        angle = self.ball_tracker.get_angle(wheel_center)
        angular_vel = self.ball_tracker.get_angular_velocity()
        is_moving = self.ball_tracker.is_moving()
        
        # Predict
        predictions = []
        if is_moving and abs(angular_vel) > 0.1:
            predictions = self.predictor.get_nearby_predictions(angle, angular_vel, friction=0.96, count=6)
        
        # Draw
        annotated = self.visualizer.draw_full_annotation(
            frame,
            wheel_center,
            wheel_radius,
            self.ball_tracker.ball_position,
            self.ball_tracker.ball_radius,
            self.ball_tracker.get_trajectory(),
            self.ball_tracker.velocity,
            angle,
            predictions,
            is_moving
        )
        
        result = {
            'angle': angle,
            'angular_velocity': angular_vel,
            'ball_position': self.ball_tracker.ball_position,
            'predictions': predictions,
            'is_moving': is_moving
        }
        
        return result, annotated
    
    def process_image(self, image_path):
        """Process single image"""
        print(f"\n🎰 Processing image: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Image not found")
            return None
        
        result, annotated = self.process_frame(image)
        
        if result:
            print(f"✅ Wheel detected")
            print(f"   Angle: {result['angle']:.2f}°")
            
            if result['predictions']:
                pred_num, pred_conf = result['predictions'][0]
                print(f"   🎯 Predicted: {pred_num}")
                print(f"   Confidence: {pred_conf*100:.1f}%")
                print(f"\n   Top 5:")
                for i, (num, conf) in enumerate(result['predictions'][:5], 1):
                    print(f"   {i}. Number {num}: {conf*100:.1f}%")
        
        return annotated
    
    def process_video(self, video_path, output_path=None):
        """Process video"""
        print(f"\n🎬 Processing video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"   FPS: {fps}, Size: {width}x{height}, Frames: {total_frames}")
        
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            result, annotated = self.process_frame(frame)
            
            if writer:
                writer.write(annotated)
            
            cv2.imshow('Roulette Tracker', annotated)
            
            if frame_count % 30 == 0:
                if result:
                    print(f"   Frame {frame_count}: Angle={result['angle']:.1f}° " +
                          f"Moving={result['is_moving']}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        if writer:
            writer.release()
        
        cv2.destroyAllWindows()
        print(f"✅ Video processing complete!")
        
        return True
    
    def process_webcam(self):
        """Live webcam feed"""
        print("\n📹 Starting webcam... (Press 'q' to quit)")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Webcam not available")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            result, annotated = self.process_frame(frame)
            
            cv2.imshow('Roulette Tracker - Live', annotated)
            
            if frame_count % 15 == 0 and result:
                print(f"Frame {frame_count}: " +
                      f"Angle={result['angle']:.1f}° " +
                      f"Moving={result['is_moving']}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Webcam closed")


def main():
    print("=" * 70)
    print("🎰 ADVANCED ROULETTE WHEEL TRACKING & PREDICTION SYSTEM v2.0")
    print("=" * 70)
    
    system = RouletteSystem()
    
    if len(sys.argv) < 2:
        print("\n📖 Usage:")
        print("   python main.py <image_or_video_path>")
        print("   python main.py --webcam")
        print("\n📋 Examples:")
        print("   python main.py roulette_wheel.jpg")
        print("   python main.py roulette_spin.mp4")
        print("   python main.py --webcam")
        return
    
    if sys.argv[1] == "--webcam":
        system.process_webcam()
    
    elif sys.argv[1].lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
        annotated = system.process_image(sys.argv[1])
        
        if annotated is not None:
            output_file = "output_roulette.jpg"
            cv2.imwrite(output_file, annotated)
            print(f"\n✅ Output saved: {output_file}")
            
            cv2.imshow('Roulette Prediction', annotated)
            print("\nPress any key to exit...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    elif sys.argv[1].lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        output_video = "output_roulette.mp4"
        system.process_video(sys.argv[1], output_video)
    
    else:
        print("❌ Unsupported file format")


if __name__ == "__main__":
    main()
