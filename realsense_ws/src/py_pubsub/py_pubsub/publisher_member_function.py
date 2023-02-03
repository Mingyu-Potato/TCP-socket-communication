# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

## realsense.py
from operator import index
import time
from pyrsistent import v
import test
import numpy as np
import pyrealsense2 as rs
import math as m

from std_msgs.msg import String
from realsense_interfaces.msg import Sensor

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(Sensor, 'topic', 10)
        self.i = 0
        
        #-----------------T265---------------------------
        self.pipe = rs.pipeline() ## context object 생성, 연결된 realsense 장치에 대한 모든 handle 소유

        # Build config object and request pose data
        self.cfg = rs.config() ## stream 구성
        self.cfg.enable_stream(rs.stream.pose)

        # Start streaming with requested config
        self.pipe.start(self.cfg) ## streaming 시작

        self.t265_key = ['x','y','z','vx','vy','vz','ax','ay','az','roll','pitch','yaw']
        self.t265_val = [0]*12
        #--------------------------------------------------
        
        timer_period = 0.01  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)


    def timer_callback(self):
        # Wait for the next set of frames from the camera   
        self.frames = self.pipe.wait_for_frames() ## 카메라에서 다음 프레임 세트를 기다림
        # Fetch pose frame
        self.pose = self.frames.get_pose_frame() ## pose frame 획득
        if self.pose:
            # Print some of the pose data to the terminal
            self.Tdata = self.pose.get_pose_data() ## pose data 반환
            
            ## 각 프레임에 해당하는 x,y,z 추가
            self.x = self.Tdata.translation.x 
            self.y = self.Tdata.translation.y
            self.z = self.Tdata.translation.z
            
            ## 각 프레임에 해당하는 vx,vy,vz(속도) 추가
            self.vx = self.Tdata.velocity.x
            self.vy = self.Tdata.velocity.y
            self.vz = self.Tdata.velocity.z
            
            ## 각 프레임에 해당하는 ax,ay,az(가속) 추가
            self.ax = self.Tdata.acceleration.x
            self.ay = self.Tdata.acceleration.y
            self.az = self.Tdata.acceleration.z
            
            ## 각 프레임에 해당하는 _w,_x,_y,_z(회전) 추가
            self._w = self.Tdata.rotation.w
            self._x = -self.Tdata.rotation.z
            self._y = self.Tdata.rotation.x
            self._z = -self.Tdata.rotation.y
            
            ## y축 중심 회전
            self.pitch = -m.asin(2.0 * (self._x*self._z - self._w*self._y)) * 180.0 / m.pi
            ## x축 중심 회전
            self.roll  = m.atan2(2.0 * (self._w*self._x + self._y*self._z), self._w*self._w - self._x*self._x - self._y*self._y + self._z*self._z) * 180.0 / m.pi
            ## z축 중심 회전
            self.yaw   = m.atan2(2.0 * (self._w*self._z + self._x*self._y), self._w*self._w + self._x*self._x - self._y*self._y - self._z*self._z) * 180.0 / m.pi
            
            ## 배열 생성
            ## self.data_list=[self.pitch, self.roll, self.yaw]
            
            ## 메세지 publish
            # msg = String()
            # msg.data = '%d: ' % self.i  + 'pitch: %f ' % self.pitch + 'roll: %f ' % self.roll + 'yaw: %f' % self.yaw
            # msg.data = self.data_list
            msg = Sensor()
            msg.pitch = self.pitch
            msg.roll = self.roll
            msg.yaw = self.yaw
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: ' + 'pitch: %f ' % msg.pitch + 'roll: %f ' % msg.roll + 'yaw: %f' % msg.yaw)
            self.i += 1
            
    def __getPipe__(self):
        return self.pipe

def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()
    pipe = minimal_publisher.__getPipe__() ## 파이프 열기

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    pipe.close() ## 파이프 닫기
    
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
