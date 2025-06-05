import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import firebase_admin
from firebase_admin import credentials, db
from collections import Counter
from datetime import datetime


class FirebaseAccessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Access Log Viewer")
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_firebase()
        self.logs = {}

        self.last_updated_label = QLabel("Last Updated: Never")
        self.last_updated_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.last_updated_label)

        #Initial load of data
        self.update_ui()

        # every 10 secs, get data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(10000)

    def init_firebase(self):
        try:
            cred = credentials.Certificate("JSON FILE PATH HERE")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://cs131-final-project-49b00-default-rtdb.firebaseio.com/'
            })
        except ValueError:
            pass

    def fetch_logs(self):
        ref = db.reference('/')
        data = ref.get()
        return data.get('access_logs', {})

    def update_ui(self):
        try:
            new_logs = self.fetch_logs()
            if new_logs != self.logs:
                self.logs = new_logs
                self.refresh_content()

            self.last_updated_label.setText(
                f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception as e:
            self.last_updated_label.setText("Last Updated: Error fetching data")

    def refresh_content(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget and widget != self.last_updated_label:
                widget.setParent(None)

        self.show_info()
        self.plot_status_bar()
        self.plot_access_histogram()

    def show_info(self):
        last_granted = "Not found"
        last_id = "N/A"

        for key, entry in sorted(self.logs.items(), key=lambda x: x[1].get('timestamp', '')):
            if entry.get('status') == 'granted':
                last_granted = entry.get('timestamp')
                last_id = key

        entries = []
        for entry in self.logs.values():
            ts = entry.get('timestamp')
            status = entry.get('status', 'N/A')
            if ts and ts != 'N/A':
                dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                entries.append((dt, status))

        entries.sort(key=lambda x: x[0])
        consecutive_failures = 0
        for _, status in reversed(entries):
            if status == 'denied':
                consecutive_failures += 1
            else:
                break

        label_granted = QLabel(f"Last Granted Access: {last_granted} (ID: {last_id})")
        label_failures = QLabel(f"Latest Consecutive Failures: {consecutive_failures}")
        label_granted.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_failures.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.layout.insertWidget(0, label_failures)
        self.layout.insertWidget(0, label_granted)

    def plot_status_bar(self):
        statuses = [entry.get('status', 'N/A') for entry in self.logs.values()]
        status_counts = Counter(statuses)

        fig = Figure(figsize=(5, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.bar(status_counts.keys(), status_counts.values())
        ax.set_title("Access Status Counts")
        ax.set_xlabel("Status")
        ax.set_ylabel("Count")
        fig.tight_layout()

        self.layout.insertWidget(2, canvas)

    def plot_access_histogram(self):
        timestamps = []
        for entry in self.logs.values():
            ts = entry.get('timestamp', 'N/A')
            if ts != 'N/A':
                dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                timestamps.append(dt)

        fig = Figure(figsize=(6, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.hist(timestamps, bins=20)
        ax.set_title("Access Frequency Over Time")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Number of Accesses")
        fig.autofmt_xdate()
        fig.tight_layout()

        self.layout.insertWidget(3, canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FirebaseAccessApp()
    window.show()
    sys.exit(app.exec())
