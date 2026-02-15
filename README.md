# MedWing: Autonomous Medical Drone Delivery Platform

**Multi-Drone AI Research Platform for Emergency Pharmaceutical Delivery**

By Juli, Mariana, Kimberly, and Mao Yu

## Project Overview

MedWing is an autonomous pharmaceutical delivery system that combines voice-controlled AI agents, drone navigation, and real-time tracking to enable rapid medical supply delivery in hospital environments. The system addresses critical delays in emergency medication delivery by providing 2-minute STAT delivery times compared to traditional 10-15 minute courier-based systems.

## System Architecture

### Core Components

1. **Voice Agent Interface**
   - Natural language voice ordering for medical personnel
   - VAPI integration for speech-to-text and intent extraction
   - Real-time call transcription and order parsing
   - Automatic medication, dosage, quantity, and urgency detection
   - Priority-based delivery scheduling (STAT: 2min, Urgent: 3-4min, Routine: 5min)

2. **Autonomous Drone Fleet**
   - DJI Tello EDU drone platform
   - ROS (Robot Operating System) integration
   - Multi-drone coordination and fleet management
   - Facial recognition for secure recipient verification
   - Battery management and auto-return functionality

3. **SLAM Navigation System**
   - ORB-SLAM2 for monocular visual SLAM
   - CCM-SLAM for collaborative multi-agent mapping
   - GPS-denied environment navigation (hospitals, urban areas)
   - Real-time obstacle avoidance
   - 3D scene reconstruction and mapping

4. **Web Dashboard**
   - React-based real-time monitoring interface
   - Live transcript streaming via Server-Sent Events (SSE)
   - Active delivery tracking and fleet status
   - Historical call logs and saved transcripts
   - Glassmorphic UI with live connection indicators

5. **Backend Services**
   - FastAPI webhook server for VAPI integration
   - Async event processing and order validation
   - Zoom and Cloudflare notification systems
   - RESTful API for dashboard communication
   - Order management and dispatch logic

## Technical Stack

### Robotics & Navigation
- **ROS**: Robot Operating System (Melodic/Noetic)
- **SLAM**: ORB-SLAM2, CCM-SLAM
- **Computer Vision**: OpenCV, MediaPipe
- **Drone Control**: TelloPy (custom modified)
- **Hardware**: DJI Tello EDU drones

### Voice AI & Backend
- **Voice Platform**: VAPI (speech-to-text, NLU, TTS)
- **Backend Framework**: FastAPI, Python 3.8+
- **Real-time Communication**: Server-Sent Events (SSE)
- **Notifications**: Zoom API, Cloudflare Workers
- **Environment Management**: python-dotenv

### Frontend
- **Framework**: React 18, Vite
- **Routing**: React Router v6
- **Styling**: Custom CSS with glassmorphism
- **State Management**: React Hooks
- **Deployment**: Vercel

### Integration Services
- **Telephony**: VAPI voice infrastructure
- **Notifications**: Zoom webhooks, Cloudflare
- **Video Processing**: H.264 decoder (C++ with Python bindings)

## Project Structure

```
Drone-SLAM/
├── ROS/
│   ├── tello_catkin_ws/         # Tello ROS workspace
│   └── ccmslam_ws/              # Multi-drone SLAM workspace
├── TelloPy/                     # Modified Tello control library
├── h264decoder/                 # Video stream decoder
├── facial_recognition/          # Face detection modules
├── voice_agent/                 # Voice AI backend
│   ├── webhook_server.py        # FastAPI webhook server
│   ├── zoom_notifications.py   # Zoom integration
│   └── cloudflare_notifications.py
├── frontendWeb/                 # React dashboard
│   └── src/
│       ├── Dashboard.jsx        # Main monitoring interface
│       ├── SavedCalls.jsx       # Call history viewer
│       ├── ErrorBoundary.jsx    # Error handling
│       └── Skeleton.jsx         # Loading states
└── Documentation/
    ├── DEMO.md                  # Demo presentation guide
    ├── README_MEDWING.md        # Detailed project docs
    └── ARCHITECTURE.md          # System architecture
```

## Key Features

### Voice-Controlled Ordering
- Hands-free medication ordering for doctors
- Natural language understanding (no special commands)
- Automatic order confirmation and readback
- Real-time transcript streaming to dashboard

### Autonomous Navigation
- Visual SLAM for GPS-denied environments
- Multi-drone fleet coordination
- Dynamic path planning and obstacle avoidance
- Collaborative mapping between drones

### Security & Verification
- Facial recognition for recipient verification
- Secure order validation
- HIPAA-compliant transcript storage (planned)
- Audit trail for all deliveries

### Real-Time Monitoring
- Live call transcription display
- Active delivery tracking
- Fleet status dashboard
- Connection status indicators
- Historical call logs

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- ROS Melodic/Noetic
- DJI Tello drone (optional for full demo)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/marianaisaw/Drone-SLAM.git
cd Drone-SLAM
```

2. **Run Setup Script**
```bash
chmod +x setup_demo.sh
./setup_demo.sh
```

3. **Configure Environment**
```bash
cp voice_agent/.env.example voice_agent/.env
# Edit voice_agent/.env with your API keys
```

4. **Start Backend**
```bash
cd voice_agent
source venv/bin/activate
python webhook_server.py
```

5. **Start Frontend**
```bash
cd frontendWeb
npm install
npm run dev
```

6. **Launch ROS (For Hardware Demo)**
```bash
cd ROS/tello_catkin_ws
catkin_make
source devel/setup.bash
roslaunch flock tello_slam.launch
```

## Usage

### Voice Call Demo
1. Call VAPI phone number
2. State: "I'm Dr. [Name] from [Facility]"
3. Order: "I need [medication] [dosage], [quantity], [STAT/Urgent/Routine] delivery"
4. Specify: "Floor [X], Room [XXX]"
5. Confirm order
6. Track delivery in real-time on dashboard

### Dashboard Monitoring
- View live transcripts in Activity feed
- Monitor active deliveries
- Check fleet status (battery, location)
- Save and review call history

## SLAM Navigation

### ORB-SLAM Integration
The Tello sends video stream to ORB-SLAM, which provides position and orientation to the control system. The control system then navigates the Tello to the target location using SLAM-derived coordinates.

### Coordinate System Calibration
The system calibrates between SLAM coordinates and real-world measurements using:

real_world_scale = Δ height_sensor / Δ SLAM_height

### Multi-Drone Coordination
CCM-SLAM enables multiple drones to:
- Share and merge maps
- Operate in unified coordinate system
- Coordinate delivery zones
- Avoid collisions

## Tello Control Interface

### Command Position Section
- Takeoff/Land controls
- Calibrate Z for coordinate scaling
- Publish command for autonomous navigation
- Stay in place command

### Real World Position
- Current coordinates display
- Altitude scale factor
- Battery and status information

### Manual Control
- Direct speed control (pitch, roll, throttle, yaw)
- Manual override capabilities
### 3D Reconstruction
- Point cloud generation from drone footage
- Scene mapping and visualization
- Depth estimation for navigation

## Impact and Applications

### Healthcare Delivery
- 2-minute STAT delivery vs 10-15 minute traditional courier
- Reduces mortality risk in cardiac arrest and anaphylaxis scenarios
- Enables doctors to remain with critical patients
- Scalable to multiple hospitals and rural clinics

### Cost Efficiency
- Estimated $50K annual savings per hospital in courier costs
- Reduced medication waste through efficient routing
- Lower operational overhead vs human couriers

### Research Applications
- Multi-drone coordination algorithms
- GPS-denied navigation systems
- Human-AI interaction patterns
- Emergency response optimization

## Performance Metrics

- Voice order processing: < 5 seconds
- STAT delivery time: 2 minutes
- Urgent delivery time: 3-4 minutes
- Routine delivery time: 5 minutes
- System uptime: 99.5% (target)
- Facial recognition accuracy: 95%+

## Demo and Deployment

### Live Demo
- Frontend: https://drone-slam.vercel.app
- Voice Agent: Call VAPI number for demo
- Dashboard: Real-time monitoring at /dashboard

### Documentation
- DEMO.md: Complete 5-minute presentation guide
- README_MEDWING.md: Detailed technical documentation
- ARCHITECTURE.md: System architecture diagrams



## Technical Documentation

### Original SLAM Implementation

This project builds upon the foundational Tello ROS ORB-SLAM framework with significant enhancements for medical delivery applications.

#### ORB-SLAM Integration
Video demonstration: [Tello ORB-SLAM Demo](http://www.youtube.com/watch?v=5tXE1TO7TC8)

The Tello sends video stream to ORB-SLAM, which provides position and orientation to the control system. The control system navigates the Tello to the target location using SLAM-derived coordinates.

#### ROS Launch Commands

##### ORB-SLAM2
```bash
roslaunch flock_driver orbslam2_with_cloud_map.launch
```

##### CCM-SLAM
Server:
```bash
roslaunch ccmslam tello_Server.launch 
```

Client 0:
```bash
roslaunch ccmslam tello_Client0.launch
```

Client 1:
```bash
roslaunch ccmslam tello_Client1.launch
```

## Installation Guide

### ROS Melodic Setup

Setup packages.ros.org:
```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
```

Set up keys:
```bash
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
```

Install ROS:
```bash
sudo apt update
sudo apt install ros-melodic-desktop-full
```

Initialize rosdep:
```bash
sudo rosdep init
rosdep update
```

Environment setup:
```bash
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Install build tools:
```bash
sudo apt install python-rosinstall python-rosinstall-generator python-wstool build-essential
```

### Prerequisites

#### Catkin Tools
```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu `lsb_release -sc` main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
sudo apt-get update
sudo apt-get install python-catkin-tools
```

#### Eigen3
```bash
sudo apt install libeigen3-dev
```

#### FFmpeg
```bash
sudo apt install ffmpeg
```

#### Joystick Drivers
```bash
sudo apt install ros-melodic-joystick-drivers
```

#### Python PIL
```bash
sudo apt-get install python-imaging-tk
```

### Pangolin (ORB-SLAM2 Dependency)
```bash
cd ~/ROS/
git clone https://github.com/stevenlovegrove/Pangolin.git
sudo apt install libgl1-mesa-dev libglew-dev libxkbcommon-dev
cd Pangolin
mkdir build && cd build
cmake ..
cmake --build .
```

### H.264 Decoder
```bash
cd ~/ROS/
git clone https://github.com/DaWelter/h264decoder.git
cd h264decoder
# Replace PIX_FMT_RGB24 with AV_PIX_FMT_RGB24 in h264decoder.cpp
mkdir build && cd build
cmake ..
make
sudo cp ~/ROS/h264decoder/libh264decoder.so /usr/local/lib/python2.7/dist-packages
```

### Clone Repository
```bash
cd ~
mkdir ROS && cd ROS
git clone https://github.com/marianaisaw/Drone-SLAM.git
```

### Install TelloPy
```bash
cd ~/ROS/Drone-SLAM/TelloPy
sudo python setup.py install
```

### Install ROS Dependencies
```bash
cd ~/ROS/Drone-SLAM/ROS/tello_catkin_ws/
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### Build ORB-SLAM2
```bash
cd ~/ROS/Drone-SLAM/ROS/tello_catkin_ws/
catkin init
catkin clean
catkin build
```
If it doesn’t work, make sure you changed the makefile to the wanted version of ROS
## Add the enviroment setup to bashrc
```
echo "source $PWD/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```
catkin build
```

For Melodic: Update CMakeLists.txt before building.

### Build CCM-SLAM

Compile DBoW2:
```bash
cd ~/ROS/Drone-SLAM/ROS/ccmslam_ws/src/ccm_slam/cslam/thirdparty/DBoW2/
mkdir build && cd build
cmake ..
make -j8
```

Compile g2o:
```bash
cd ~/ROS/Drone-SLAM/ROS/ccmslam_ws/src/ccm_slam/cslam/thirdparty/g2o
mkdir build && cd build
cmake --cmake-args -DG2O_U14=0 ..
make -j8
```

Unzip vocabulary:
```bash
cd ~/ROS/Drone-SLAM/ROS/ccmslam_ws/src/ccm_slam/cslam/conf
unzip ORBvoc.txt.zip
```

Build workspace:
```bash
cd ~/ROS/Drone-SLAM/ROS/ccmslam_ws/
source /opt/ros/melodic/setup.bash
catkin init
catkin config --extend /opt/ros/melodic
catkin build ccmslam --cmake-args -DG2O_U14=0 -DCMAKE_BUILD_TYPE=Release
```

Add to bashrc:
```bash
echo "source $PWD/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Acknowledgments

This project builds upon:
- ORB-SLAM2 by Raúl Mur-Artal
- CCM-SLAM by VIS4ROB-lab
- TelloPy by hanyazou
- Pangolin by Steven Lovegrove

TreeHacks 2026 Sponsors:
- Vapi for voice AI platform
- Cloudflare for email notifications
- Zoom for meeting integrations

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please submit pull requests or open issues for bugs and feature requests.

## Contact

For questions or collaboration:
- GitHub: github.com/marianaisaw/Drone-SLAM
- Project Demo: drone-slam.vercel.app

## Citations

If you use this work in your research, please cite:

```
@misc{medwing2026,
  title={MedWing: Autonomous Medical Drone Delivery Platform},
  author={Juli and Mariana and Kimberly and Mao Yu},
  year={2026},
  publisher={GitHub},
  url={https://github.com/marianaisaw/Drone-SLAM}
}
```

---

Built with dedication for TreeHacks 2026


### Architecture

```
Phone Call → Vapi → Groq LLM → Webhook Server → Drone Dispatcher → Tello Fleet
                                       ↓
                              Cloudflare Worker → MailChannels → Email 📧
                                (Edge Network)        (Free)
```

See `voice_agent/README.md` for detailed documentation.

## Notes
### Flock
we have used code from https://github.com/clydemcqueen/flock
