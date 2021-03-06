#!/usr/bin/env python
# license removed for brevity
import rospy
import os
import roslib
import time
import math
import numpy as np

from nav_msgs.msg import Path
from std_msgs.msg import Header
from geometry_msgs.msg import PoseStamped

def IsValidTrajType(traj_type):
    return traj_type in ('sin', 'polygon')

def SinTrajGenerator(msg, step):
    x_ar = np.arange(0,2*np.pi, step)   # start,stop,step
    y_ar = np.sin(x_ar)

    cnt = 0
    for i in range(len(x_ar)):
        ps = PoseStamped()
        ps.header = msg.header
        ps.header.seq = cnt
        cnt += 1
        ps.pose.position.x = x_ar[i]
        ps.pose.position.y = y_ar[i]
        ps.pose.position.z = 0 
        msg.poses.append(ps)  

    return msg 

def PolygonTrajGenerator(msg, step):

    p1 = (0.0, 0.0)
    p_edges = [(2.0, -0.1), (2.1, 1.9),  (0.1, 2.0), (0, 0)]
    
    points = []
    
    for edge in p_edges:
        p2 = edge
        k = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = (p1[1]*p2[0] - p2[1]*p1[0] ) / (p2[0] - p1[0])
        x = p1[0]
        y = k*x + b
        points.append((x,y))
        step = abs(p2[0] - p1[0])/10
        if p2[0] > p1[0]:
            while (x < p2[0]):
                x += step
                if (x > p2[0]):
                    break
                y = k*x + b
                points.append((x,y))
        else:
             while (x > p2[0]):
                x -= step
                if (x < p2[0]):
                    break
                y = k*x + b
                points.append((x,y))
        p1 = p2

    cnt = 0
    for p in points:
        ps = PoseStamped()
        ps.header = msg.header
        ps.header.seq = cnt
        cnt += 1
        ps.pose.position.x = p[0]
        ps.pose.position.y = p[1]
        ps.pose.position.z = 0 
        msg.poses.append(ps)  

    return msg     

     


def main():
    rospy.init_node("path_pub", anonymous=True)
    rospy.loginfo("path_pub init")
    traj_type = rospy.get_param('~traj_type')

    if not IsValidTrajType(traj_type):
        rospy.logerr("Not valid traj type")
        return

    path_topic_name = "/path"

    path_pub = rospy.Publisher(path_topic_name, Path, queue_size=5)    

    msg = Path()
    msg.header.frame_id = "odom"
    msg.header.stamp = rospy.Time.now()
    msg.header.seq = 0
    msg.poses = []

    step = 0.1

    if traj_type == 'sin':
        msg = SinTrajGenerator(msg, step)
    elif traj_type == 'polygon':
        msg = PolygonTrajGenerator(msg, step)

    while not rospy.is_shutdown():
        if path_pub.get_num_connections() > 1:
            break
        rospy.sleep(0.3)

    path_pub.publish(msg)

if __name__ == '__main__':
    main()
