#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
import sys
import select
import termios
import tty

msg = """
========================================
JetAuto Keyboard Controller
========================================
Up Arrow    : move forward
Down Arrow  : move backward
Left Arrow  : rotate counterclockwise
Right Arrow : rotate clockwise
Space       : stop
1           : increase speed step
2           : decrease speed step
q           : quit
========================================
"""

def get_key():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)

    if rlist:
        key = sys.stdin.read(1)
        if key == '\x1b':
            key2 = sys.stdin.read(1)
            key3 = sys.stdin.read(1)
            key = key + key2 + key3
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main():
    rospy.init_node('jetauto_keyboard_controller')
    pub = rospy.Publisher('/jetauto_controller/cmd_vel', Twist, queue_size=10)

    linear_speed = 0.15
    angular_speed = 0.80

    linear_step = 0.05
    angular_step = 0.10

    min_linear_speed = 0.05
    max_linear_speed = 0.50

    min_angular_speed = 0.20
    max_angular_speed = 2.00

    current_twist = Twist()
    rate = rospy.Rate(10)

    print(msg)
    print("Controller is running...")
    print(f"Current linear speed: {linear_speed:.2f}")
    print(f"Current angular speed: {angular_speed:.2f}")

    while not rospy.is_shutdown():
        key = get_key()

        if key == '\x1b[A':      # Up arrow
            current_twist.linear.x = linear_speed
            current_twist.angular.z = 0.0
            print(f"Forward | linear_speed={linear_speed:.2f}")

        elif key == '\x1b[B':    # Down arrow
            current_twist.linear.x = -linear_speed
            current_twist.angular.z = 0.0
            print(f"Backward | linear_speed={linear_speed:.2f}")

        elif key == '\x1b[C':    # Right arrow
            current_twist.linear.x = 0.0
            current_twist.angular.z = -angular_speed
            print(f"Rotate Clockwise | angular_speed={angular_speed:.2f}")

        elif key == '\x1b[D':    # Left arrow
            current_twist.linear.x = 0.0
            current_twist.angular.z = angular_speed
            print(f"Rotate Counterclockwise | angular_speed={angular_speed:.2f}")

        elif key == ' ':
            current_twist = Twist()
            print("Stop")

        elif key == '1':
            linear_speed = min(linear_speed + linear_step, max_linear_speed)
            angular_speed = min(angular_speed + angular_step, max_angular_speed)
            print(f"Speed increased | linear={linear_speed:.2f}, angular={angular_speed:.2f}")

        elif key == '2':
            linear_speed = max(linear_speed - linear_step, min_linear_speed)
            angular_speed = max(angular_speed - angular_step, min_angular_speed)
            print(f"Speed decreased | linear={linear_speed:.2f}, angular={angular_speed:.2f}")

        elif key == 'q':
            current_twist = Twist()
            pub.publish(current_twist)
            print("Quit")
            break

        pub.publish(current_twist)
        rate.sleep()

if __name__ == '__main__':
    settings = termios.tcgetattr(sys.stdin)
    try:
        main()
    except rospy.ROSInterruptException:
        pass