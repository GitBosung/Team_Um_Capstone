[한림대학교 SW중심대학 사업] 2025 1학기 Capstone Design(종합설계) 프로젝트 결과 파일을 담고 있습니다.

# Team Um Capstone: 차세대 실내 항법 기술 개발

## 개요
본 프로젝트는 GPS 신호가 닿지 않는 실내 환경에서 **PDR(Pedestrian Dead Reckoning)** 의 누적 오차를 **Wi-Fi/BLE 무선 신호** 기반의 핑거프린팅 기법과 결합한 **Surface Correlation (SC)** 알고리즘으로 보정하여, 정확하고 안정적인 실내 위치 추정 시스템을 구현하는 것을 목표로 한다. 


- **과제 배경**  
  - GPS는 실내에서 신호 감쇠로 인해 위치 오차가 크게 증가  
  - 기존 PDR은 관성센서 누적 오차(드리프트)가 장시간 운용에 한계  
  - Fingerprinting 방식은 환경 변화에 취약  

- **과제 목적**  
  - PDR 궤적 정보와 누적 RSSI 시퀀스를 결합한 SC 기법으로 PDR 누적 오차 보정  
  - 실제 실내 환경(한림대학교 공학관 3층)에서 성능 검증  

---

## 주요 기능
1. **Android 앱 (`App/NNL_SensorLogger-capstone`)**  
   - 라디오맵 빌더: 1 m 격자 기반으로 특정 좌표에서 4 초간 Wi-Fi 스캔 후 CSV 저장  
   - IMU(50 Hz) + RSSI(0.25 Hz) 동시 로깅: 걸으면서 센서·무선신호 동기 저장  

2. **웨어러블 디바이스 펌웨어 (`Arduino/`)**  
   - Arduino Nano 33 BLE Sense 기반 저전력 스마트밴드  
   - BLE로 20 Hz IMU 데이터 전송 및 스마트폰 저장  

3. **PDR 알고리즘 (`PDR_RSSI/`)**  
   - 걸음 검출(피크 탐지) → 쿼터니언 보정 → ENU 좌표 적분  
   - Δx = L·sin ψ, Δy = L·cos ψ 공식에 따라 보행 궤적 생성
   - 획득한 PDR 궤적과 시간대별로 수집된 RSSI 벡터를 매칭

4. **Surface Correlation 알고리즘 (`SC/`)**  
   - PDR 궤적에 따라 수집된 누적 RSSI 시퀀스(URS)와 라디오맵 상관도 계산  
   - 최고 상관도를 보이는 위치를 실내 위치 추정 결과로 반환  

5. **라디오맵 구축 스크립트 (`RadioMap/`)**  
   - 1 m 격자 설계 → 각 RP에서 Wi-Fi 스캔 → CSV 저장 및 시각화  

---

## 폴더 구조
├── App/NNL_SensorLogger-capstone # Android 앱 소스
├── Arduino/ # 스마트밴드 펌웨어 (Arduino IDE)
├── PDR_RSSI/ # PDR 및 RSSI 데이터 처리 파이프라인
├── RadioMap/ # 라디오맵 수집·보간·시각화 스크립트
├── SC/ # Surface Correlation 알고리즘 구현
├── LICENSE # MIT 라이선스
└── README.md # 프로젝트 개요 및 사용법

---

## 사용 예시
# 1) Android 앱으로 CSV 데이터 수집-
# 2) `RadioMap/`에서 라디오맵 구축
# 3) `PDR_RSSI/`로 PDR + RSSI 전처리
# 4) `SC/`로 최종 위치 추정

---
##라이선스
#이 프로젝트는 MIT 라이선스를 따릅니다.

> **문의**: 김보성 (kimbosung1217@gmail.com / GitHub: [GitBosung](https://github.com/GitBosung)
