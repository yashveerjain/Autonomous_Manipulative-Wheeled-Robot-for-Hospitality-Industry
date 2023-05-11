# Manipulatie-Wheeled-Robot-for-Hospitality-Industry
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
git clone https://github.com/yashveerjain/Autonomous_Manipulative-Wheeled-Robot-for-Hospitality-Industry.git
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
 - this will do the path planning where in you need to type a number (1-4) for table and then the robot will be spawned in the gazebo

## About Executables:
* robo_motion.py
    - Operates solely on Teleop keyboard keys.
    - See the message printed on after running to hit right keys
* robo_motion_v2.py
    - Meant to be fully Autonomous, but still work in progress ;)
* automotion.py 
 - autonomous path planning 


## Robo Workspace
![](robo_details/RoboArmWorkspace.png)

---

## Gazebo Visulization
click [here](https://drive.google.com/file/d/1JSarveQId-FuYrpnsp-5kvK6pxswPh_k/view?usp=sharing)

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
