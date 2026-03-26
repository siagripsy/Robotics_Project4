#!/usr/bin/env python3
import select
import subprocess
import sys
import termios
import tty
from typing import List

import rospy
from geometry_msgs.msg import Twist

HELP_MSG = """
========================================
JetAuto Flexible Keyboard Controller
========================================
Movement
  Up Arrow    : move forward
  Down Arrow  : move backward
  Left Arrow  : rotate counterclockwise
  Right Arrow : rotate clockwise
  Space       : stop

Speed
  f           : increase speed
  s           : decrease speed

Other
  h           : show this help again
  q           : quit
========================================
"""

DEFAULT_TOPICS = [
    "/cmd_vel",
    "/jetauto_controller/cmd_vel",
    "/jetauto_1/jetauto_controller/cmd_vel",
    "/jetauto_1/cmd_vel",
]


settings = None


def run_command(command: List[str]) -> str:
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return f"ERROR: {exc}"



def detect_cmd_vel_topics() -> List[str]:
    output = run_command(["rostopic", "list"])
    if output.startswith("ERROR:"):
        return []

    detected = []
    for line in output.splitlines():
        topic = line.strip()
        if "cmd_vel" in topic and topic not in detected:
            detected.append(topic)
    return detected



def build_topic_menu() -> List[str]:
    topics = []
    for topic in DEFAULT_TOPICS + detect_cmd_vel_topics():
        if topic not in topics:
            topics.append(topic)
    return topics



def show_topic_diagnostics(topic: str) -> None:
    print("\nSelected topic:", topic)
    print("\nTopic diagnostics:")
    info_output = run_command(["rostopic", "info", topic])
    print(info_output)
    print("\nQuick checks you can run in another terminal:")
    print(f"  rostopic info {topic}")
    print(f"  rostopic echo {topic}")
    print("  rostopic list | grep cmd_vel")
    print("  rosnode list")



def choose_topic() -> str:
    topics = build_topic_menu()

    print("\nAvailable cmd_vel topic options:")
    for idx, topic in enumerate(topics, start=1):
        print(f"  {idx}. {topic}")
    print(f"  {len(topics) + 1}. other")

    while True:
        choice = input("\nSelect the topic number to publish to: ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        selected = int(choice)
        if 1 <= selected <= len(topics):
            topic = topics[selected - 1]
            show_topic_diagnostics(topic)
            confirm = input("\nUse this topic? [y/n]: ").strip().lower()
            if confirm in {"y", "yes", ""}:
                return topic
        elif selected == len(topics) + 1:
            custom_topic = input("Enter the full topic name: ").strip()
            if not custom_topic:
                print("Topic name cannot be empty.")
                continue
            if not custom_topic.startswith("/"):
                custom_topic = "/" + custom_topic
            show_topic_diagnostics(custom_topic)
            confirm = input("\nUse this topic? [y/n]: ").strip().lower()
            if confirm in {"y", "yes", ""}:
                return custom_topic
        else:
            print("Invalid selection. Try again.")



def get_key() -> str:
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)

    if rlist:
        key = sys.stdin.read(1)
        if key == "\x1b":
            key2 = sys.stdin.read(1)
            key3 = sys.stdin.read(1)
            key = key + key2 + key3
    else:
        key = ""

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key



def main() -> None:
    selected_topic = choose_topic()

    rospy.init_node("jetauto_keyboard_controller")
    pub = rospy.Publisher(selected_topic, Twist, queue_size=10)

    linear_speed = 0.08
    angular_speed = 0.50

    linear_step = 0.01
    angular_step = 0.05

    min_linear_speed = 0.02
    max_linear_speed = 0.50

    min_angular_speed = 0.10
    max_angular_speed = 2.00

    current_twist = Twist()
    rate = rospy.Rate(10)

    print("\n" + HELP_MSG)
    print(f"Publishing to: {selected_topic}")
    print("Controller is running...")
    print(f"Current linear speed: {linear_speed:.2f}")
    print(f"Current angular speed: {angular_speed:.2f}")

    while not rospy.is_shutdown():
        key = get_key()

        if key == "\x1b[A":
            current_twist.linear.x = linear_speed
            current_twist.angular.z = 0.0
            print(f"Forward | linear_speed={linear_speed:.2f}")

        elif key == "\x1b[B":
            current_twist.linear.x = -linear_speed
            current_twist.angular.z = 0.0
            print(f"Backward | linear_speed={linear_speed:.2f}")

        elif key == "\x1b[C":
            current_twist.linear.x = 0.0
            current_twist.angular.z = -angular_speed
            print(f"Rotate Clockwise | angular_speed={angular_speed:.2f}")

        elif key == "\x1b[D":
            current_twist.linear.x = 0.0
            current_twist.angular.z = angular_speed
            print(f"Rotate Counterclockwise | angular_speed={angular_speed:.2f}")

        elif key == " ":
            current_twist = Twist()
            print("Stop")

        elif key.lower() == "f":
            linear_speed = min(linear_speed + linear_step, max_linear_speed)
            angular_speed = min(angular_speed + angular_step, max_angular_speed)
            print(f"Speed increased | linear={linear_speed:.2f}, angular={angular_speed:.2f}")

        elif key.lower() == "s":
            linear_speed = max(linear_speed - linear_step, min_linear_speed)
            angular_speed = max(angular_speed - angular_step, min_angular_speed)
            print(f"Speed decreased | linear={linear_speed:.2f}, angular={angular_speed:.2f}")

        elif key.lower() == "h":
            print(HELP_MSG)
            print(f"Publishing to: {selected_topic}")
            print(f"Current linear speed: {linear_speed:.2f}")
            print(f"Current angular speed: {angular_speed:.2f}")

        elif key.lower() == "q":
            current_twist = Twist()
            pub.publish(current_twist)
            print("Quit")
            break

        pub.publish(current_twist)
        rate.sleep()


if __name__ == "__main__":
    settings = termios.tcgetattr(sys.stdin)
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
