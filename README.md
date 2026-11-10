# FAIRINO FR3 + DH AG-140 구동 환경 기록

FAIRINO FR3 협동로봇과 DH 그리퍼를 PC에서 구동할 때 실제로 동작을 확인한 SDK·드라이버 버전 조합입니다.

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

`fairino_hardware_v3_8_2_11` 패키지에 들어 있던 SDK(2.2.2)의 헤더와 라이브러리를 위 SDK 2.2.6으로 교체해서 씁니다.

### 동작하지 않았던 조합

| SDK | 증상 |
|---|---|
| 2.2.2 (패키지 기본 포함) | `ServoJ` 인자가 7개라 컨트롤러가 거부 (오류 -502 / -4) |
| 2.3.0 (`fairino_hardware_v3_9_0`) | `error SDK version`으로 연결 거부 |

`fairino_hardware_v3_9_0`은 플러그인 이름이 겹치므로 `COLCON_IGNORE`를 두어 빌드에서 뺍니다.

## 연결

- 컨트롤 박스 랜 포트는 2개입니다. `192.168.58.2`는 웹 화면과 SDK, `192.168.57.2`는 SDK 전용입니다. 펜던트가 58.2 쪽을 쓰므로 PC는 57.2로 붙습니다.
- 포트: `20003` XML-RPC (`http://<컨트롤러 IP>:20003/RPC2`), `20004` 실시간 상태 스트림(약 100 Hz).
- 외부에서 `ServoJ`로 움직이려면 펜던트에서 자동 모드로 바꿔야 합니다.

## 실행

```bash
ros2 launch fairino3_v6_moveit2_config real_robot.launch.py controller_ip:=192.168.57.2
```

`real_robot.launch.py`는 원본 저장소에 없는 파일로, 직접 추가한 것입니다.

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
