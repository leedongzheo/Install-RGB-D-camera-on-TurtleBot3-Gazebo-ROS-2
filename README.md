# Install-RGB-D-camera-on-TurtleBot3-Gazebo-ROS-2
RGB-D Sensor Integration on TurtleBot3 within ROS 2 Jazzy &amp; Gazebo Harmonic Simulation
## Overview

This project focuses on significantly upgrading the perception
capabilities of the standard **TurtleBot3** mobile robot by integrating
a high-fidelity **RGB-D (Red, Green, Blue - Depth)** camera sensor into
its simulation model. Utilizing the latest **ROS 2 Jazzy** framework and
the modern **Gazebo Harmonic** simulator, this integration is essential
for enabling advanced robotic applications such as 3D mapping, obstacle
avoidance, and precise object manipulation in complex environments.

------------------------------------------------------------------------

## Technical Implementation & Scope

### Category Details

## 🛠️ Technical Stack

| Component | Detail | Notes |
| :--- | :--- | :--- |
| **Robot Platform** | TurtleBot3 | Source code cloned directly from GitHub. The robot model used is: Waffle|
| **Robot OS** | ROS 2 Jazzy | Latest LTS distribution for robust control. |
| **Simulator** | Gazebo Harmonic (Gz-Harmonic) | Optimized for compatibility with ROS 2 Jazzy. |
| **Core Sensor** | RGB-D Camera | Provides synchronized image and depth data. |
| **Configuration File** | `model.sdf` | Manual modification of the robot's geometric and sensor description files to incorporate the RGB-D camera link and plugin. |
| **Source Management** | Direct GitHub Cloning | Ensures full control and customization of the TurtleBot3 simulation packages, bypassing standard library installation. |
| **Output & Control** | Robot Control & Data Visualization | The final integration will allow for real-time control of the robot and visualization of the rich RGB and Depth data streams via a suitable ROS 2 interface (e.g., RViz). |
------------------------------------------------------------------------

## Project Goal

To successfully implement and validate the RGB-D sensor stack on the
source-cloned TurtleBot3 model, confirming that **high-quality,
synchronized 3D point cloud and image data** are published correctly
over the ROS 2 network. This establishes a foundation for advanced:

-   3D SLAM\
-   Navigation\
-   Perception-driven manipulation\
-   Complex-environment autonomy

------------------------------------------------------------------------

## Source Cloning Instructions

``` bash
# Navigate to your ROS 2 workspace (e.g., ~/ros2_ws/src)
cd ~/ros2_ws/src

# Clone the necessary TurtleBot3 repositories
git clone -b jazzy-devel https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b jazzy-devel https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
https://github.com/ROBOTIS-GIT/DynamixelSDK.git
```
