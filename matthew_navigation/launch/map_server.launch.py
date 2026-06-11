from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from launch_ros.actions import LifecycleNode
from launch_ros.actions import ExecuteProcess


def generate_launch_description():

    map_yaml = "/ros_ws/src/matthew_summer26/maps/baseline_map.yaml"

    # Map server (Nav2 lifecycle node)
    map_server = LifecycleNode(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[{
            "yaml_filename": map_yaml,
            "use_sim_time": True
        }],
    )

    # Auto-configure + activate lifecycle node
    # (so you don't have to manually run ros2 lifecycle commands)
    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_map",
        output="screen",
        parameters=[{
            "use_sim_time": True,
            "autostart": True,
            "node_names": ["map_server"]
        }],
    )

    return LaunchDescription([
        map_server,
        lifecycle_manager
    ])