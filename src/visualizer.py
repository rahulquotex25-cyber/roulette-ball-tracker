import cv2
import numpy as np

class RouletteVisualizer:
    """Visualizes tracking results on images"""
    
    def __init__(self):
        self.colors = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'white': (255, 255, 255),
            'cyan': (255, 255, 0)
        }
    
    def draw_wheel(self, image, wheel_center, wheel_radius):
        """Draw wheel boundaries"""
        if wheel_center is None or wheel_radius is None:
            return image
        
        cv2.circle(image, wheel_center, wheel_radius, self.colors['cyan'], 2)
        cv2.circle(image, wheel_center, 5, self.colors['red'], -1)
        
        return image
    
    def draw_ball(self, image, ball_position, ball_radius, moving=False):
        """Draw ball position"""
        if ball_position is None or ball_radius is None:
            return image
        
        color = self.colors['yellow'] if moving else self.colors['green']
        cv2.circle(image, ball_position, ball_radius, color, 2)
        cv2.circle(image, ball_position, 3, color, -1)
        
        return image
    
    def draw_trajectory(self, image, trajectory):
        """Draw ball trajectory"""
        if len(trajectory) < 2:
            return image
        
        for i in range(1, len(trajectory)):
            pt1 = trajectory[i-1]
            pt2 = trajectory[i]
            alpha = i / len(trajectory)  # Fade effect
            
            color = (int(255 * alpha), int(255 * (1 - alpha)), 100)
            cv2.line(image, pt1, pt2, color, 1)
        
        return image
    
    def draw_velocity_vector(self, image, ball_position, velocity, scale=2):
        """Draw velocity vector"""
        if ball_position is None or velocity is None:
            return image
        
        vx, vy = velocity
        end_point = (
            int(ball_position[0] + vx * scale),
            int(ball_position[1] + vy * scale)
        )
        
        cv2.arrowedLine(image, ball_position, end_point, self.colors['cyan'], 2)
        
        return image
    
    def draw_predictions(self, image, predictions, ball_position):
        """Draw predicted numbers"""
        if not predictions or ball_position is None:
            return image
        
        y_offset = 30
        cv2.putText(image, "PREDICTIONS:", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['yellow'], 2)
        
        for i, (number, confidence) in enumerate(predictions[:5]):
            text = f"#{number}: {confidence*100:.1f}%"
            y_pos = y_offset + 30 * (i + 1)
            
            # Color based on confidence
            if confidence > 0.6:
                color = self.colors['green']
            elif confidence > 0.3:
                color = self.colors['yellow']
            else:
                color = self.colors['red']
            
            cv2.putText(image, text, (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return image
    
    def draw_info(self, image, angle=None, velocity=None, moving=False):
        """Draw tracking information"""
        info = []
        
        if angle is not None:
            info.append(f"Angle: {angle:.1f}°")
        
        if velocity is not None:
            speed = np.sqrt(velocity[0]**2 + velocity[1]**2)
            info.append(f"Speed: {speed:.2f}px/frame")
        
        status = "MOVING" if moving else "STOPPED"
        info.append(f"Status: {status}")
        
        h, w = image.shape[:2]
        y_offset = h - 80
        
        for i, text in enumerate(info):
            cv2.putText(image, text, (10, y_offset + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['white'], 2)
        
        return image
    
    def annotate_frame(self, image, wheel_center=None, wheel_radius=None, 
                      ball_position=None, ball_radius=None, trajectory=None,
                      velocity=None, angle=None, predictions=None, moving=False):
        """Draw all annotations on frame"""
        
        result = image.copy()
        result = self.draw_wheel(result, wheel_center, wheel_radius)
        result = self.draw_trajectory(result, trajectory or [])
        result = self.draw_ball(result, ball_position, ball_radius, moving)
        result = self.draw_velocity_vector(result, ball_position, velocity)
        result = self.draw_predictions(result, predictions or [], ball_position)
        result = self.draw_info(result, angle, velocity, moving)
        
        return result
