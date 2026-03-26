# Project 4 Zone 1 Offline Guide for JetAuto

This guide is for **Project 4 JetAuto Mapping** using the real robot. Project 4 asks you to follow Lab 6, teleoperate the robot through the assigned area, monitor mapping in RViz, save the map, analyze the result, and submit the saved map files, a screenshot, a short real-robot RViz video, and a text file with answers. Lab 6 also gives the standard commands for the physical robot workflow, including stopping the app service, launching `gmapping`, launching RViz, and saving the map with `map:=/jetauto_1/map`. See the uploaded controller file and manuals for the baseline workflow and map saving commands. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2

---

## Assumptions used in this guide

- Robot name: `jetauto`
- Robot IP: `192.168.149.1`
- Ubuntu VM name: `ubuntu`
- You copy files from **Ubuntu VM** to the **robot**
- You connect to the robot with **NoMachine**
- You already finished the **Gazebo** part of Lab 6 successfully
- Your Project 4 assigned area is **Zone 1**

---

## Files to prepare before class

### On Ubuntu
Put these files somewhere easy to reach:

```bash
~/robotics/project4/
```

Recommended contents:

```bash
keyboard_controller_flexible.py
Project4_Zone1_Offline_Guide.md
```

---

## Part A. Pre-check on Ubuntu before you go to the robot

### Step A1. Start the Ubuntu VM
**Do this on Ubuntu**

Expected result:
- Ubuntu opens normally
- Your ROS workspace is available

If wrong:
- Start VirtualBox first
- Make sure the VM is the correct Ubuntu used in robotics

---

### Step A2. Check that the controller file exists
**Do this on Ubuntu**

```bash
ls -l /mnt/data/keyboard_controller_flexible.py
```

Expected result:
- File is listed

If wrong:
- Copy the file to Ubuntu first

---

### Step A3. Copy the controller file into your Ubuntu ROS workspace
**Do this on Ubuntu**

```bash
mkdir -p ~/ros_ws/src/lab6/scripts
cp /mnt/data/keyboard_controller_flexible.py ~/ros_ws/src/lab6/scripts/
chmod +x ~/ros_ws/src/lab6/scripts/keyboard_controller_flexible.py
```

Expected result:
- No error

If wrong:
- Make sure `~/ros_ws/src/lab6/scripts` exists
- If `lab6` does not exist on Ubuntu, create it or use the package you already use for your controller

---

### Step A4. Keep a backup of the old controller
**Do this on Ubuntu**

```bash
cp ~/ros_ws/src/lab6/scripts/keyboard_controller.py ~/ros_ws/src/lab6/scripts/keyboard_controller_backup.py
```

Expected result:
- Backup file created

If wrong:
- Skip this if you do not have an old file with that exact name

---

## Part B. Connect to the robot and copy the file

### Step B1. Make sure the robot WiFi is connected
**Do this on Ubuntu**

Your VM must be able to reach the robot network.

```bash
ping 192.168.149.1
```

Expected result:
- Replies from `192.168.149.1`

If wrong:
- Reconnect to the JetAuto access point
- If using bridged networking, verify the VM got an IP on the `192.168.149.x` network

---

### Step B2. Copy the controller to the robot
**Do this on Ubuntu**

```bash
scp ~/ros_ws/src/lab6/scripts/keyboard_controller_flexible.py jetauto@192.168.149.1:~/ros_ws/src/lab6/scripts/
```

Expected result:
- File transfers without error

If wrong:
- Confirm robot username
- Confirm the robot is reachable
- If `~/ros_ws/src/lab6/scripts` does not exist on the robot, copy to home first:

```bash
scp ~/ros_ws/src/lab6/scripts/keyboard_controller_flexible.py jetauto@192.168.149.1:~/ 
```

Then move it on the robot later

---

### Step B3. Open NoMachine to the robot
**Do this on Ubuntu**

Expected result:
- You see the robot desktop

If wrong:
- Reconnect to JetAuto WiFi
- Retry NoMachine
- If NoMachine is too slow, use SSH for commands and keep NoMachine only for the minimum visual steps. Lab 6 notes that SSH can be used if NoMachine is slow. fileciteturn0file1

---

## Part C. Robot-side setup before mapping

### Step C1. Open a terminal on the robot and move the file if needed
**Do this on Robot**

```bash
mkdir -p ~/ros_ws/src/lab6/scripts
mv ~/keyboard_controller_flexible.py ~/ros_ws/src/lab6/scripts/ 2>/dev/null || true
chmod +x ~/ros_ws/src/lab6/scripts/keyboard_controller_flexible.py
```

Expected result:
- No critical error

If wrong:
- Verify the file path using:

```bash
ls -l ~/ros_ws/src/lab6/scripts/
ls -l ~/
```

---

### Step C2. Source ROS and workspace
**Do this on Robot**

```bash
source /opt/ros/melodic/setup.bash
source ~/ros_ws/devel/setup.bash
```

Expected result:
- No error

If wrong:
- If `~/ros_ws/devel/setup.bash` does not exist, build first:

```bash
cd ~/ros_ws
catkin_make
source ~/ros_ws/devel/setup.bash
```

---

### Step C3. Stop the default app service
Lab 6 says to stop the app service before SLAM on the physical robot. fileciteturn0file1

**Do this on Robot**

```bash
sudo systemctl stop start_app_node.service
```

Expected result:
- Service stops without error

If wrong:
- Retry once
- If it says service not found, note it and continue, but expect topic conflicts later

---

### Step C4. Check current motion topics
**Do this on Robot**

```bash
rostopic list | grep cmd_vel
```

Expected result:
- You may see one or more topics such as:

```bash
/cmd_vel
/jetauto_controller/cmd_vel
/jetauto_1/jetauto_controller/cmd_vel
/jetauto_1/cmd_vel
```

If wrong:
- Continue anyway. The new controller also lets you type a custom topic manually

---

### Step C5. Check who publishes to the likely robot motion topic
**Do this on Robot**

Run these one by one if they exist:

```bash
rostopic info /jetauto_1/jetauto_controller/cmd_vel
rostopic info /jetauto_1/cmd_vel
rostopic info /jetauto_controller/cmd_vel
rostopic info /cmd_vel
```

Expected result:
- You want to find the topic that has a **Subscriber** from the robot controller side
- If you see a **Publisher** like `joystick_control`, that can hijack motion

If wrong:
- If `joystick_control` is still publishing and blocking your controller, kill it:

```bash
rosnode kill /jetauto_1/joystick_control
```

Then re-check `rostopic info`

---

## Part D. Start SLAM and RViz

### Step D1. Launch SLAM on the robot
Lab 6 uses `gmapping` on the physical robot. fileciteturn0file1

**Do this on Robot**

Standard command:

```bash
roslaunch jetauto_slam slam.launch slam_methods:=gmapping
```

If your setup has the filtered scan problem and `scan` is empty while `scan_raw` has data, use:

```bash
roslaunch jetauto_slam slam.launch slam_methods:=gmapping scan_topic:=/jetauto_1/scan_raw
```

Expected result:
- You should see messages like:
- `Initialization complete`
- `Registering First Scan`
- No repeating TF errors about missing `base_footprint` or `lidar_frame`

If wrong:
- If SLAM hangs or fails, stop it and restart:

```bash
Ctrl+C
rosnode list
```

If needed, kill stale nodes and relaunch:

```bash
rosnode kill /jetauto_1/jetauto_slam_gmapping 2>/dev/null || true
roslaunch jetauto_slam slam.launch slam_methods:=gmapping
```

- If you get TF errors, run:

```bash
rosnode list
rostopic list | egrep "scan|tf|odom|imu"
```

- If `/jetauto_1/scan` exists but shows no data, check:

```bash
rostopic info /jetauto_1/scan
rostopic info /jetauto_1/scan_raw
```

If `scan_raw` has data but `scan` does not, use the `scan_topic:=/jetauto_1/scan_raw` workaround above

---

### Step D2. Launch RViz on the robot
Lab 6 uses RViz to monitor mapping. fileciteturn0file1

**Do this on Robot**

```bash
roslaunch jetauto_slam rviz_slam.launch slam_methods:=gmapping
```

Expected result:
- RViz opens
- Map display updates when the robot moves

If wrong:
- In RViz go to **File > Open Config** and open the correct JetAuto SLAM RViz config if needed, as Lab 6 notes for RViz config issues. fileciteturn0file1
- Check that **Fixed Frame** is `map`

---

## Part E. Run the flexible controller

### Step E1. Start the controller
**Do this on Robot**

```bash
source /opt/ros/melodic/setup.bash
source ~/ros_ws/devel/setup.bash
rosrun lab6 keyboard_controller_flexible.py
```

Expected result:
- The controller prints a topic menu
- Example options may include:

```bash
1. /cmd_vel
2. /jetauto_controller/cmd_vel
3. /jetauto_1/jetauto_controller/cmd_vel
4. /jetauto_1/cmd_vel
5. other
```

If wrong:
- If `rosrun` says package not found, verify the package exists and source the workspace again
- You can also run directly:

```bash
python3 ~/ros_ws/src/lab6/scripts/keyboard_controller_flexible.py
```

---

### Step E2. Choose the topic carefully
**Do this on Robot**

Pick the topic that you already verified has the right **Subscriber** from the robot side.

Recommended order to try:

1. `/jetauto_1/jetauto_controller/cmd_vel`
2. `/jetauto_1/cmd_vel`
3. `/jetauto_controller/cmd_vel`
4. `/cmd_vel`
5. `other`

Expected result:
- The controller prints topic diagnostics using `rostopic info`
- You confirm the topic and the controller starts

If wrong:
- Cancel and re-run the controller
- Choose a different topic

---

### Step E3. Verify publisher and subscriber before driving
**Do this on Robot**

Open a new terminal and run the topic you selected. Example:

```bash
rostopic info /jetauto_1/jetauto_controller/cmd_vel
```

Expected result:
- Your keyboard controller appears under **Publishers**
- The robot side appears under **Subscribers**

If wrong:
- Your selected topic is wrong
- Re-run the controller and pick another topic

---

### Step E4. Verify that messages are actually being published
**Do this on Robot**

Open a new terminal and run the topic you selected. Example:

```bash
rostopic echo /jetauto_1/jetauto_controller/cmd_vel
```

Now press arrow keys in the controller terminal.

Expected result:
- You should see `geometry_msgs/Twist` values change

If wrong:
- The controller is not publishing correctly
- Restart the controller
- Confirm the controller terminal still has focus

---

### Step E5. Test direct motion if needed
**Do this on Robot**

If the controller still does not move the robot, test the candidate topics directly.

```bash
rostopic pub /jetauto_1/jetauto_controller/cmd_vel geometry_msgs/Twist '{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' -r 5
```

If no motion, test:

```bash
rostopic pub /jetauto_1/cmd_vel geometry_msgs/Twist '{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' -r 5
```

Then:

```bash
rostopic pub /jetauto_controller/cmd_vel geometry_msgs/Twist '{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' -r 5
```

Expected result:
- One of these should move the robot

If wrong:
- Re-check service conflicts
- Re-check `rostopic info` and `rosnode list`
- Kill joystick again if it returns

---

## Part F. Mapping Zone 1

Project 4 says to map the assigned zone and monitor the process in RViz. The uploaded project sheet marks the hallway **Zone 1** on the plan. fileciteturn0file2

### Step F1. Start slowly
**Do this on Robot while watching RViz**

Use the new keys:

- `f` to increase speed
- `s` to decrease speed
- `space` to stop

Suggested mapping speed:
- Start low
- Use very low speed near corners and obstacles
- Do not rush turns

Expected result:
- RViz shows walls becoming continuous
- The map is not broken into scattered arcs

If wrong:
- Slow down
- Stop and let scans settle
- Relaunch SLAM if the map stops updating

---

### Step F2. Cover all of Zone 1
**Do this on Robot**

Goal:
- Cover the entire Zone 1 hallway
- Revisit gaps if walls look broken
- Avoid very sharp, fast turns

Expected result:
- Continuous hallway boundaries
- Openings appear where doors or hall gaps are located

If wrong:
- Drive that section again more slowly
- Keep the robot farther from obstacles when possible

---

### Step F3. Record the required short video
Project 4 requires a short real-robot RViz video. fileciteturn0file2

**Do this on Ubuntu or with your phone if needed**

Capture:
- Real robot moving
- RViz showing the map updating

Expected result:
- Short video clearly shows live mapping

If wrong:
- Record again before closing RViz

---

## Part G. Save the Zone 1 map

Lab 6 says that on the physical robot you should save the map from `/jetauto_1/map`. fileciteturn0file1

### Step G1. Save the map on the robot
**Do this on Robot**

```bash
roscd jetauto_slam/maps
rosrun map_server map_saver -f zone1_map map:=/jetauto_1/map
```

Expected result:
- You should see lines similar to:
- `Waiting for the map`
- `Received a ... map`
- `Writing map occupancy data to zone1_map.pgm`
- `Writing map occupancy data to zone1_map.yaml`
- `Done`

If wrong:
- Check whether SLAM is still running
- Check whether `/jetauto_1/map` exists:

```bash
rostopic list | grep map
```

---

### Step G2. Verify the files exist
**Do this on Robot**

```bash
ls -l $(rospack find jetauto_slam)/maps | grep zone1_map
```

Expected result:
- `zone1_map.pgm`
- `zone1_map.yaml`

If wrong:
- Save again with the same command

---

## Part H. Copy the saved files back to Ubuntu

### Step H1. Copy files from robot to Ubuntu
**Do this on Ubuntu**

```bash
mkdir -p ~/project4_submission/zone1
scp jetauto@192.168.149.1:$(ssh jetauto@192.168.149.1 'rospack find jetauto_slam')/maps/zone1_map.pgm ~/project4_submission/zone1/
scp jetauto@192.168.149.1:$(ssh jetauto@192.168.149.1 'rospack find jetauto_slam')/maps/zone1_map.yaml ~/project4_submission/zone1/
```

If shell substitution over ssh is annoying, use the exact absolute path shown by this on the robot:

```bash
rospack find jetauto_slam
```

Then copy with the full path.

Expected result:
- Both files are copied

If wrong:
- First run `rospack find jetauto_slam` on the robot manually and copy the exact path

---

### Step H2. Open the map image and take the required screenshot
Project 4 requires a screenshot of the generated map and analysis of any issues. fileciteturn0file2

**Do this on Ubuntu**

```bash
eog ~/project4_submission/zone1/zone1_map.pgm
```

Expected result:
- The occupancy map opens

If wrong:
- Confirm the file copied correctly

What to look for in the screenshot:
- Continuous corridor walls
- Missing sections
- Double walls caused by drift
- Noisy or scattered points

---

## Part I. Fast recovery checklist for common failures

### Case 1. SLAM is running but RViz map is not updating
**Check on Robot**

```bash
rostopic list | egrep "scan|map|tf|odom"
rostopic info /jetauto_1/scan
rostopic info /jetauto_1/scan_raw
```

Fix:
- If `scan` is empty but `scan_raw` has data, relaunch with:

```bash
roslaunch jetauto_slam slam.launch slam_methods:=gmapping scan_topic:=/jetauto_1/scan_raw
```

---

### Case 2. TF errors mention missing `base_footprint` or `lidar_frame`
**Check on Robot**

```bash
rosnode list
rostopic echo -n 5 /tf
```

Fix:
- Stop SLAM and relaunch
- Make sure the robot sensor nodes are up before running RViz

---

### Case 3. The robot does not move
**Check on Robot**

```bash
rostopic list | grep cmd_vel
rostopic info /your_selected_topic_here
rostopic echo /your_selected_topic_here
```

Fix:
- Re-run the controller and pick another topic
- Test direct publish with `rostopic pub`
- Kill joystick if it comes back:

```bash
rosnode kill /jetauto_1/joystick_control
```

---

### Case 4. SLAM crashes or freezes
**Do this on Robot**

```bash
rosnode kill /jetauto_1/jetauto_slam_gmapping 2>/dev/null || true
roslaunch jetauto_slam slam.launch slam_methods:=gmapping
```

If needed, fully reset ROS terminals and relaunch the workflow.

---

### Case 5. NoMachine is too slow
Lab 6 mentions doing robot-side services through SSH when remote desktop is slow. fileciteturn0file1

Use:
- Robot commands over SSH
- RViz only where needed
- Phone video if screen capture is too slow

---

## Part J. Submission checklist

Project 4 asks for these items. fileciteturn0file2

- `map.pgm` and `map.yaml` from the classroom
- `map.pgm` and `map.yaml` from the assigned zone, which is Zone 1 in your case
- Screenshot of the map with notes on quality or errors
- Short RViz video using the real robot
- Text file with the answers to the assessment questions

Recommended filenames:

```bash
classroom_map.pgm
classroom_map.yaml
zone1_map.pgm
zone1_map.yaml
answers.txt
zone1_map_screenshot.png
rviz_zone1_mapping.mp4
```

---

## Part K. Commands only quick reference

### Ubuntu

```bash
ping 192.168.149.1
scp ~/ros_ws/src/lab6/scripts/keyboard_controller_flexible.py jetauto@192.168.149.1:~/ros_ws/src/lab6/scripts/
mkdir -p ~/project4_submission/zone1
```

### Robot

```bash
source /opt/ros/melodic/setup.bash
source ~/ros_ws/devel/setup.bash
sudo systemctl stop start_app_node.service
rostopic list | grep cmd_vel
rostopic info /jetauto_1/jetauto_controller/cmd_vel
rostopic info /jetauto_1/cmd_vel
roslaunch jetauto_slam slam.launch slam_methods:=gmapping
roslaunch jetauto_slam rviz_slam.launch slam_methods:=gmapping
rosrun lab6 keyboard_controller_flexible.py
roscd jetauto_slam/maps
rosrun map_server map_saver -f zone1_map map:=/jetauto_1/map
```

### Emergency motion tests on Robot

```bash
rostopic pub /jetauto_1/jetauto_controller/cmd_vel geometry_msgs/Twist '{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' -r 5
rostopic pub /jetauto_1/cmd_vel geometry_msgs/Twist '{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' -r 5
rostopic pub /jetauto_controller/cmd_vel geometry_msgs/Twist '{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' -r 5
rosnode kill /jetauto_1/joystick_control
```
