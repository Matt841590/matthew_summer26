#!/bin/bash
set -e

echo "Installing system dependencies..."
apt-get install -y ros-iron-navigation2 ros-iron-nav2-bringup ros-iron-slam-toolbox

echo "Installing Python packages..."
# - pip3 install ...

echo "Setting up ROS environment..."
echo 'source /opt/ros/iron/setup.bash' >> ~/.bashrc
echo 'source /ros_ws/install/setup.bash' >> ~/.bashrc

echo "Setting DDS implementation..."
# - this bit was AI help as I had NO CLUE what i was doing
#----------------------------------------------------------------
rm -f /etc/apt/sources.list.d/ros2-snapshots.list
apt-get clean

apt-get update
apt-get install -y curl gnupg lsb-release

curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  | gpg --dearmor \
  | tee /usr/share/keyrings/ros-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | tee /etc/apt/sources.list.d/ros2.list > /dev/null

apt-get update

# - Clone, patch, and install the lidar tracking library
git clone https://github.com/gabe-ochoa/lidar-tracking.git /tmp/lidar-tracking
sed -i 's/requires-python = ">=3.11"/requires-python = ">=3.10"/' /tmp/lidar-tracking/pyproject.toml
pip install /tmp/lidar-tracking
rm -rf /tmp/lidar-tracking
#------------------------------------------------------------------
apt install -y ros-iron-rmw-cyclonedds-cpp

echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc

echo "Setup complete."