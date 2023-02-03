## Introduction
연구원 내부망을 통해 turtlebot을 제어하기 위해서, turtlebot의 인터넷과 내부망이 연결되어야 한다.<br>
하지만, 내부망은 외부 연결이 제한되어 있기 때문에 broker pc를 통하여 통신을 시도하였다.<br><br>

## Code
내부망 pc와 turtlebot은 각각 client_socket.py, client_socket2.py를 실행하고,<br>
broker pc는 server_socket.py를 실행시키면 된다.<br>
이를 통해 내부망 pc와 turtlebot의 통신이 가능하다.
