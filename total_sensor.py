from operator import index
import time
from pyrsistent import v
import serial
import numpy as np
import pyrealsense2 as rs
import math as m


## sudo chmod 777 /dev/ttyUSB0 해준 후 실행(포트 권한 설정)
ser = serial.Serial(port = '/dev/ttyUSB0', baudrate = 115200, timeout = 1)

path = "../Log/Log_220805/Anchor/"

#-----------------T265---------------------------
pipe = rs.pipeline()

# Build config object and request pose data
cfg = rs.config()
cfg.enable_stream(rs.stream.pose)

# Start streaming with requested config
pipe.start(cfg)

t265_key = ['x','y','z','vx','vy','vz','ax','ay','az','roll','pitch','yaw']
t265_val = [0]*12

#--------------------------------------------------


## 파이썬에서 입력 -> 아두이노 시리얼에서 입력됨
while True:
    
    print("input: ", end='')
    op = input()    ## p : 메뉴 확인
    ser.write(op.encode())
    
    count = 10
    idx = 0
    log_data = []
    data_list = []
    
    tag_key = [i for i in range(10,20)]
    tag_val = [None]*10
    tag_dict = dict(zip(tag_key, tag_val))

    while True:
        
        try:
            data = ser.readline().decode()
            # print(data, end="")
            
            ## 태그 10-19번 거리 추출(1번)
            if (op == '5'):
                
                if "DIST" in data:
                    Dist = data.split(',')
                    Dist = Dist[0][6:]
                    # print("{}번 태그 : {}".format(count, data), end="")
                    
                    tag_dict = {count : Dist}
                    print(tag_dict)
                    
                    count += 1
                    if count == 20:
                        count = 10
                        
            ## 태그 10-19번 거리 추출(연속)
            elif (op == '6'):
                if "DIST" in data:
                    Dist = data.split(',')
                    Dist = Dist[0][6:]

                    tag_dict[count] = Dist
                    count += 1
                    
                    if count == 20:
                        arr = [idx, tag_dict]
                        log_data.append(arr)
                        
                        print(arr)
                        
                        count = 10
                        tag_dict = dict(zip(tag_key, tag_val))
                        
                        frames = pipe.wait_for_frames()
                        pose = frames.get_pose_frame()
                        if pose:
                            # Print some of the pose data to the terminal
                            Tdata = pose.get_pose_data()
                            x = Tdata.translation.x
                            y = Tdata.translation.y
                            z = Tdata.translation.z
                            
                            vx = Tdata.velocity.x
                            vy = Tdata.velocity.y
                            vz = Tdata.velocity.z
                            
                            ax = Tdata.acceleration.x
                            ay = Tdata.acceleration.y
                            az = Tdata.acceleration.z
                            
                            _w = Tdata.rotation.w
                            _x = -Tdata.rotation.z
                            _y = Tdata.rotation.x
                            _z = -Tdata.rotation.y
                            
                            pitch = -m.asin(2.0 * (_x*_z - _w*_y)) * 180.0 / m.pi
                            roll  = m.atan2(2.0 * (_w*_x + _y*_z), _w*_w - _x*_x - _y*_y + _z*_z) * 180.0 / m.pi
                            yaw   = m.atan2(2.0 * (_w*_z + _x*_y), _w*_w + _x*_x - _y*_y - _z*_z) * 180.0 / m.pi
                            
                            t265_val = [x,y,z,vx,vy,vz,ax,ay,az,roll,pitch,yaw]
                            
                            t265_dict = dict(zip(t265_key,t265_val))
                            
                            t265_arr = [idx,t265_dict]
                            data_list.append(t265_arr)        
                            
                            print(t265_arr)
                            idx += 1
                            print("--------------------------------")
                            
                            # print("x:{0:0.8f}, y:{1:0.8f}, z:{2:0.8f}".format(x,y,z))
                            # print("Velocity: {}".format(Tdata.velocity))
                            # print("Acceleration: {}\n".format(Tdata.acceleration))
                            # print("RPY [deg]: Roll: {0:.7f}, Pitch: {1:.7f}, Yaw: {2:.7f}".format(roll, pitch, yaw))
                            
            ## 나머지
            else:
                print(data, end="")
            
            if data == "":
                break
            
            
            
        except KeyboardInterrupt:
            
            np.save("../Log/Log_220809/T265/T265_220809_Case.npy",data_list)
            
            np.save("../Log/Log_220809/Anchor/uwb_220809_Case.npy", log_data, allow_pickle=True)  ## 로그 저장
            op = 'p'    ## p : 메뉴 확인
            ser.write(op.encode())
            ser.flush()
            break

    
    ## 종료
    if op == 'q':
        ser.close()
        pipe.stop()
        
        break
    