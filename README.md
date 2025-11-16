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

## Repository Contents

This repository now ships a lightweight Python utility that
automatically patches the **TurtleBot3 Waffle** `model.sdf` description
with a simulated RGB-D camera that is compatible with ROS 2 Jazzy and
Gazebo Harmonic.  Instead of editing XML by hand, the helper script
creates:

1.  An RGB-D camera link complete with inertia, collision and visual
    geometry sized like a typical RealSense-class sensor.
2.  A fixed joint that anchors the sensor on top of the `base_link`
    chassis.
3.  A `depth` sensor definition with synchronized RGB, depth image and
    point cloud topics that can be bridged into ROS 2 using the
    `libgazebo_ros_depth_camera.so` plugin.

The key module is located at `turtlebot3_rgbd/sdf_patcher.py` and can be
used either programmatically or via the command line interface exposed
in `turtlebot3_rgbd/cli.py`.

## How to Use the Patcher

### 1. Prepare a TurtleBot3 Workspace

```bash
# Navigate to your ROS 2 workspace (e.g., ~/ros2_ws/src)
cd ~/ros2_ws/src

# Clone the necessary TurtleBot3 repositories
git clone -b jazzy-devel https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b jazzy-devel https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
```

### 2. Run the CLI Tool

With this repository available in your Python path (e.g., via
`pip install -e .` or by executing within the cloned folder), run:

```bash
python -m turtlebot3_rgbd.cli \
  ~/ros2_ws/src/turtlebot3/turtlebot3_description/urdf/turtlebot3_waffle/model.sdf \
  --namespace /tb3 \
  --pose 0 0 0.23 0 0 0
```

-   Use `--dry-run` to check whether the file already contains the
    sensor without touching the XML.
-   Supply `--output some/path/model_rgbd.sdf` to keep the original file
    untouched while generating an augmented version for experiments.

### 3. Launch Gazebo Harmonic

After patching the model you can launch Gazebo Harmonic through the
standard TurtleBot3 bringup launch files. RViz2 should expose
`/tb3/image`, `/tb3/image/depth` and `/tb3/points` topics when the robot
spawns successfully.

## Running Tests

The helper library ships with unit tests that validate the SDF
transforms and CLI behaviour. Install the optional development
dependencies and execute:

```bash
pip install -r requirements-dev.txt  # contains pytest
pytest
```

These tests parse minimal SDF models to ensure that the generated sensor
link, joint, and Gazebo ROS plugin definitions appear exactly once.
