# Import database module.
# from firebase_admin import db

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize the app with a service account
cred = credentials.Certificate("file json path")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cs131-final-project-49b00-default-rtdb.firebaseio.com/'
})

# Reference the root of the database
ref = db.reference('/')
data = ref.get()

# Print the data
print(data)

# Access the 'access_logs' dictionary
logs = data['access_logs']

# Iterate through each log entry
for key, entry in logs.items():
    status = entry.get('status', 'N/A')
    person = entry.get('person', 'N/A')
    timestamp = entry.get('timestamp', 'N/A')

    if status == 'granted':
        # print(f"  Status: {status}")
        # print(f"  Person: {person}")
        print()
        print(f"Last time granted: {timestamp}")
        print(f"ID: {key}")
        print()
        break

#Print amount of latest consecutive failures

from datetime import datetime

logs = data['access_logs']

# Extract and sort log entries by timestamp
log_entries = []
for entry in logs.values():
    timestamp = entry.get('timestamp')
    status = entry.get('status', 'N/A')
    if timestamp != 'N/A':
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        log_entries.append((dt, status))

# Sort by timestamp
log_entries.sort(key=lambda x: x[0])

# Count consecutive failures from the end
consec_failures = 0
for dt, status in reversed(log_entries):
    if status == 'denied':
        consec_failures += 1
    else:
        break  # Stop as soon as we hit a "granted"

print(f"Latest consecutive failures: {consec_failures}")


import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Assuming `data` contains the Firebase access_logs dictionary
logs = data['access_logs']

# Prepare lists
timestamps = []
statuses = []
persons = []

# Extract values
for entry in logs.values():
    timestamps.append(entry.get('timestamp', 'N/A'))
    statuses.append(entry.get('status', 'N/A'))
    persons.append(entry.get('person', 'Unknown'))

# Convert timestamps to datetime objects for time-based plots
timestamps_dt = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps if ts != 'N/A']

# Convert to NumPy arrays if needed
timestamps_np = np.array(timestamps_dt)
statuses_np = np.array(statuses)
persons_np = np.array(persons)

from collections import Counter

# Count status occurrences
status_counts = Counter(statuses)

# Bar chart
plt.figure(figsize=(6, 4))
plt.bar(status_counts.keys(), status_counts.values())
plt.title('Access Status Counts')
plt.xlabel('Status')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# Count number of accesses per timestamp
plt.figure(figsize=(10, 4))
plt.hist(timestamps_dt, bins=20)
plt.title('Access Frequency Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Number of Accesses')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

