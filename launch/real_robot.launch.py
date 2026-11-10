"""실제 FAIRINO FR3를 MoveIt2 + RViz2로 제어하는 런치.

demo.launch.py와 같지만 ros2_control 하드웨어를 mock 대신
fairino_hardware/FairinoHardwareInterface(ServoJ)로 바꾼다.

주의: generate_demo_launch()는 패키지의 rsp/move_group 런치 파일을 include하고,
그 파일들이 MoveItConfigsBuilder를 매핑 없이 다시 만들기 때문에 mock 하드웨어가 뜬다.
그래서 여기서는 같은 moveit_config로 각 구성요소를 직접 생성한다.

실행: ros2 launch fairino3_v6_moveit2_config real_robot.launch.py controller_ip:=192.168.57.2
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import (
    generate_move_group_launch,
    generate_moveit_rviz_launch,
    generate_rsp_launch,
    generate_spawn_controllers_launch,
)


def _launch_setup(context):
    controller_ip = LaunchConfiguration("controller_ip").perform(context)
    moveit_config = (
        MoveItConfigsBuilder("fairino3_v6_robot", package_name="fairino3_v6_moveit2_config")
        .robot_description(mappings={"use_fake_hardware": "false", "controller_ip": controller_ip})
        .to_moveit_configs()
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[str(moveit_config.package_path / "config/ros2_controllers.yaml")],
        remappings=[("/controller_manager/robot_description", "/robot_description")],
        output="screen",
    )

    entities = []
    for ld in (
        generate_rsp_launch(moveit_config),
        generate_move_group_launch(moveit_config),
        generate_moveit_rviz_launch(moveit_config),
    ):
        entities += ld.entities
    entities.append(ros2_control_node)
    entities += generate_spawn_controllers_launch(moveit_config).entities
    return entities


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("controller_ip", default_value="192.168.58.2",
                              description="FAIRINO 컨트롤러 IP (SDK 포트 20003/20004)"),
        OpaqueFunction(function=_launch_setup),
    ])
