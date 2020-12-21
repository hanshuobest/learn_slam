#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@filename    :aruco_subscriber.py
@brief       :订阅/aruco_single/transform
@time        :2020/12/16 15:22:45
@author      :hscoder
@versions    :1.0
@email       :hscoder@163.com
@usage       :
'''

import rospy
import math
from geometry_msgs.msg import TransformStamped
import numpy as np
from scipy.spatial.transform import Rotation
import yaml


# base_link to object trans
# base_link_2_object_matrix = np.mat([[-1 , 0 , 0 , 0] ,
#                                     [0 , 0 , 1 , -0.156] ,
#                                     [0 , -1 , 0 , 1.173] ,
#                                     [0 , 0 , 0 , 1]])

# base_link_2_object_matrix = np.mat([[1, 0, 0, 0],
#                                     [0, 1, 0, 0.156],
#                                     [0, 0, 1, -1.457],
#                                     [0, 0, 0, 1]])


base_link_2_object_matrix = np.mat([[1, 0, 0, 0],
                                    [0, 1, 0, 0.156],
                                    [0, 0, 1, -1.061],
                                    [0, 0, 0, 1]])

object_2_base_link = base_link_2_object_matrix.I


class ArucoSub(object):
    def __init__(self, aruco_trans_topic):
        self.aruco_trans_topic = aruco_trans_topic
        self.trans_pub = rospy.Subscriber(
            aruco_trans_topic, TransformStamped, self.callback)
        self.queue = []

    def callback(self, data):

        translation = data.transform.translation
        rotation = data.transform.rotation

        translation_vec = [translation.x, translation.y, translation.z]
        rotation_vec = [rotation.x, rotation.y, rotation.z, rotation.w]

        R = {"tran": translation_vec, "quart": rotation_vec}
        self.queue.append(R)

        if len(self.queue) < 20:
            pass
        else:
            mean_translation_x = 0.0
            mean_translation_y = 0.0
            mean_translation_z = 0.0
            mean_rotation_x = 0.0
            mean_rotation_y = 0.0
            mean_rotation_z = 0.0
            mean_rotation_w = 0.0
            for t in self.queue:
                mean_translation_x += t['tran'][0]
                mean_translation_y += t['tran'][1]
                mean_translation_z += t['tran'][2]

                mean_rotation_x += t['quart'][0]
                mean_rotation_y += t['quart'][1]
                mean_rotation_z += t['quart'][2]
                mean_rotation_w += t['quart'][3]

            mean_translation_x /= 20
            mean_translation_y /= 20
            mean_translation_z /= 20
            mean_rotation_x /= 20
            mean_rotation_y /= 20
            mean_rotation_z /= 20
            mean_rotation_w /= 20

            mean_translation_x = -1.0 * mean_translation_x

            # 四元数转旋转矩阵
            rotation_matrix = Rotation(
                [mean_rotation_x, mean_rotation_y, mean_rotation_z, mean_rotation_w]).as_matrix()
            T = np.identity(4, dtype=np.float32)
            # T[:3 , :3] = rotation_matrix
            T[0, 0] = rotation_matrix[0, 0]
            T[0, 1] = rotation_matrix[0, 1]
            T[0, 2] = rotation_matrix[0, 2]
            T[1, 0] = rotation_matrix[1, 0]
            T[1, 1] = rotation_matrix[1, 1]
            T[1, 2] = rotation_matrix[1, 2]
            T[2, 0] = rotation_matrix[2, 0]
            T[2, 1] = rotation_matrix[2, 1]
            T[2, 2] = rotation_matrix[2, 2]
            T[0, 3] = mean_translation_x
            T[1, 3] = mean_translation_y
            T[2, 3] = mean_translation_z

            # T = np.mat(T).I

            print("T: ", T)
            print("*********************************")
            print("object 2 base: ")
            print(object_2_base_link)
            print('---------------------------------')

            print("camera to base-link trans: ", T @ object_2_base_link)
            self.queue = []


def main():
    rospy.init_node('arucoTransformNode')
    aruco_sub = ArucoSub('/aruco_single/transform')
    rospy.spin()
    q = aruco_sub.get_transformation()
    print(q)


if __name__ == '__main__':
    main()
