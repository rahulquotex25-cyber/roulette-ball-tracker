"""
Quick start guide for Roulette Ball Tracking System
"""

print("""

╔═══════════════════════════════════════════════════════════════╗
║        🎰 ROULETTE BALL TRACKING & PREDICTION SYSTEM         ║
║                      QUICK START GUIDE                        ║
╚═══════════════════════════════════════════════════════════════╝

📋 INSTALLATION STEPS:

1️⃣  Install Python 3.7 or higher
   → https://www.python.org/downloads/

2️⃣  Install required packages:
   $ pip install -r requirements.txt

3️⃣  Prepare your input (image or video file)
   → Place roulette wheel image/video in project folder

4️⃣  Run the system:
   $ python main.py your_image.jpg
   $ python main.py your_video.mp4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK EXAMPLES:

Example 1: Process an image
   $ python main.py roulette_wheel.jpg
   
   Output:
   ✓ Detects wheel
   ✓ Finds ball
   ✓ Predicts landing number
   ✓ Saves annotated image as "output_prediction.jpg"

Example 2: Process a video
   $ python main.py casino_spin.mp4
   
   Output:
   ✓ Processes every frame
   ✓ Tracks ball movement
   ✓ Shows live predictions
   ✓ Saves result as "output_prediction.mp4"

Example 3: Interactive examples
   $ python examples.py
   
   Menu with 5 different usage scenarios

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 UNDERSTANDING THE OUTPUT:

Console Output:
  ✓ Wheel detected at (512, 384) with radius 280px
    → Wheel center position and size
  
  • Angle: 145.32°
    → Current ball angle from wheel center
  
  • 🎯 PREDICTED NUMBER: 17
    → Most likely landing pocket
  
  • Confidence: 85.3%
    → How confident is the prediction (0-100%)
  
  • Top 5 Predictions:
    1. Number 17: 85.3%
    2. Number 34: 68.2%
    → Ranked list of possible numbers

Visual Output (output_prediction.jpg):
  🔵 Cyan circle → Wheel boundary
  🟡 Yellow circle → Ball position
  ➡️ Cyan arrow → Ball velocity
  🟢 Green line → Ball trajectory
  📝 Text overlay → Predictions and stats

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  CUSTOMIZATION:

Adjust detection sensitivity:
  File: src/wheel_detector.py
  - Modify minRadius, maxRadius for wheel size
  - Adjust param1, param2 for detection sensitivity

Change ball color range:
  File: src/ball_tracker.py
  - Modify lower_ball, upper_ball for different lighting

Adjust prediction physics:
  File: src/number_predictor.py
  - Change friction value (0.95-0.99)
  - Modify max_frames for simulation length

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 TROUBLESHOOTING:

Problem: "Wheel not detected"
Solution:
  ✓ Ensure wheel is clearly visible in image
  ✓ Try adjusting wheel radius range in wheel_detector.py
  ✓ Check lighting - wheel should be well-lit

Problem: "Ball not detected"
Solution:
  ✓ Verify ball color is white/cream
  ✓ Adjust HSV range in ball_tracker.py
  ✓ Increase image contrast/brightness

Problem: "Import errors"
Solution:
  ✓ Install all packages: pip install -r requirements.txt
  ✓ Check Python version: python --version (3.7+)
  ✓ Verify you're in the project directory

Problem: Low prediction confidence
Solution:
  ✓ Use images with clear ball motion
  ✓ Ensure multiple frames show ball movement
  ✓ Video works better than single images

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 PROJECT STRUCTURE:

roulette-ball-tracker/
├── main.py              ← Run this file
├── examples.py          ← Example usage
├── requirements.txt     ← Install with: pip install -r requirements.txt
├── README.md            ← Full documentation
├── QUICKSTART.md        ← This file
└── src/
    ├── wheel_detector.py    ← Detects roulette wheel
    ├── ball_tracker.py      ← Tracks ball position
    ├── number_predictor.py  ← Predicts landing number
    └── visualizer.py        ← Creates output visualizations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:

  ✓ Automatic wheel detection (Hough Circle Transform)
  ✓ Real-time ball tracking (color-based detection)
  ✓ Angle calculation (polar coordinates)
  ✓ Physics-based prediction (deceleration model)
  ✓ Trajectory visualization (fade effect)
  ✓ Confidence scoring (0-100%)
  ✓ Video support (frame-by-frame processing)
  ✓ Live camera input (webcam support)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  LEGAL DISCLAIMER:

  ⚖️  Educational purposes only
  🎲 NOT for actual casino gambling or cheating
  🛑 Violates gaming laws in most jurisdictions
  📚 For research and learning only
  ✅ Use responsibly and legally

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS FOR BEST RESULTS:

  1. Use clear, well-lit images/videos
  2. Ensure ball and wheel are visible
  3. Video works better than static images
  4. Multiple frames improve accuracy
  5. Consistent lighting produces better results
  6. Clear contrast between ball and background
  7. Wheel should be mostly stationary
  8. Frame rate affects tracking quality (30fps+ recommended)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 NEED HELP?

  📖 Read full documentation in README.md
  🔍 Check examples.py for sample usage
  🐛 Review console output for error messages
  💬 Open issue on GitHub

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to get started? Run this command:

  $ python main.py your_roulette_image.jpg

Good luck! 🎯

""")
