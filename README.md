# 🚀 ROI-Based Intelligent Video Analytics System

> A scalable real-time video analytics platform built using **YOLOv7**, **YOLOv7 Segmentation**, **RabbitMQ**, **Redis**, **OpenCV**, and **Python** for intelligent surveillance and safety monitoring.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![YOLOv7](https://img.shields.io/badge/YOLOv7-Detection-green)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-MessageBroker-orange)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![OpenCV](https://img.shields.io/badge/OpenCV-ComputerVision-blueviolet)

---

# 📖 Overview

This project is a **Region of Interest (ROI) Based Intelligent Video Analytics System** designed to process multiple surveillance camera streams in real-time.

The system leverages **RabbitMQ** for distributed communication, **Redis** for configuration management and event storage, **YOLOv7 Detection** for object detection, and **YOLOv7 Segmentation** for person segmentation.

Instead of processing every detected object, the system applies **ROI validation**, ensuring that only detections occurring within predefined regions are considered valid and stored.

This significantly reduces:

- False detections
- Storage requirements
- Unnecessary event processing
- System overhead

---

# 🎯 Problem Statement

Traditional surveillance systems process every detection regardless of its location.

This often results in:

❌ High computational load

❌ Unnecessary event generation

❌ Increased storage usage

❌ False alarms

To overcome these challenges, this project introduces an **ROI-Based Detection Pipeline** where only objects detected within user-defined regions are processed and stored.

---

# ✨ Key Features

✅ Multi-camera video processing

✅ Multi-threaded architecture

✅ Redis-based configuration caching

✅ RabbitMQ producer-consumer architecture

✅ YOLOv7 object detection

✅ YOLOv7 person segmentation

✅ ROI-based event filtering

✅ Base64 frame transmission

✅ Distributed processing pipeline

✅ Real-time event monitoring

---

# 🛠️ Technology Stack

| Technology | Purpose |
|------------|----------|
| Python | Core Development |
| OpenCV | Video Processing |
| YOLOv7 | Object Detection |
| YOLOv7 Segmentation | Person Segmentation |
| RabbitMQ | Message Broker |
| Redis | Data Storage & Caching |
| JSON | Camera Configuration |
| Base64 | Frame Serialization |
| Multi-threading | Parallel Camera Processing |

---

# 🏗️ System Architecture

```text
                    Camera Configuration (JSON)
                                 |
                                 v
                           Redis Cache
                                 |
                                 v
                          Frame Producer
                                 |
                                 v
                        RabbitMQ Exchange
                                 |
              ---------------------------------------
              |                                     |
              v                                     v

       Person Queue                      Non-Person Queue
              |                                     |
              v                                     v

  YOLOv7 Segmentation                    YOLOv7 Detection
              |                                     |
              ------------ Detection Exchange -------
                                 |
      --------------------------------------------------------
      |                         |                           |
      v                         v                           v

 Vehicle Queue          Fire-Smoke Queue         Helmet-Jacket Queue
      |                         |                           |
      v                         v                           v

 ROI Validation         ROI Validation            ROI Validation
      |                         |                           |
      v                         v                           v

    Redis                     Redis                      Redis
```

---

# 🔄 Project Workflow

## Step 1: Camera Configuration

The system starts by loading camera information from a JSON configuration file.

Each camera entry contains:

- Camera ID
- Camera IP Address
- Video Path / RTSP Stream
- Labels
- Additional Metadata

### Example

```json
{
  "camera_1": {
    "ip_address": "192.168.1.100",
    "video_path": "video1.mp4",
    "labels": ["car", "bike"]
  }
}
```

---

## Step 2: Redis Configuration Management

When the application starts:

### Check Redis

```text
Configuration Available?
        |
   +----+----+
   |         |
  YES       NO
   |         |
Load      Read JSON
Redis         |
              v
        Store in Redis
              |
              v
        Load Configuration
```

### Benefits

- Faster startup
- Reduced file access
- Centralized configuration management

---

## Step 3: Multi-Camera Processing

The producer dynamically distributes cameras across processors and threads.

### Example

4 Cameras

```text
Processor 1
├── Thread 1 → Camera 1
└── Thread 2 → Camera 2

Processor 2
├── Thread 1 → Camera 3
└── Thread 2 → Camera 4
```

Each thread continuously captures frames from its assigned camera.

---

## Step 4: Frame Encoding & Publishing

Captured frames are encoded using Base64 before transmission.

```text
Camera Frame
      |
      v
Base64 Encoding
      |
      v
RabbitMQ Exchange
```

### Why Base64?

- Easy serialization
- Broker-friendly transmission
- Cross-service compatibility

---

## Step 5: Queue Separation

Frames are divided into two primary queues.

### 👤 Person Queue

Contains:

- Person-related frames

Purpose:

- Person Segmentation

---

### 🚗 Non-Person Queue

Contains:

- Car
- Bike
- Helmet
- Jacket
- Fire
- Smoke

Purpose:

- Object Detection

---

# 🤖 YOLOv7 Detection Pipeline

Frames received from the Non-Person Queue are:

1. Decoded
2. Sent to YOLOv7 Detection
3. Processed for object detection

### Supported Detection Classes

| Class |
|---------|
| Person |
| Car |
| Bike |
| Helmet |
| Jacket |
| Fire |
| Smoke |

### Detection Output

- Bounding Box Coordinates
- Confidence Score
- Class Label

---

# 👤 YOLOv7 Segmentation Pipeline

Frames received from the Person Queue are:

1. Decoded
2. Sent to YOLOv7 Segmentation
3. Person masks generated

### Output

- Person Mask
- Segmented Person Region
- Real-time Visualization

---

# 🔀 Detection Routing

Detection results are routed to another RabbitMQ Exchange.

The exchange creates dedicated queues based on detection type.

---

## 🚗 Vehicle Queue

Processes:

- Car
- Bike

Use Cases:

- Vehicle Monitoring
- Traffic Analytics
- Restricted Zone Monitoring

---

## 🔥 Fire-Smoke Queue

Processes:

- Fire
- Smoke

Use Cases:

- Fire Detection
- Industrial Safety Monitoring
- Emergency Alerts

---

## 🦺 Helmet-Jacket Queue

Processes:

- Helmet
- Jacket

Use Cases:

- PPE Compliance Monitoring
- Workplace Safety

---

# 📍 ROI Validation

ROI (Region of Interest) filtering is applied before storing detections.

### Workflow

```text
Object Detected
       |
       v
Check ROI
       |
   +---+---+
   |       |
 Inside   Outside
 ROI      ROI
   |       |
   v       v

 Save    Ignore
 Event
```

Only detections inside the ROI are considered valid.

### Advantages

✅ Reduced False Positives

✅ Focused Event Monitoring

✅ Lower Storage Usage

✅ Improved Analytics Accuracy

---

# 💾 Redis Event Storage

Validated detections are stored in Redis.

### Example Keys

```text
vehicle_frames
fire_smoke_frames
helmet_jacket_frames
person_frames
```

### Stored Information

- Camera ID
- Timestamp
- Detection Class
- Bounding Box Coordinates
- Confidence Score
- ROI Status
- Encoded Frame

---

# 📊 Supported Analytics

| Analytics Module | Description |
|------------------|-------------|
| Vehicle Monitoring | Car & Bike Detection |
| Fire Monitoring | Fire & Smoke Detection |
| PPE Monitoring | Helmet & Jacket Detection |
| Human Monitoring | Person Segmentation |
| ROI Analytics | Zone-Based Event Detection |

---

# 📸 Sample Outputs

## System Architecture

```markdown
![Architecture](assets/architecture.png)
```

## Vehicle Detection

```markdown
![Vehicle Detection](assets/vehicle_detection.png)
```

## Fire & Smoke Detection

```markdown
![Fire Detection](assets/fire_detection.png)
```

## Person Segmentation

```markdown
![Segmentation](assets/person_segmentation.png)
```

## ROI Validation

```markdown
![ROI](assets/roi_validation.png)
```

---

# 📂 Project Structure

```text
project/
│
├── config/
│   ├── config.py
│   └── camera_config.json
│
├── producers/
│   └── frame_producer.py
│
├── consumers/
│   ├── detection_consumer.py
│   ├── segmentation_consumer.py
│   └── roi_consumer.py
│
├── models/
│   ├── yolov7_detection.pt
│   └── yolov7_segmentation.pt
│
├── assets/
│   ├── architecture.png
│   ├── vehicle_detection.png
│   ├── fire_detection.png
│   ├── person_segmentation.png
│   └── roi_validation.png
│
├── README.md
│
└── requirements.txt
```

---

# 🚀 Future Enhancements

- Multi-Object Tracking (DeepSORT)
- Vehicle Counting
- Intrusion Detection
- Email Notifications
- SMS Alerts
- Dashboard Visualization
- Grafana Integration
- Docker Deployment
- Kubernetes Deployment
- Cloud Deployment (AWS/Azure/GCP)

---

# 🏆 Project Achievements

- Built a distributed real-time video analytics pipeline.
- Implemented YOLOv7-based detection and segmentation.
- Developed ROI-aware event filtering logic.
- Integrated Redis for high-speed event storage.
- Designed RabbitMQ-based asynchronous communication.
- Enabled scalable processing of multiple camera streams.

---

# 👨‍💻 Author

**Sai Prasanthi N**

AI/ML Engineer | Computer Vision Engineer

### Skills Demonstrated

🐍 Python

👁️ OpenCV

🤖 YOLOv7

🧠 Deep Learning

📨 RabbitMQ

⚡ Redis

🎯 Computer Vision

🔄 Multi-threading

📹 Real-Time Video Analytics

---

⭐ If you found this project useful, consider giving it a star on GitHub.
