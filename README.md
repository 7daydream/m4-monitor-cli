# 🖥️ m4-monitor-cli

맥미니 M4 환경에서 시스템 리소스를 실시간으로 모니터링하기 위한 경량 CLI 도구입니다.

## 🚀 주요 기능
- **Real-time Monitoring:** CPU, Memory, Disk 사용량을 1초 단위로 갱신합니다.
- **Rich UI:** 터미널 내에서 시각적인 게이지 바와 테이블을 제공합니다.
- **Apple Silicon Optimized:** M4 칩 환경의 리소스 관리에 최적화된 `psutil` 기반 로직을 사용합니다.

## 🛠️ 기술 스택
- **Language:** Python 3.x
- **Libraries:** 
  - `psutil`: 하드웨어 정보 추출
  - `rich`: 터미널 UI 렌더링

## 📦 설치 및 실행 방법
1. 저장소 클론:
   ```bash
   git clone [https://github.com/7daydream/m4-monitor-cli.git](https://github.com/7daydream/m4-monitor-cli.git)
   cd m4-monitor-cli
