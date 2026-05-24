import os
import sys
import subprocess

# 표준 출력을 UTF-8로 강제 재설정하여 인코딩 오류 방지
if sys.stdout and sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def initialize_environment():
    print("[1/3] 프로그램 구동 환경 검증 중...")
    
    # 실행 파일 기준으로 현재 위치(상대 경로) 계산
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
    sdk_path = os.path.abspath(os.path.join(current_dir, "android_sdk"))
    avd_manager_path = os.path.join(sdk_path, "cmdline-tools", "latest", "bin", "avdmanager")
    
    if sys.platform == "win32":
        avd_manager_path += ".bat"

    # 1. splatnet3-token-util용 config.txt 자동 생성/보정
    config_path = os.path.join(current_dir, "config.txt")
    print(f" -> config.txt 설정 파일 생성 중... (AVD: NSA)")
    
    # 기존 원본 툴이 요구하는 설정 규격에 맞게 덮어씁니다.
    config_data = {
        "avd_name": "NSA",
        "sdk_path": sdk_path.replace("\\", "/")  # 경로 역슬래시 치환
    }
    
    with open(config_path, "w", encoding="utf-8") as f:
        for key, val in config_data.items():
            f.write(f'{key}="{val}"\n')

    # 2. 가상 기기(AVD) 'NSA' 존재 여부 체크 및 자동 생성
    print("[2/3] 안드로이드 가상 기기(AVD) 상태 확인 중...")
    
    # avd_home 경로를 현재 폴더 내부로 고정하여 사용자 PC의 원래 환경과 격리시킵니다.
    avd_home_dir = os.path.join(current_dir, ".android")
    os.environ["ANDROID_AVD_HOME"] = avd_home_dir
    os.makedirs(avd_home_dir, exist_ok=True)

    # 이미 NSA 가상기기가 만들어져 있는지 확인
    avd_ini_path = os.path.join(avd_home_dir, "NSA.ini")
    if os.path.exists(avd_ini_path):
        print(" -> ✅ 'NSA' 가상 기기가 이미 준비되어 있습니다.")
    else:
        print(" -> 📥 'NSA' 가상 기기(Pixel 4 / API 30)를 최초 생성합니다. (약 5초 소요)")
        
        # avdmanager create avd 명령을 백그라운드로 실행
        # --force를 주어 혹시 모를 찌꺼기 파일을 덮어쓰고, 인풋 창 무시를 위해 echo "no"를 던집니다.
        cmd = [
            avd_manager_path,
            "create", "avd",
            "-n", "NSA",
            "-k", "system-images;android-30;google_apis;x86_64" if sys.platform == "win32" else "system-images;android-30;google_apis;arm64-v8a",
            "-d", "pixel_4",
            "--force"
        ]
        
        try:
            # 커스텀 디바이스 생성 질문에 자동으로 'no' 처리하기 위한 파이프라인 구성
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input="no\n")
            print(" -> ✅ 가상 기기 생성 성공!")
        except Exception as e:
            print(f" -> ❌ 가상 기기 생성 실패: {e}")
            return False

    # 3. 렌더링 및 부팅 옵션 강제 최적화 (Cold Boot 고정)
    print("[3/3] 에뮬레이터 하드웨어 가속 및 Cold Boot 옵션 최적화 중...")
    nsa_avd_dir = os.path.join(avd_home_dir, "NSA.avd")
    os.makedirs(nsa_avd_dir, exist_ok=True)
    
    config_ini_path = os.path.join(nsa_avd_dir, "config.ini")
    
    # 일반인 PC 사양을 타지 않게 만드는 마법의 에뮬레이터 최적화 옵션들
    optimal_configs = {
        "hw.gpu.enabled": "yes",
        "hw.gpu.mode": "auto",
        "fastboot.forceCold": "yes",       # 🌟 질문자님이 요청하신 Cold Boot 고정!
        "hw.ramSize": "2048",              # 스플래툰 앱이 원활히 돌 수 있는 최소 2GB 램 할당
        "vm.heapSize": "256"
    }
    
    # 기존 가상기기 config.ini 파일이 있다면 읽어서 덮어쓰고, 없다면 새로 만듭니다.
    existing_ini = {}
    if os.path.exists(config_ini_path):
        with open(config_ini_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    existing_ini[k.strip()] = v.strip()
                    
    existing_ini.update(optimal_configs)
    
    with open(config_ini_path, "w", encoding="utf-8") as f:
        for k, v in existing_ini.items():
            f.write(f"{k}={v}\n")
            
    print(" -> ✅ 모든 최적화 설정 완료! 에뮬레이터를 작동할 준비가 되었습니다.\n")
    return True

if __name__ == '__main__':
    initialize_environment()
