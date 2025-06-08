import sys
import cv2
import numpy as np
import dlib
from imutils import face_utils
import pygame
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QTextEdit, QComboBox
)
from PyQt5.QtCore import QTimer, QDateTime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import qdarkstyle
import pymysql
import warnings
import csv

# إخفاء تحذير sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning)

# تهيئة Pygame للصوت
pygame.mixer.init()

# دالة تشغيل صوت التنبيه
def play_alarm_sound(window):
    global alarm_playing
    alarm_playing = True
    try:
        pygame.mixer.music.load("ses.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        print(f"Error playing sound: {e}")
        window.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Error playing sound: {e}")
    finally:
        alarm_playing = False
        window.sound_finished = True

# دوال مساعدة
def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    return ratio

# كلاس الواجهة الرسومية
class DriverMonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luxury Driver Monitoring System")
        self.setGeometry(100, 100, 1400, 800)

        # تهيئة الكاميرا
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            sys.exit(1)
        self.detector = dlib.get_frontal_face_detector()
        try:
            self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        except Exception as e:
            print(f"Error loading shape predictor: {e}")
            sys.exit(1)

        # متغيرات الحالة
        self.sleep = 0
        self.drowsy = 0
        self.active = 0
        self.status = "Waiting..."
        self.color = (255, 255, 255)
        self.alarm_playing = False
        self.sound_finished = True
        self.ear_history = []
        self.sleep_count = 0
        self.drowsy_count = 0
        self.active_count = 0
        self.sleep_duration = 0
        self.drowsy_duration = 0
        self.active_duration = 0
        self.last_state = None
        self.last_state_time = QDateTime.currentDateTime()
        self.sensitivity = 0.25
        self.is_running = True
        self.last_sleep_recorded = False
        self.last_drowsy_recorded = False
        self.sleep_start_time = None
        self.current_ear = 0.0
        self.session_id = None  # معرف الجلسة

        # تهيئة سجل أحداث مؤقت كقائمة
        self.temp_log = []

        # الاتصال بقاعدة البيانات
        self.db_connection = self.connect_to_db()
        if self.db_connection:
            self.temp_log.append(f"[{QDateTime.currentDateTime().toString()}] Connected to MySQL database.")
            # إنشاء جلسة جديدة
            self.create_session()
        else:
            self.temp_log.append(f"[{QDateTime.currentDateTime().toString()}] Failed to connect to MySQL database.")

        # إعداد واجهة المستخدم
        self.setup_ui()

        # نقل سجل الأحداث المؤقت إلى QTextEdit
        for log in self.temp_log:
            self.event_log.append(log)

        # إعداد المؤقت
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def connect_to_db(self):
        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="driver_monitoring",
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def create_session(self):
        if not self.db_connection:
            return
        try:
            with self.db_connection.cursor() as cursor:
                sql = "INSERT INTO sessions (start_time) VALUES (%s)"
                cursor.execute(sql, QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
                self.db_connection.commit()
                self.session_id = cursor.lastrowid
                self.temp_log.append(f"[{QDateTime.currentDateTime().toString()}] Session {self.session_id} created.")
        except pymysql.MySQLError as e:
            print(f"Error creating session: {e}")
            self.temp_log.append(f"[{QDateTime.currentDateTime().toString()}] Error creating session: {e}")

    def save_to_db(self, timestamp, status, ear):
        if not self.db_connection or not self.session_id:
            return
        try:
            with self.db_connection.cursor() as cursor:
                sql = """
                    INSERT INTO driver_data (timestamp, status, ear, sleep_count, drowsy_count, active_count, sleep_duration, drowsy_duration, active_duration, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    timestamp.toString("yyyy-MM-dd hh:mm:ss"),
                    status,
                    ear,
                    self.sleep_count,
                    self.drowsy_count,
                    self.active_count,
                    self.sleep_duration,
                    self.drowsy_duration,
                    self.active_duration,
                    self.session_id
                )
                cursor.execute(sql, values)
            self.db_connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error saving to MySQL: {e}")
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Error saving to MySQL: {e}")

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #1E1E1E; border-radius: 15px;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        self.video_label = QLabel("Waiting for video...")
        self.video_label.setFixedSize(720, 540)
        self.video_label.setStyleSheet("""
            border: 4px solid #4CAF50;
            border-radius: 15px;
            background-color: #222222;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        """)
        left_layout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        left_layout.addStretch()
        main_layout.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #1E1E1E; border-radius: 15px;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)

        self.status_label = QLabel("Status: Waiting...")
        self.status_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            background-color: #2E2E2E;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        """)
        right_layout.addWidget(self.status_label)

        self.drowsiness_bar = QProgressBar()
        self.drowsiness_bar.setMaximum(100)
        self.drowsiness_bar.setValue(0)
        self.drowsiness_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                text-align: center;
                font-size: 16px;
                background-color: #222222;
                color: white;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5555, stop:1 #FF9999);
                border-radius: 6px;
            }
        """)
        right_layout.addWidget(QLabel("Drowsiness Level:", styleSheet="font-size: 18px; color: white; font-weight: bold;"))
        right_layout.addWidget(self.drowsiness_bar)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setFixedSize(120, 50)
        self.start_stop_button.clicked.connect(self.toggle_system)
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        controls_layout.addWidget(self.start_stop_button)

        self.save_button = QPushButton("Save Stats")
        self.save_button.setFixedSize(120, 50)
        self.save_button.clicked.connect(self.save_stats)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
            QPushButton:hover {
                background-color: #1e87db;
            }
            QPushButton:pressed {
                background-color: #1a78c2;
            }
        """)
        controls_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Reset Log")
        self.reset_button.setFixedSize(120, 50)
        self.reset_button.clicked.connect(self.reset_log)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
            QPushButton:hover {
                background-color: #da3c30;
            }
            QPushButton:pressed {
                background-color: #c1352b;
            }
        """)
        controls_layout.addWidget(self.reset_button)

        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Low (0.27)", "Medium (0.25)", "High (0.23)"])
        self.sensitivity_combo.setCurrentIndex(1)
        self.sensitivity_combo.currentIndexChanged.connect(self.update_sensitivity)
        self.sensitivity_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                background-color: #2E2E2E;
                color: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 5px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        controls_layout.addWidget(QLabel("Sensitivity:", styleSheet="font-size: 18px; color: white; font-weight: bold;"))
        controls_layout.addWidget(self.sensitivity_combo)
        controls_layout.addStretch()
        right_layout.addLayout(controls_layout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(250)
        right_layout.addWidget(QLabel("Eye Aspect Ratio (EAR):", styleSheet="font-size: 18px; color: white; font-weight: bold;"))
        right_layout.addWidget(self.canvas)

        self.stats_table = QTableWidget()
        self.stats_table.setRowCount(6)
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.stats_table.setItem(0, 0, QTableWidgetItem("Sleep Events"))
        self.stats_table.setItem(1, 0, QTableWidgetItem("Drowsy Events"))
        self.stats_table.setItem(2, 0, QTableWidgetItem("Active Events"))
        self.stats_table.setItem(3, 0, QTableWidgetItem("Sleep Duration (s)"))
        self.stats_table.setItem(4, 0, QTableWidgetItem("Drowsy Duration (s)"))
        self.stats_table.setItem(5, 0, QTableWidgetItem("Active Duration (s)"))
        for i in range(6):
            self.stats_table.setItem(i, 1, QTableWidgetItem("0"))
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setMinimumHeight(300)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                font-size: 18px;
                background-color: #2E2E2E;
                color: white;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                gridline-color: #555555;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                padding: 8px;
                border: none;
            }
        """)
        right_layout.addWidget(QLabel("Statistics:", styleSheet="font-size: 18px; color: white; font-weight: bold;"))
        right_layout.addWidget(self.stats_table)

        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMinimumHeight(100)
        self.event_log.setStyleSheet("""
            font-size: 14px;
            background-color: #2E2E2E;
            color: white;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 5px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        """)
        right_layout.addWidget(QLabel("Event Log:", styleSheet="font-size: 18px; color: white; font-weight: bold;"))
        right_layout.addWidget(self.event_log)

        right_layout.addStretch()
        main_layout.addWidget(right_widget)

    def update_sensitivity(self):
        sensitivities = [0.27, 0.25, 0.23]
        self.sensitivity = sensitivities[self.sensitivity_combo.currentIndex()]
        self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Sensitivity set to {self.sensitivity}")

    def save_stats(self):
        try:
            with open("driver_stats.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    QDateTime.currentDateTime().toString(),
                    self.sleep_count, self.drowsy_count, self.active_count,
                    self.sleep_duration, self.drowsy_duration, self.active_duration,
                    self.session_id
                ])
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Statistics saved to driver_stats.csv")
        except Exception as e:
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Error saving stats: {e}")

    def reset_log(self):
        self.sleep_count = 0
        self.drowsy_count = 0
        self.active_count = 0
        self.sleep_duration = 0
        self.drowsy_duration = 0
        self.active_duration = 0
        for i in range(6):
            self.stats_table.setItem(i, 1, QTableWidgetItem("0"))
        self.event_log.clear()
        self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Log reset.")
        self.last_sleep_recorded = False
        self.last_drowsy_recorded = False
        self.sleep_start_time = None

    def toggle_system(self):
        if self.start_stop_button.text() == "Start":
            self.start_stop_button.setText("Stop")
            self.is_running = True
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Error: Could not open camera.")
                self.start_stop_button.setText("Start")
                self.is_running = False
                return
            self.timer.start(30)
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] System started.")
            self.save_to_db(QDateTime.currentDateTime(), "System Started", 0.0)
        else:
            self.start_stop_button.setText("Start")
            self.is_running = False
            self.timer.stop()
            self.cap.release()
            self.video_label.clear()
            self.status_label.setText("Status: Stopped")
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] System stopped.")
            self.save_to_db(QDateTime.currentDateTime(), "System Stopped", 0.0)
            self.last_sleep_recorded = False
            self.last_drowsy_recorded = False
            self.sleep_start_time = None

    def update_frame(self):
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] Error reading frame.")
            return

        frame = cv2.resize(frame, (720, 540))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        ear = 0.3
        for face in faces:
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = self.predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)

            left_ear = blinked(landmarks[36], landmarks[37], landmarks[38],
                               landmarks[41], landmarks[40], landmarks[39])
            right_ear = blinked(landmarks[42], landmarks[43], landmarks[44],
                                landmarks[47], landmarks[46], landmarks[45])
            ear = (left_ear + right_ear) / 2.0
            self.current_ear = ear
            self.ear_history.append(ear)
            if len(self.ear_history) > 50:
                self.ear_history.pop(0)

            drowsiness_level = max(0, min(100, int((0.3 - ear) * 400)))
            self.drowsiness_bar.setValue(drowsiness_level)

            current_time = QDateTime.currentDateTime()
            if ear < self.sensitivity - 0.04:
                self.drowsy = 0
                self.active = 0
                if self.sleep_start_time is None:
                    self.sleep_start_time = current_time
                elapsed_time = self.sleep_start_time.secsTo(current_time)
                if elapsed_time >= 1.6:
                    self.status = "UYUYOR !!!"
                    self.color = (0, 0, 255)
                    self.video_label.setStyleSheet("""
                        border: 4px solid #FF5555;
                        border-radius: 15px;
                        background-color: #222222;
                        box-shadow: 0 4px 8px rgba(255, 0, 0, 0.5);
                    """)
                    if self.sound_finished and not self.alarm_playing:
                        if not self.last_sleep_recorded:
                            self.sleep_count += 1
                            self.stats_table.setItem(0, 1, QTableWidgetItem(str(self.sleep_count)))
                            self.event_log.append(f"[{current_time.toString()}] Driver is SLEEPING!")
                            self.last_sleep_recorded = True
                            self.save_to_db(current_time, self.status, ear)
                        self.sound_finished = False
                        threading.Thread(target=play_alarm_sound, args=(self,), daemon=True).start()
                else:
                    self.status = "Eyes Closed..."
                    self.color = (255, 255, 0)
                self.last_drowsy_recorded = False
            elif self.sensitivity - 0.04 <= ear <= self.sensitivity:
                self.sleep = 0
                self.active = 0
                self.drowsy += 1
                self.sleep_start_time = None
                if self.drowsy > 6:
                    self.status = "YORGUN !"
                    self.color = (255, 0, 0)
                    self.video_label.setStyleSheet("""
                        border: 4px solid #FF9900;
                        border-radius: 15px;
                        background-color: #222222;
                        box-shadow: 0 4px 8px rgba(255, 165, 0, 0.5);
                    """)
                    if not self.last_drowsy_recorded:
                        self.drowsy_count += 1
                        self.stats_table.setItem(1, 1, QTableWidgetItem(str(self.drowsy_count)))
                        self.event_log.append(f"[{current_time.toString()}] Driver is DROWSY!")
                        self.last_drowsy_recorded = True
                        self.save_to_db(current_time, self.status, ear)
                self.last_sleep_recorded = False
            else:
                self.drowsy = 0
                self.sleep = 0
                self.active += 1
                self.sleep_start_time = None
                if self.active > 6:
                    self.status = "AKTIF :)"
                    self.color = (0, 255, 0)
                    self.video_label.setStyleSheet("""
                        border: 4px solid #4CAF50;
                        border-radius: 15px;
                        background-color: #222222;
                        box-shadow: 0 4px 8px rgba(0, 255, 0, 0.5);
                    """)
                    self.active_count += 1
                    self.stats_table.setItem(2, 1, QTableWidgetItem(str(self.active_count)))
                    self.event_log.append(f"[{current_time.toString()}] Driver is ACTIVE.")
                    self.save_to_db(current_time, self.status, ear)
                    self.alarm_playing = False
                    self.last_sleep_recorded = False
                    self.last_drowsy_recorded = False
                    self.sound_finished = True

            if self.last_state != self.status:
                if self.last_state:
                    duration = self.last_state_time.secsTo(current_time)
                    if self.last_state == "UYUYOR !!!":
                        self.sleep_duration += duration
                        self.stats_table.setItem(3, 1, QTableWidgetItem(str(self.sleep_duration)))
                    elif self.last_state == "YORGUN !":
                        self.drowsy_duration += duration
                        self.stats_table.setItem(4, 1, QTableWidgetItem(str(self.drowsy_duration)))
                    elif self.last_state == "AKTIF :)":
                        self.active_duration += duration
                        self.stats_table.setItem(5, 1, QTableWidgetItem(str(self.active_duration)))
                self.last_state = self.status
                self.last_state_time = current_time

            cv2.putText(frame, self.status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.color, 3)
            cv2.putText(frame, f"EAR: {ear:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        image = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio))

        self.status_label.setText(f"Status: {self.status}")
        self.status_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: rgb{self.color};
            background-color: #2E2E2E;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        """)

        self.ax.clear()
        self.ax.plot(self.ear_history, label="EAR", color="cyan")
        self.ax.axhline(y=self.sensitivity, color="red", linestyle="--", label="Threshold")
        self.ax.set_title("EAR Over Time", color="white", fontsize=14, fontweight="bold")
        self.ax.legend()
        self.ax.set_facecolor("#2E2E2E")
        self.figure.set_facecolor("#2E2E2E")
        self.ax.tick_params(colors="white")
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.canvas.draw()

    def closeEvent(self, event):
        self.is_running = False
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        if self.db_connection:
            self.db_connection.close()
            self.event_log.append(f"[{QDateTime.currentDateTime().toString()}] MySQL connection closed.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = DriverMonitorWindow()
    window.show()
    sys.exit(app.exec_())