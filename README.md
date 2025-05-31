# Predictive Maintenance Using Random Forest Classifier

This project uses a Random Forest Classifier to predict machine failure and integrates Firebase Realtime Database to collect and display real-time sensor data.

---

## Setup Instructions

### 1. Firebase Realtime Database

1. Create a Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com).
2. Enable **Realtime Database**.
3. Structure your database as follows:

    ```json
    {
      "sensors": {
        "temp1": 0,
        "temp2": 0
      }
    }
    ```

---

### 2. API Key and JSON Configuration

#### In `Project2.ino` (Arduino Code):

```cpp
// Add your Firebase API key and host
#define FIREBASE_HOST "your-project.firebaseio.com"
#define FIREBASE_AUTH "your_api_key"

// Add your WiFi credentials
#define WIFI_SSID "your_wifi_name"
#define WIFI_PASSWORD "your_wifi_password"
```

#### 3. BACKEND

1. Export JSON From Firebase realtime database.
2. Paste the JSON file into the `users` folder.
3. In 'views.py',update the path of json file.
