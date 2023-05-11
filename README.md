# Robo Serve
Serve in restraunts

## Overview
These kinds of robots are very efficient and convenient during the covid times without much human intervention, which will deliver the food from the kitchen to the table. This ensures the hygiene of the food and safety of the customers. 

There are many applications instead of serving food, including but not limited to hospitality, home and the patients with covid positive. 

## Team
* Yashveer Jain
* Mayank Sharma

---

## Installation
```
cd ~/catkin_ws/src
git clone https://github.com/yashveerjain/Robo-Serve.git robo_serve
cd ..
catkin_make
. devel/setup.bash
```
* Note: 
    - Assuming the ROS is already installed and the workspace is already created as `catkin_ws` in home dir.
    - `robo_serve` is package name and so we are naming it our clone directory.

---

## Run
* On one terminal
```
* roslaunch launch/robo.launch
```
 - this will do the path planning where in you need to type a number (1-4) for table and then the robot will be spawned in the gazebo and moved to that table, and again moveback to kitchen.

## About Executables:

* automnomous_motion.py 
 - autonomous path planning and moving the robot by publishing the command vel, and subscribe to odometry for closed loop feedback

---

## Gazebo Visulization
click [here](https://drive.google.com/file/d/171N8MvP9Bu7LfLLoF1u9X4jArhIm103k/view)

---

## Model
Robot modelling is done on solidworks, part and assembly files are present [here](robot_part_files_solidworks/)

![](robo_details/robo.png)

---

## Depedencies
* ROS - noetic
* python3
* gazebo
* Rviz

### Installing Dependencies for Python
```
pip install -r requirements.txt
```
