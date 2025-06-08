# Luxury Driver Monitoring System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PHP](https://img.shields.io/badge/PHP-7.4+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

The **Luxury Driver Monitoring System** is an advanced real-time driver monitoring solution designed to enhance road safety by detecting driver drowsiness and fatigue. By leveraging computer vision to analyze the Eye Aspect Ratio (EAR), the system provides a user-friendly interface to display live monitoring data, issue audio alerts, and store session information in a MySQL database. A complementary PHP-based web interface allows users to browse and analyze historical session data, making it ideal for fleet management and driver behavior analysis.

This project consists of two main components:
1. **Python Application**: A real-time driver monitoring system built with OpenCV, dlib, and PyQt5.
2. **PHP Web Interface**: A web dashboard for viewing and analyzing stored session data.

## Project Overview

### Purpose
The Luxury Driver Monitoring System aims to prevent road accidents by detecting driver drowsiness or fatigue in real-time. The Python application monitors the driver's state using facial landmark detection and EAR calculations, while the PHP web interface provides a platform to review historical data for analysis. The system is designed for applications in vehicle safety, fleet management, and driver training.

### Components and Workflow
- **Python Application**: Captures live video from a webcam, processes it using OpenCV and dlib to detect facial landmarks, calculates EAR, and classifies the driver's state as Asleep (UYUYOR), Drowsy (YORGUN), or Active (AKTIF). It logs data to a MySQL database and exports statistics to CSV.
- **PHP Web Interface**: Retrieves session data from the MySQL database, displays a list of sessions, and provides detailed views with statistics for each session.
- **Database Integration**: Both components share a MySQL database (`driver_monitoring`) with tables for sessions (`sessions`) and monitoring data (`driver_data`).

### Detailed Analysis

#### Python Application (driver_monitor.py)
The Python application is the core of the system, responsible for real-time monitoring and data collection.

**Key Features**:
- **Computer Vision**:
  - Uses OpenCV for video capture and grayscale conversion.
  - Employs dlib's frontal face detector and 68-point facial landmark predictor (`shape_predictor_68_face_landmarks.dat`) to locate facial features.
  - Calculates the Eye Aspect Ratio (EAR) using the `blinked` function, which measures distances between eye landmarks to determine eye closure.
  - Classifies driver state based on EAR thresholds:
    - **Asleep**: EAR < (sensitivity - 0.04) for 1.6 seconds, triggering an audio alert (`ses.mp3`).
    - **Drowsy**: EAR between (sensitivity - 0.04) and sensitivity for 6 frames.
    - **Active**: EAR > sensitivity.
- **Graphical User Interface (PyQt5)**:
  - Displays live video with face detection overlay and status text (e.g., "UYUYOR !!!", "YORGUN !", "AKTIF :)").
  - Features a drowsiness level progress bar, a real-time EAR graph (using Matplotlib), a statistics table, and an event log.
  - Includes control buttons (Start/Stop, Save Stats, Reset Log) and a sensitivity dropdown (Low: 0.27, Medium: 0.25, High: 0.23).
- **Audio Alerts**: Uses Pygame to play an alarm sound in a separate thread when the driver is asleep.
- **Data Storage**:
  - Connects to a MySQL database using `pymysql` to store session data (timestamp, status, EAR, event counts, durations).
  - Creates a new session on startup and associates all data with a unique `session_id`.
  - Exports statistics to `driver_stats.csv` when the Save Stats button is clicked.
- **State Management**:
  - Tracks event counts (sleep, drowsy, active) and durations.
  - Updates the GUI and database when the driver's state changes.
- **Error Handling**: Logs errors (e.g., camera failure, database issues) to the event log.

**Workflow**:
1. Initializes the webcam, loads the facial landmark predictor, and connects to the MySQL database.
2. Processes video frames every 30ms, detects faces, calculates EAR, and updates the driver's state.
3. Displays real-time data on the GUI (video, status, EAR graph, statistics).
4. Triggers audio alerts for sleep states and logs data to the database.
5. Allows users to start/stop monitoring, save stats, or reset logs.

#### PHP Web Interface (index.php)
The PHP web interface serves as a dashboard for reviewing stored session data.

**Key Features**:
- **Session List**:
  - Displays a table of all sessions with their `session_id` and `start_time`.
  - Provides links to view detailed data for each session.
- **Session Details**:
  - Shows a table with monitoring data (timestamp, status, EAR, event counts, durations) for a selected session.
  - Includes a summary section with total event counts and durations (sleep, drowsy, active).
- **Security**:
  - Uses prepared statements to prevent SQL injection.
  - Escapes output with `htmlspecialchars` to mitigate XSS attacks.
- **Responsive Design**:
  - Features a modern, dark-themed UI with the Roboto font.
  - Optimized for desktop and mobile devices with CSS media queries.
- **Multilingual Support**: Configured for Turkish characters using UTF-8 encoding.

**Workflow**:
1. Connects to the MySQL database (`driver_monitoring`) using `mysqli`.
2. Displays a session list if no `session_id` is provided.
3. Shows detailed data and statistics for a specific session when a `session_id` is selected.
4. Closes the database connection after rendering the page.

#### Database Structure
The system relies on a MySQL database (`driver_monitoring`) with two tables:
- **sessions**: Stores session metadata (`session_id`, `start_time`).
- **driver_data**: Stores monitoring data (`timestamp`, `status`, `ear`, `sleep_count`, `drowsy_count`, `active_count`, `sleep_duration`, `drowsy_duration`, `active_duration`, `session_id`).

The Python application writes data to these tables, while the PHP interface reads and displays the data.

## Features

### Python Application
- **Real-Time Drowsiness Detection**: Classifies driver states (Asleep, Drowsy, Active) based on EAR.
- **Graphical User Interface**:
  - Live video feed with face detection overlay.
  - Color-coded status display (green for active, yellow for drowsy, red for asleep).
  - Drowsiness level progress bar and real-time EAR graph.
  - Statistics table for event counts and durations.
  - Event log for system activities and errors.
  - Adjustable sensitivity settings (Low: 0.27, Medium: 0.25, High: 0.23).
- **Audio Alerts**: Plays `ses.mp3` when the driver is asleep, using a separate thread.
- **Data Storage**:
  - Stores data in a MySQL database and exports to `driver_stats.csv`.
  - Manages sessions with unique IDs.
- **Control Options**: Start/Stop monitoring, save stats, reset logs.

### PHP Web Interface
- **Session Browser**: Lists all sessions with start times and detail links.
- **Detailed Session View**: Displays timestamp, status, EAR, and event data.
- **Summary Statistics**: Shows total event counts and durations per session.
- **Responsive Design**: Dark-themed, mobile-friendly UI.
- **Security**: Prevents SQL injection and XSS attacks.

## Prerequisites

### Python Application
- **Python**: 3.8 or higher
- **Dependencies**:
  - `opencv-python`
  - `numpy`
  - `dlib`
  - `imutils`
  - `pygame`
  - `PyQt5`
  - `matplotlib`
  - `qdarkstyle`
  - `pymysql`
- **Pre-trained Model**: Download `shape_predictor_68_face_landmarks.dat` from [dlib's model repository](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) and place it in the project root.
- **Audio File**: `ses.mp3` in the project root.
- **Hardware**: Webcam or camera device.

### PHP Web Interface
- **PHP**: 7.4 or higher
- **Web Server**: Apache or Nginx
- **MySQL**: 8.0 or higher
- **Browser**: Modern browser (Chrome, Firefox, Safari, etc.)

### Database
- MySQL database named `driver_monitoring` with the following schema:

```sql
CREATE TABLE sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    start_time DATETIME NOT NULL
);

CREATE TABLE driver_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL,
    ear FLOAT NOT NULL,
    sleep_count INT DEFAULT 0,
    drowsy_count INT DEFAULT 0,
    active_count INT DEFAULT 0,
    sleep_duration INT DEFAULT 0,
    drowsy_duration INT DEFAULT 0,
    active_duration INT DEFAULT 0,
    session_id INT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
