import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
from roulette_tracker import RouletteSystem

class RouletteGUI:
    """GUI Interface for Roulette Tracking System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎰 Roulette Ball Tracker v2.0")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")
        
        self.system = RouletteSystem()
        self.current_frame = None
        self.is_processing = False
        self.video_cap = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup user interface"""
        
        # Top Panel
        top_frame = tk.Frame(self.root, bg="#2d2d2d", height=80)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            top_frame,
            text="🎰 ROULETTE BALL TRACKING & PREDICTION SYSTEM",
            font=("Helvetica", 16, "bold"),
            fg="#00ff00",
            bg="#2d2d2d"
        )
        title_label.pack(pady=10)
        
        # Button Panel
        button_frame = tk.Frame(self.root, bg="#2d2d2d", height=60)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_image = tk.Button(
            button_frame,
            text="📷 Load Image",
            command=self.load_image,
            font=("Arial", 11),
            bg="#00aa00",
            fg="white",
            padx=15,
            pady=8
        )
        self.btn_image.pack(side=tk.LEFT, padx=5)
        
        self.btn_video = tk.Button(
            button_frame,
            text="🎬 Load Video",
            command=self.load_video,
            font=("Arial", 11),
            bg="#0088ff",
            fg="white",
            padx=15,
            pady=8
        )
        self.btn_video.pack(side=tk.LEFT, padx=5)
        
        self.btn_webcam = tk.Button(
            button_frame,
            text="📹 Live Webcam",
            command=self.start_webcam,
            font=("Arial", 11),
            bg="#ff8800",
            fg="white",
            padx=15,
            pady=8
        )
        self.btn_webcam.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(
            button_frame,
            text="⏹️  Stop",
            command=self.stop_processing,
            font=("Arial", 11),
            bg="#ff0000",
            fg="white",
            padx=15,
            pady=8,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.btn_save = tk.Button(
            button_frame,
            text="💾 Save Result",
            command=self.save_result,
            font=("Arial", 11),
            bg="#aa00aa",
            fg="white",
            padx=15,
            pady=8
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        # Main Content Area
        content_frame = tk.Frame(self.root, bg="#1e1e1e")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Image Display
        left_frame = tk.Frame(content_frame, bg="#2d2d2d")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(left_frame, text="📊 Detection Result", font=("Arial", 12, "bold"),
                fg="#00ff00", bg="#2d2d2d").pack(pady=5)
        
        self.canvas = tk.Canvas(left_frame, bg="black", width=700, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right: Info Panel
        right_frame = tk.Frame(content_frame, bg="#2d2d2d", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="📈 Analysis Info", font=("Arial", 12, "bold"),
                fg="#00ff00", bg="#2d2d2d").pack(pady=5)
        
        # Info text area
        self.info_text = tk.Text(right_frame, bg="#1e1e1e", fg="#00ff00",
                                font=("Courier", 10), height=15, width=40)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
        # Prediction Panel
        tk.Label(right_frame, text="🎯 TOP PREDICTIONS", font=("Arial", 11, "bold"),
                fg="#ffff00", bg="#2d2d2d").pack(pady=10)
        
        self.prediction_frame = tk.Frame(right_frame, bg="#1e1e1e")
        self.prediction_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             font=("Arial", 10), bg="#2d2d2d", fg="#00ff00")
        status_bar.pack(fill=tk.X, pady=5)
        
    def load_image(self):
        """Load and process image"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if file_path:
            self.status_var.set(f"Loading: {file_path}")
            self.root.update()
            
            thread = threading.Thread(target=self.process_image, args=(file_path,))
            thread.daemon = True
            thread.start()
    
    def process_image(self, path):
        """Process image in background"""
        try:
            image = cv2.imread(path)
            result, annotated = self.system.process_frame(image)
            
            # Convert to RGB for display
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            h, w = annotated_rgb.shape[:2]
            if w > 700:
                scale = 700 / w
                new_h = int(h * scale)
                annotated_rgb = cv2.resize(annotated_rgb, (700, new_h))
            
            self.current_frame = annotated_rgb
            
            # Display
            self.display_on_canvas(annotated_rgb)
            
            # Update info
            if result:
                self.update_info(result)
            
            self.status_var.set("✅ Image processed successfully")
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
    
    def load_video(self):
        """Load and process video"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.is_processing = True
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_image.config(state=tk.DISABLED)
            self.btn_video.config(state=tk.DISABLED)
            self.btn_webcam.config(state=tk.DISABLED)
            
            thread = threading.Thread(target=self.process_video, args=(file_path,))
            thread.daemon = True
            thread.start()
    
    def process_video(self, path):
        """Process video in background"""
        try:
            cap = cv2.VideoCapture(path)
            frame_count = 0
            
            while cap.isOpened() and self.is_processing:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                result, annotated = self.system.process_frame(frame)
                
                if frame_count % 5 == 0:  # Update every 5 frames
                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    
                    h, w = annotated_rgb.shape[:2]
                    if w > 700:
                        scale = 700 / w
                        new_h = int(h * scale)
                        annotated_rgb = cv2.resize(annotated_rgb, (700, new_h))
                    
                    self.current_frame = annotated_rgb
                    self.display_on_canvas(annotated_rgb)
                    
                    if result:
                        self.update_info(result, frame_count)
                    
                    self.status_var.set(f"▶️  Processing frame {frame_count}...")
                    self.root.update()
            
            cap.release()
            self.status_var.set("✅ Video processing complete")
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
        
        finally:
            self.is_processing = False
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_image.config(state=tk.NORMAL)
            self.btn_video.config(state=tk.NORMAL)
            self.btn_webcam.config(state=tk.NORMAL)
    
    def start_webcam(self):
        """Start webcam processing"""
        self.is_processing = True
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_image.config(state=tk.DISABLED)
        self.btn_video.config(state=tk.DISABLED)
        self.btn_webcam.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.process_webcam)
        thread.daemon = True
        thread.start()
    
    def process_webcam(self):
        """Process webcam in background"""
        try:
            cap = cv2.VideoCapture(0)
            frame_count = 0
            
            while cap.isOpened() and self.is_processing:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                result, annotated = self.system.process_frame(frame)
                
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                
                h, w = annotated_rgb.shape[:2]
                if w > 700:
                    scale = 700 / w
                    new_h = int(h * scale)
                    annotated_rgb = cv2.resize(annotated_rgb, (700, new_h))
                
                self.current_frame = annotated_rgb
                self.display_on_canvas(annotated_rgb)
                
                if result:
                    self.update_info(result, frame_count)
                
                self.status_var.set(f"📹 Live frame {frame_count}...")
                self.root.update()
            
            cap.release()
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
        
        finally:
            self.is_processing = False
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_image.config(state=tk.NORMAL)
            self.btn_video.config(state=tk.NORMAL)
            self.btn_webcam.config(state=tk.NORMAL)
    
    def display_on_canvas(self, cv_image):
        """Display OpenCV image on canvas"""
        h, w = cv_image.shape[:2]
        
        # Convert to PIL
        pil_image = Image.fromarray(cv_image)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        self.canvas.create_image(0, 0, image=tk_image, anchor=tk.NW)
        self.canvas.image = tk_image
    
    def update_info(self, result, frame_num=None):
        """Update info panel with results"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = []
        if frame_num:
            info.append(f"Frame: {frame_num}\n")
        
        if 'angle' in result:
            info.append(f"Angle: {result['angle']:.2f}°\n")
        
        if 'angular_velocity' in result:
            info.append(f"Angular Vel: {result['angular_velocity']:.2f}°/frame\n")
        
        if 'is_moving' in result:
            status = "🟢 MOVING" if result['is_moving'] else "🔴 STOPPED"
            info.append(f"Status: {status}\n")
        
        if 'ball_position' in result and result['ball_position']:
            x, y = result['ball_position']
            info.append(f"Ball Position: ({x}, {y})\n")
        
        self.info_text.insert(1.0, "".join(info))
        
        # Clear predictions
        for widget in self.prediction_frame.winfo_children():
            widget.destroy()
        
        # Add predictions
        if 'predictions' in result and result['predictions']:
            for i, (num, conf) in enumerate(result['predictions'][:5]):
                pred_text = f"#{num}: {conf*100:.1f}%"
                
                # Color based on confidence
                if conf > 0.7:
                    color = "#00ff00"
                elif conf > 0.4:
                    color = "#ffff00"
                else:
                    color = "#ff0000"
                
                label = tk.Label(
                    self.prediction_frame,
                    text=pred_text,
                    font=("Courier", 12, "bold"),
                    fg=color,
                    bg="#1e1e1e"
                )
                label.pack(pady=3)
                
                # Progress bar
                progress = ttk.Progressbar(
                    self.prediction_frame,
                    length=150,
                    mode='determinate',
                    value=conf*100
                )
                progress.pack(padx=10, pady=2)
        
        self.info_text.config(state=tk.DISABLED)
    
    def stop_processing(self):
        """Stop processing"""
        self.is_processing = False
        self.status_var.set("⏹️  Processing stopped")
    
    def save_result(self):
        """Save current result"""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No image to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            # Convert back to BGR
            bgr_image = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, bgr_image)
            messagebox.showinfo("Success", f"Image saved to {file_path}")
            self.status_var.set(f"💾 Saved: {file_path}")


def main():
    root = tk.Tk()
    gui = RouletteGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
