from http import client
import multiprocessing
import socket
from _thread import *
from multiprocessing import Process, Queue
from threading import Thread

class socket_Transportation():
    def __init__(self, INNER_HOST, ROBOT_HOST, PORT):
        self.INNER_HOST = INNER_HOST
        self.ROBOT_HOST = ROBOT_HOST
        self.PORT = PORT

        self.socket_dict = dict()
        self.socketIsAlive = [False, False]


    def start_process(self):
        pc1 = Thread(target=self.inner_thread, args=(self.INNER_HOST, self.PORT))
        pc2 = Thread(target=self.robot_thread, args=(self.ROBOT_HOST, self.PORT))

        pc1.start()
        pc2.start()


    def inner_thread(self, HOST, PORT):
        # 서버 소켓 생성
        print(f'>> {HOST} Server Start')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        try:
            while True:
                self.socketIsAlive[0] = False
                print('>> Wait')
                inner_socket, inner_addr = server_socket.accept()
                self.socket_dict[inner_socket] = inner_addr

                self.socketIsAlive[0] = True

                self.inner2robot(inner_socket)

                #
                del self.socket_dict[inner_socket]
            
        except Exception as e :
            print ('inner 에러는? : ',e)

        finally:
            inner_socket.close()


    def robot_thread(self, HOST, PORT):
        # 서버 소켓 생성
        print(f'>> {HOST} Server Start')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        try:
            while True:
                self.socketIsAlive[1] = False

                print('?',self.socketIsAlive[1])
                
                print('>> Wait')
                robot_socket, robot_addr = server_socket.accept()
                self.socket_dict[robot_socket] = robot_addr

                self.socketIsAlive[1] = True
                print('!',self.socketIsAlive[1])

                self.robot2inner(robot_socket)

                #
                del self.socket_dict[robot_socket]

        except Exception as e :
            print ('robot 에러는? : ',e)

        finally:
            robot_socket.close()


    def inner2robot(self, inner_socket):
        print('>> Connected by', self.socket_dict[inner_socket][0], f'({len(self.socket_dict)} / 2)')
        
        while True:
            
            try:
                data = inner_socket.recv(1024)

                if not data:
                    del self.socket_dict[inner_socket]
                    print('>> Disconnected by ' + self.socket_dict[inner_socket][0], f'({len(self.socket_dict)} / 2)')
                    break

                print('>> Received from', self.socket_dict[inner_socket][0], ':', data.decode())

                for k in list(self.socket_dict.keys()):
                    if k == inner_socket:
                        continue
                    else:
                        robot_socket = k

                if self.socketIsAlive[1]:
                    robot_socket.send(data)

            except ConnectionResetError as e:
                print('>> Disconnected by ' + self.socket_dict[inner_socket][0])
                break


    def robot2inner(self, robot_socket):
        print('>> Connected by', self.socket_dict[robot_socket][0], f'({len(self.socket_dict)} / 2)')
        while True:
            
            try:
                data = robot_socket.recv(1024)

                if not data:
                    del self.socket_dict[robot_socket]
                    print('>> Disconnected by ' + self.socket_dict[robot_socket][0], f'({len(self.socket_dict)} / 2)')
                    break

                print('>> Received from', self.socket_dict[robot_socket][0], ':', data.decode())

                for k in list(self.socket_dict.keys()):
                    if k == robot_socket:
                        continue
                    else:
                        inner_socket = k

                if self.socketIsAlive[0]:
                    inner_socket.send(data)

            except ConnectionResetError as e:
                print('>> Disconnected by ' + self.socket_dict[robot_socket][0])
                break



if __name__ == '__main__':
    # 서버 IP 및 열어줄 포트
    INNER_HOST = '10.10.33.148' # 내부망
    ROBOT_HOST = '192.168.2.5' # 공유기
    PORT = 9999

    a = socket_Transportation(INNER_HOST, ROBOT_HOST, PORT)
    a.start_process()
