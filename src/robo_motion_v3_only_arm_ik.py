#!/usr/bin/python3

import rospy
import numpy as np
import sympy
from sympy import Matrix, Symbol, symbols, BlockMatrix
import pandas as pd
from tabulate import tabulate
import math

from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
import sys, select, termios, tty
import time

msg = """
Control Your Bot!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .
space key, k : force stop
anything else : stop smoothly
CTRL-C to quit
"""

table_details = """
"1" : ((-2,0),"right"),
"2" : ((-5,0),"right"),
"3" : ((-8,0),"right"),
"4" : ((-8,0),"left"),
"5" : ((-5,0),"left"),
"6" : ((-2,0),"left"),            
"""

class Robot:
        # pub_left = rospy.Publisher('/rat_bot/front_left_axle_revolute_controller/command', Float64, queue_size=10)
    
     # Add your topic for move here '' Eg '/my_robot/longitudinal_controller/command'

    x = 0
    th = 0
    status = 0
    count = 0
    acc = 0.1
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0
    # rate = rospy.Rate(100)
    
    front_man_angle= 3*1.57
    left_side_man_angle = 2*3.14
    right_side_man_angle =  3.14
    base_pose_tray_diffusor = 6
    final_pose_tray_diffusor = 6.2
    initial_end_effector_pose = 0
    final_end_effector_pose = .15
    
    current_man_angle = front_man_angle
    current_end_effector_pose = initial_end_effector_pose
    current_tray_diffusor_pose = base_pose_tray_diffusor

    moveBindings = {
        'i':(1,0),
        'o':(1,-1),
        'j':(0,1),
        'l':(0,-1),
        'u':(1,1),
        ',':(-1,0),
        '.':(-1,1),
        'm':(-1,-1),
           }
    def __init__(self, robo_cmd="/robo_serve"):
        self.speed = 0.3 # 1m/s
        self.turn = 0.3 # 1rad/sec

        self.pub_manipulator = rospy.Publisher(f'{robo_cmd}/first_link_controller/command', Float64, queue_size=10)
        self.pub_move = rospy.Publisher(f'{robo_cmd}/cmd_vel', Twist, queue_size=10)
        self.pub_tray_diff = rospy.Publisher(f'{robo_cmd}/tray_diffusor_joint_controller/command', Float64, queue_size=10)
        self.pub_end_effector = rospy.Publisher(f'{robo_cmd}/end_effector_controller/command', Float64, queue_size=10)


        thetas = symbols(r"theta_1")
        distances = symbols("a1 a2 D")
        self.DH_param = self.get_dh_parameters(thetas,distances)
        self.armBindings={
            'e':(self.pub_end_effector,self.initial_end_effector_pose,self.final_end_effector_pose),
            'E':(self.pub_end_effector,self.final_end_effector_pose,self.initial_end_effector_pose),
            't': (self.pub_tray_diff,self.base_pose_tray_diffusor,self.final_pose_tray_diffusor),
            'T': (self.pub_tray_diff,self.final_pose_tray_diffusor,self.base_pose_tray_diffusor),
            'a' : (self.pub_manipulator,self.front_man_angle,self.left_side_man_angle), # left side manipulator
            'd' : (self.pub_manipulator,self.front_man_angle,self.right_side_man_angle), # right side manipulator
            'A' : (self.pub_manipulator,self.left_side_man_angle,self.front_man_angle), # left side to front post manipulator
            'D' : (self.pub_manipulator,self.right_side_man_angle,self.front_man_angle), # right side to front manipulator
            }
        self.start=True
        self.settings = termios.tcgetattr(sys.stdin)
        self.table2pose()
        
        

    def table2pose(self):
        self.tablePose = {
            "1" : ((-2,0),"right"),
            "2" : ((-5,0),"right"),
            "3" : ((-8,0),"right"),
            "4" : ((-8,0),"left"),
            "5" : ((-5,0),"left"),
            "6" : ((-2,0),"left"),            
        }
        print("Table coordinates ---")
        print("Key : Location")
        for key, value in self.tablePose.items():
            print(key, ' : ', value) 
        print("------")   
    def getKey(self):
        
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key
    
    def get_dh_parameters(self,thetas, distances):
        theta_1  = thetas
        self.a1,self.a2,self.D = distances
        # DH Parameters
        data = {r'theta': [theta_1-90, 0],#['laptop', 'printer', 'tablet', 'desk', 'chair'],
                'alpha': [-90, 0], #[1200, 150, 300, 450, 200],
                'r' : [0,0],
                'd' : [self.a1,self.a2+self.D]
                }

        df = pd.DataFrame(data, index=['frame_1','frame_2'])
        # df.style
        # displaying the DataFrame
        print("\n################DH Table--------------\n")
        print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
        print("\n#################\n")
        
        ## DH parameters values
        self.a2 = 0.3048
        self.a1 = 0

        return df

    def vels(self,speed,turn):
        return "currently:\tspeed %s\tturn %s " % (speed,turn)

    def gen_arm_move_func(self, publisher, initial, final, num=50):
        
        steps = np.linspace(initial, final, num)
        print(steps)
        for i in steps:
            publisher.publish(i)
            time.sleep(0.1)
        
    def get_desired_steering(self, x, y):
        theta = np.arctan2((y),(x))# between -pi to pi
        # -pi/4 means 4rd quadrant and pi/4 1st quadrant
        return theta

    def IK_arm(self, tableKey):
        pose, direction = self.tablePose[tableKey]
        print(direction)
        # Pose w.r.t to robot
        if direction=="right":
            yf = -0.55
            xf = 0
        else:
            yf = 0.55
            xf = 0
        theta_pre = self.get_desired_steering(xf,yf)
        print(theta_pre)
        theta = theta_pre - 1.57 # subtracting with 90 deg
        print(self.front_man_angle, theta)
        print(f"moving arm in {direction} direction --- ")
        self.gen_arm_move_func(self.pub_manipulator, self.front_man_angle, theta)
        if math.cos(theta)<1e-2 and math.cos(theta)>-1e-2:
            self.D = -xf/math.sin(theta) - self.a2
        else:
            self.D = yf/math.cos(theta) - self.a2
        
        print("Dispatching end effector --- ")
        self.gen_arm_move_func(self.pub_end_effector, self.initial_end_effector_pose, self.D)
        print("IK : ",self.D, "| theta : ",theta)
        time.sleep(1)
        print(f"moving end effector to base position --- ")
        self.gen_arm_move_func(self.pub_end_effector, self.D, self.initial_end_effector_pose)

        print(f"moving arm to base position --- ")
        self.gen_arm_move_func(self.pub_manipulator,theta, self.front_man_angle)


    def base_move(self, start_pose, goal_pose):
        x_o,y_o = start_pose
        x_g,y_g = goal_pose
        
    def move(self,key,x,th,status,target_speed,target_turn,control_speed,control_turn):
        move_msg = Twist()
        target_speed = self.speed
        target_turn = self.turn 
        count = 0
        try:

            if key in self.moveBindings.keys():
                x = self.moveBindings[key][0]
                th = self.moveBindings[key][1]
                print("key",key)
                count = 0
                self.start=False
            elif key in self.tablePose.keys():
                x = 0
                th = 0
                print("############")
                print("Table number Recieved: ",key)
                self.IK_arm(key)
                
                count = 0
                if (status == 14):
                    print (msg)
                status = (status + 1) % 15
                self.start=False
            elif key == ' ' or key == 'k' :
                x = 0
                th = 0
                control_speed = 0
                control_turn = 0
            else:
                count = count + 1
            
            target_speed = self.speed * x
            target_turn = self.turn * th

            if target_speed > control_speed:
                control_speed = min( target_speed, control_speed + 0.02 )
            elif target_speed < control_speed:
                control_speed = max( target_speed, control_speed - 0.02 )
            else:
                control_speed = target_speed

            if target_turn > control_turn:
                control_turn = min( target_turn, control_turn + 0.1 )
            elif target_turn < control_turn:
                control_turn = max( target_turn, control_turn - 0.1 )
            else:
                control_turn = target_turn


        except Exception as e:
            print (e)

        finally:
            # control_turn=0.5
            # control_speed =5
            print("############")
            print("control speed : ",control_speed)
            print("control turn : ",control_turn)
            print("############") 
            move_msg.angular.z = control_turn
            move_msg.linear.x = control_speed
            
            self.pub_move.publish(move_msg)
            
            if self.start:
                self.pub_manipulator.publish(self.front_man_angle)
                self.pub_tray_diff.publish(self.base_pose_tray_diffusor)
                self.pub_end_effector.publish(self.initial_end_effector_pose)
        return x,th,status,target_speed,target_turn,control_speed,control_turn

    def run(self):
        x = 0
        th = 0
        status = 0
        count = 0
        
        target_speed = 0
        target_turn = 0
        control_speed = 0
        control_turn = 0
        inp = (x,th,status,target_speed,target_turn,control_speed,control_turn)
        print (msg)
        while(1):
            key = self.getKey()
            inp = self.move(key,*inp)
            if (key == '\x03'):
                break
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        
if __name__=="__main__":
    
    
    rospy.init_node('my_teleop')

    # pub_right = rospy.Publisher('/rat_bot/front_right_axle_revolute_controller/command', Float64, queue_size=10) # Add your topic here between ''. Eg '/my_robot/steering_controller/command'

    robot  = Robot()    
    robot.run()
    
    
