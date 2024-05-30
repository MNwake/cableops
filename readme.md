# Cabled App Backend

Welcome to the backend repository for the Cabled App. This backend is designed to support the Cabled mobile application by providing real-time data processing, live updates, and control over the cable wakeboard park system.

## Overview

This backend is written in Python and runs on a Raspberry Pi. It serves multiple purposes:

- **API and Webserver:** Hosts an API that feeds data to users and provides live updates as data changes.
- **Robotics Control:** Connects the Raspberry Pi to multiple motors, switches, and drivers to control the cable system.
- **Graphical User Interface:** Provides a GUI built in Python using Kivy, utilizing the MVC architecture to give the operator complete control over the cable system.

## Features

### API and Webserver

- Hosts a FastAPI to provide data to the Cabled mobile app.
- Processes incoming data from the judges' app and updates rider statistics instantly.
- Provides real-time updates to users as data changes.

### CableOps Control

- Connects to multiple motors, switches, and drivers to control the cable system.
- Enables precise control of the cable system components.
- Designed ready for AI and Machine Learning implementation. 

### Graphical User Interface

- Built in Python using Kivy.
- Utilizes the MVC architecture to separate the concerns of the application.
- Provides a user-friendly interface for the operator to control the cable system.

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

