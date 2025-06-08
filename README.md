# Luxury Driver Monitoring System

![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat-square&logo=python)
![PHP](https://img.shields.io/badge/PHP-7.4+-777BB4.svg?style=flat-square&logo=php)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=flat-square&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-4CAF50.svg?style=flat-square)

<p align="center">
  <img src="screenshots/logo.png" alt="Luxury Driver Monitoring System Logo" width="200"/>
</p>

<p align="center">
  <strong>An advanced real-time driver monitoring solution designed to enhance road safety by detecting drowsiness and fatigue, powered by computer vision and a sleek web interface.</strong>
</p>

---

## 🚗 Overview

The **Luxury Driver Monitoring System** is a state-of-the-art solution engineered to improve road safety by detecting driver drowsiness and fatigue in real-time. Leveraging cutting-edge computer vision techniques, the system analyzes the Eye Aspect Ratio (EAR) to classify driver states (Asleep, Drowsy, Active) and provides immediate audio alerts to prevent accidents. A sophisticated PyQt5-based GUI displays live monitoring data, while a MySQL database stores session details for analysis. A complementary PHP web interface offers a visually appealing dashboard to review historical data, making it ideal for fleet management, driver training, and safety research.

### 🛠️ Project Components
- **Python Application (`driver_monitor.py`)**: A real-time monitoring system built with OpenCV, dlib, and PyQt5, featuring live video, dynamic visualizations, and audio alerts.
- **PHP Web Interface (`index.php`)**: A responsive, dark-themed dashboard for browsing and analyzing session data stored in MySQL.
- **MySQL Database (`driver_monitoring`)**: Stores session metadata and monitoring data, enabling seamless integration between the application and web interface.

---

## 🌟 Features

### Python Application
- **Real-Time Drowsiness Detection**:
  - Uses OpenCV and dlib to detect facial landmarks and calculate EAR.
  - Classifies driver states:
    - **Asleep (UYUYOR)**: EAR below threshold for 1.6 seconds, triggering an audio alert.
    - **Drowsy (YORGUN)**: EAR indicating fatigue for 6 frames.
    - **Active (AKTIF)**: EAR above threshold, signaling alertness.
- **Elegant GUI (PyQt5)**:
  - **Live Video Feed**: Displays webcam footage with face detection overlays.
  - **Status Display**: Color-coded indicators (green: active, yellow: drowsy, red: asleep).
  - **Drowsiness Progress Bar**: Visualizes fatigue levels based on EAR.
  - **Real-Time EAR Graph**: Plots EAR over time using Matplotlib, with a threshold line.
  - **Statistics Table**: Tracks event counts and durations (sleep, drowsy, active).
  - **Event Log**: Records system activities and errors.
  - **Controls**: Start/Stop monitoring, Save Stats to CSV, Reset Logs, and adjustable sensitivity (Low: 0.27, Medium: 0.25, High: 0.23).
- **Audio Alerts**: Plays `ses.mp3` in a separate thread (via Pygame) when the driver is asleep.
- **Data Persistence**:
  - Stores session data (timestamp, status, EAR, event counts, durations) in a MySQL database.
  - Exports statistics to `driver_stats.csv` for offline analysis.
- **Session Management**: Automatically creates a unique session ID on startup.

### PHP Web Interface
- **Session Browser**: Lists all sessions with start times and links to detailed views.
- **Detailed Session View**:
  - Displays monitoring data (timestamp, status, EAR, event counts, durations) in a responsive table.
  - Provides summary statistics (total events and durations) for each session.
- **Modern Design**:
  - Dark-themed UI with the Roboto font, optimized for desktop and mobile.
  - Smooth animations and hover effects for an engaging user experience.
- **Security**:
  - Uses prepared statements to prevent SQL injection.
  - Escapes output with `htmlspecialchars` to mitigate XSS risks.
- **Multilingual Support**: Configured for Turkish characters (UTF-8).

---

## 🏗️ Architecture

The system integrates two components via a shared MySQL database (`driver_monitoring`):
- **Tables**:
  - `sessions`: Stores session metadata (`session_id`, `start_time`).
  - `driver_data`: Stores monitoring data (`timestamp`, `status`, `ear`, `sleep_count`, `drowsy_count`, `active_count`, `sleep_duration`, `drowsy_duration`, `active_duration`, `session_id`).
- **Workflow**:
  - The Python application captures and processes video, calculates EAR, and logs data to the database in real-time.
  - The PHP web interface retrieves and displays this data for historical analysis.

<p align="center">
  <img src="screenshots/architecture-diagram.png" alt="System Architecture" width="600"/>
</p>

---

## 📋 Prerequisites

### Python Application
- **Python**: 3.8 or higher
- **Dependencies**:
  ```bash
  opencv-python numpy dlib imutils pygame PyQt5 matplotlib qdarkstyle pymysql
