#!/bin/bash
set -e

echo "Cleaning up broken ROS snapshot repositories..."
# This MUST happen before any apt-get update runs, or the script will crash
rm -f /etc/apt/sources.list.d/ros2-snapshots.list

echo "Installing system dependencies..."
apt-get update
apt-get install -y ros-iron-navigation2 ros-iron-nav2-bringup ros-iron-slam-toolbox
rm -f /etc/apt/sources.list.d/ros2-snapshots.list

echo "NUCLEAR CLEAN of Python ML stack..."
rm -rf /usr/local/lib/python3.10/dist-packages/numpy*
rm -rf /usr/local/lib/python3.10/dist-packages/scipy*
rm -rf /usr/local/lib/python3.10/dist-packages/sklearn*
rm -rf /usr/local/lib/python3.10/dist-packages/numpy-*.dist-info

rm -rf ~/.local/lib/python3.10/site-packages/numpy*
rm -rf ~/.local/lib/python3.10/site-packages/scipy*
rm -rf ~/.local/lib/python3.10/site-packages/sklearn*

echo "Resetting Python ML stack base..."
apt-get update
apt-get install -y --reinstall \
  python3-numpy \
  python3-scipy

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
#   (Moved up so its dependencies don't hijack scikit-learn later)
git clone https://github.com/gabe-ochoa/lidar-tracking.git /tmp/lidar-tracking
sed -i 's/requires-python = ">=3.11"/requires-python = ">=3.10"/' /tmp/lidar-tracking/pyproject.toml
pip install /tmp/lidar-tracking
rm -rf /tmp/lidar-tracking
#------------------------------------------------------------------

echo "Installing requested scikit-learn version..."
# We use --force-reinstall to override any version pulled by lidar-tracking
pip install --no-cache-dir --force-reinstall scikit-learn==1.3.2

apt update
apt install -y ros-iron-rmw-cyclonedds-cpp

echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc

# Final cleanup of leftover metadata
rm -rf /usr/local/lib/python3.10/dist-packages/numpy-*.dist-info

echo "Verifying environment..."
python3 -c "
import numpy
import sklearn
print('NumPy version:', numpy.__version__)
print('NumPy path:', numpy.__file__)
print('Scikit-learn version:', sklearn.__version__)
print('Scikit-learn path:', sklearn.__file__)
"

echo "Setup complete."