# FAIRINO FR3 + DH AG-140 구동 환경 기록

FAIRINO FR3 협동로봇과 DH 그리퍼를 PC에서 구동할 때 실제로 동작을 확인한 SDK·드라이버 버전 조합입니다.

## 요약: 같은 하드웨어라면 이것을 설치하면 됩니다

1. Ubuntu 24.04 + ROS 2 Jazzy
2. 제조사 ROS 2 드라이버 `frcobot_ros2` (커밋 `fcf0c7f`) 중 `fairino_hardware_v3_8_2_11` 패키지
3. 제조사 C++ SDK `fairino-cpp-sdk`의 `3.8.6` 브랜치 (라이브러리 버전 2.2.6)
4. 이 저장소의 패치와 런치 파일

SDK 버전은 컨트롤러 소프트웨어 버전과 맞아야 합니다. 여기 조합은 컨트롤러 소프트웨어 3.8.6 기준입니다. 컨트롤러 버전이 다르면 SDK 저장소에서 그 버전에 해당하는 브랜치를 써야 하며, 맞지 않으면 아래 "동작하지 않았던 조합"처럼 연결이나 명령이 거부됩니다. 컨트롤러 버전은 펜던트(웹 화면)의 시스템 정보에서 확인합니다.

그리퍼는 PC에 따로 설치할 것이 없고, 펜던트에서 등록만 하면 됩니다.

구체적인 명령은 아래 "설치 순서"에 있습니다.

## 장비

| 항목 | 내용 |
|---|---|
| 로봇팔 | FAIRINO FR3 (6축 협동로봇, `frcobot_ros2`에서의 모델명 `fairino3_v6`) |
| 그리퍼 | DH Robotics AG-140-165 (펜던트에는 DH "PGI-140" 유형으로 등록) |
| PC | Ubuntu 24.04, ROS 2 Jazzy |

## 소프트웨어 버전

| 항목 | 버전 |
|---|---|
| ROS 2 드라이버 | [FAIR-INNOVATION/frcobot_ros2](https://github.com/FAIR-INNOVATION/frcobot_ros2) `main` 브랜치, 커밋 `fcf0c7f` (2026-09-23) |
| 사용 패키지 | `fairino_hardware_v3_8_2_11`, `fairino3_v6_moveit2_config` |
| C++ SDK | [FAIR-INNOVATION/fairino-cpp-sdk](https://github.com/FAIR-INNOVATION/fairino-cpp-sdk) `3.8.6` 브랜치, 커밋 `d560292` (`libfairino.so.2.2.6`) |

`fairino_hardware_v3_8_2_11` 패키지에 들어 있던 SDK(2.2.2)의 헤더와 라이브러리를 위 SDK 2.2.6으로 교체해서 씁니다. 방법은 아래 설치 순서에 있습니다.

### 동작하지 않았던 조합

| SDK | 증상 |
|---|---|
| 2.2.2 (패키지 기본 포함) | `ServoJ` 인자가 7개라 컨트롤러가 거부 (오류 -502 / -4) |
| 2.3.0 (`fairino_hardware_v3_9_0`) | `error SDK version`으로 연결 거부 |

버전별 하드웨어 패키지는 플러그인 이름이 겹치므로 함께 빌드하지 않습니다. 아래 설치 순서처럼 필요한 패키지만 골라 빌드하거나, 쓰지 않는 패키지 폴더에 `COLCON_IGNORE` 파일을 둡니다.

## 설치 순서

Ubuntu 24.04에 ROS 2 Jazzy가 설치되어 있다고 가정합니다.

**1. ROS 패키지 설치**

```bash
sudo apt install ros-jazzy-moveit ros-jazzy-ros2-control ros-jazzy-ros2-controllers
```

**2. 드라이버와 SDK 받기**

```bash
mkdir -p ~/fairino_ws/src ~/fairino_ws/third_party
cd ~/fairino_ws/src
git clone https://github.com/FAIR-INNOVATION/frcobot_ros2.git
cd frcobot_ros2 && git checkout fcf0c7f

cd ~/fairino_ws/third_party
git clone -b 3.8.6 https://github.com/FAIR-INNOVATION/fairino-cpp-sdk.git fairino-cpp-sdk-3.8.6
```

**3. 드라이버 패키지의 SDK를 2.2.6으로 교체**

SDK 저장소에 들어 있는 미리 빌드된 x86 라이브러리와 헤더를 그대로 복사합니다.

```bash
SDK=~/fairino_ws/third_party/fairino-cpp-sdk-3.8.6/linux/libfairino
PKG=~/fairino_ws/src/frcobot_ros2/fairino_hardware_v3_8_2_11/libfairino
cp $SDK/include/robot.h $SDK/include/robot_error.h $SDK/include/robot_types.h $PKG/include/
cp $SDK/lib/x86/lib/libfairino.so.2.2.6 $PKG/lib/
```

**4. 이 저장소의 패치와 런치 파일 적용**

```bash
git clone https://github.com/ImJoonHyung/fairino-fr3-dh-setup.git ~/fairino-fr3-dh-setup
cd ~/fairino_ws/src/frcobot_ros2
git apply ~/fairino-fr3-dh-setup/patches/frcobot_ros2-fcf0c7f.patch
cp ~/fairino-fr3-dh-setup/launch/real_robot.launch.py fairino3_v6_moveit2_config/launch/
```

패치가 바꾸는 내용:

- 빌드가 SDK 2.2.6을 링크하도록 변경하고, SDK 2.2.6에서 빌드되지 않는 `ros2_cmd_server`는 기본으로 끔
- 컨트롤러 IP를 런치 인자로 지정할 수 있게 함
- 실제 로봇용 하드웨어 플러그인을 선택할 수 있게 함(`use_fake_hardware`)
- 제어 주기를 `ServoJ` 주기(8 ms)에 맞춰 125 Hz로 변경, 관절 가속도 제한 추가
- `ServoJ`가 연속 25회 거부되면 하드웨어를 정지

**5. 빌드**

저장소에 버전별 하드웨어 패키지가 여러 개 있고 플러그인 이름이 겹치므로, 필요한 패키지만 골라 빌드합니다.

```bash
cd ~/fairino_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select fairino_msgs fairino_description fairino_hardware_v3_8_2_11 fairino3_v6_moveit2_config
source install/setup.bash
```

**6. 그리퍼 등록**

그리퍼는 로봇 끝단 커넥터에 연결하고, 펜던트의 그리퍼 설정에서 DH "PGI-140" 유형으로 등록합니다. AG-140 전용 항목은 없지만 이 설정으로 동작합니다. PC 쪽에 따로 설치할 것은 없습니다.

## 연결

- 컨트롤 박스 랜 포트는 2개입니다. `192.168.58.2`는 웹 화면과 SDK, `192.168.57.2`는 SDK 전용입니다. 펜던트가 58.2 쪽을 쓰므로 PC는 57.2로 붙습니다.
- 포트: `20003` XML-RPC (`http://<컨트롤러 IP>:20003/RPC2`), `20004` 실시간 상태 스트림(약 100 Hz).
- 외부에서 `ServoJ`로 움직이려면 펜던트에서 자동 모드로 바꿔야 합니다.

## 실행

```bash
ros2 launch fairino3_v6_moveit2_config real_robot.launch.py controller_ip:=192.168.57.2
```

`real_robot.launch.py`는 원본 저장소에 없는 파일로, 이 저장소의 `launch/`에 들어 있습니다.

## 그리퍼

XML-RPC로 직접 호출합니다.

```python
MoveGripper(1, pos, vel, force, 3000, block, 0, 0.0, 0, 0)
# pos: 100 = 열림, 0 = 닫힘 (%)
# block: 0 = 끝날 때까지 대기, 1 = 바로 반환
```

힘 30%에서 전체 스트로크는 약 2.7초이고, 명령 후 움직이기 시작할 때까지 약 0.9초 걸립니다.

## 주의

- XML-RPC `system.listMethods`를 호출한 직후 컨트롤러의 20003/20004 포트가 닫힌 적이 있습니다. 호출하지 않는 것이 안전합니다.
- 포트가 열려 있는지 확인하려고 빈 TCP 연결만 열었다 닫는 것도 피합니다. 그 직후 제어 프로그램이 죽은 적이 있습니다.
