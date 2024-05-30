# Cabled App Backend

Welcome to the backend repository for the Cabled App. This backend is designed to support the Cabled mobile application by providing real-time data processing, live updates, and control over the cable wakeboard park system.

## Overview

This backend is written in Python and runs on a Raspberry Pi. It serves multiple purposes:

- **Active Webserver:** Hosts an API that feeds data to users and provides live updates as data changes.
- **Data Processing:** Receives rider scores from a separate judges' mobile app, processes the data in Python, updates rider statistics, and broadcasts the updates to all active users.
- **Robotics:** Controls the cable wakeboard park system by connecting the Raspberry Pi to multiple motors, switches, and drivers.

## Features

### Webserver and API

- Hosts a FastAPI to provide data to the Cabled mobile app.
- Provides real-time updates to users as data changes.
- Processes incoming data from thee judges' app and updates rider statistics instantly.

### Robotics Control

- Connects to multiple motors, switches, and drivers to control the cable system.
- Allows for complete control of the cable system via a GUI built in Kivy.

## Installation

### Prerequisites

- Python 3.6+
- Raspberry Pi with Raspbian OS
- Required hardware (motors, switches, drivers)
- Kivy 2.0+ (for the GUI)

### Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/cabled-backend.git
    cd cabled-backend
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the server:**
    ```bash
    python server.py
    ```


## Disclaimer

This backend is part of an ongoing project to develop an operating system for cable wakeboard parks. It is a work in progress and may not be fully functional. For the most current version of the Cabled app, please refer to the Apple App Store.

