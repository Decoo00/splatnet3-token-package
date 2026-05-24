import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import re

# 우리가 만든 환경 초기화 스크립트 불러오기
try:
    from initialize_env import initialize_environment
except ImportError:
    def initialize_environment(): return True

class TokenExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("스플래툰 3 토큰 추출기 (무설치 완결 배포판)")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # 현재 실행 경로 계산 (EXE 패키징 완벽 대응)
        if getattr(sys, 'frozen', False):
            self.current_dir = os.path.dirname(sys.executable)
        else:
            self.current_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.sdk_path = os.path.join(self.current_dir, "android_sdk")
        
        # UI 요소 생성
        self.create_widgets()
        
    def create_widgets(self):
        # 상단 안내 타이틀
        title_label = tk.Label(self.root, text="SplatNet 3 Token Extractor", font=("Arial", 18, "bold"), fg="#1a73e8")
        title_label.pack(pady=15)
        
        desc_label = tk.Label(self.root, text="순정 램 덤프 엔진을 내장하여 안전하고 확실하게 토큰을 추출합니다.", font=("Arial", 10))
        desc_label.pack(pady=2)
        
        # 버튼 영역 프레임
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        # 1단계 에뮬레이터 켜기 버튼
        self.btn_launch = tk.Button(btn_frame, text="🚀 1단계: 에뮬레이터 켜기", font=("Arial", 11, "bold"), 
                                    bg="#34a853", fg="white", width=22, height=2, command=self.start_launch_thread)
        self.btn_launch.grid(row=0, column=0, padx=10)
        
        # 2단계 토큰 세트 추출 버튼
        self.btn_extract = tk.Button(btn_frame, text="🔍 2단계: 토큰 세트 추출", font=("Arial", 11, "bold"), 
                                     bg="#4285f4", fg="white", width=22, height=2, command=self.start_extract_thread)
        self.btn_extract.grid(row=0, column=1, padx=10)
        
        # 로그 및 결과 출력 스크롤 창
        log_label = tk.Label(self.root, text="실행 로그 및 최종 결과:", font=("Arial", 10, "bold"))
        log_label.pack(anchor="w", padx=25, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(self.root, width=75, height=18, font=("Consolas", 9))
        self.log_area.pack(padx=20, pady=5)
        self.append_log("▶ 프로그램이 준비되었습니다. 공유받은 압축을 풀고 첫 실행이라면 '1단계'를 눌러주세요.\n")
        
        # 하단 경고/안내 메시지
        footer = tk.Label(self.root, text="※ 에뮬레이터 기기 안에서 닌텐도 온라인 앱 로그인이 완전히 끝난 후 2단계를 누르세요.", font=("Arial", 9), fg="gray")
        footer.pack(pady=10)

    def append_log(self, message):
        self.log_area.insert(tk.END, message)
        self.log_area.see(tk.END)

    def start_launch_thread(self):
        self.btn_launch.config(state=tk.DISABLED)
        threading.Thread(target=self.launch_emulator, daemon=True).start()

    def launch_emulator(self):
        self.append_log("🤖 사용자의 무설치 SDK 환경 검증 및 가상 기기(NSA) 초기화 중...\n")
        
        if not initialize_environment():
            self.append_log("❌ 초기화 실패: android_sdk 내부에 필수 이미지나 도구가 누락되었습니다.\n")
            self.root.after(0, lambda: self.btn_launch.config(state=tk.NORMAL))
            return
            
        self.append_log("✅ 기기 뼈대 구축 완료! 에뮬레이터 부팅 프로세스를 구동합니다...\n")
        
        emulator_exe = os.path.join(self.sdk_path, "emulator", "emulator")
        if sys.platform == "win32":
            emulator_exe += ".exe"
            
        avd_home_dir = os.path.join(self.current_dir, ".android")
        os.environ["ANDROID_AVD_HOME"] = avd_home_dir

        # Cold Boot 고정 및 최적화 렌더링 부팅 옵션 적용
        cmd = [
            emulator_exe,
            "-avd", "NSA",
            "-no-snapshot-load",
            "-no-snapshot-save",
            "-gpu", "auto"
        ]
        
        try:
            self.append_log("🚀 스마트폰 가상 화면(NSA)이 실행됩니다. 구글/닌텐도 로그인을 진행해주세요!\n")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            self.append_log(f"❌ 에뮬레이터 구동 에러: {e}\n")
            
        self.root.after(0, lambda: self.btn_launch.config(state=tk.NORMAL))

    def start_extract_thread(self):
        self.btn_extract.config(state=tk.DISABLED)
        threading.Thread(target=self.extract_tokens, daemon=True).start()

    def extract_tokens(self):
        self.append_log("\n--------------------------------------------------\n")
        self.append_log("🔍 순정 파싱 엔진 설정을 로드하는 중...\n")
        
        try:
            # 1. 긁어온 순정 소스코드 모듈들을 그대로 불러옵니다.
            sys.path.append(self.current_dir)
            from data.app_config import AppConfig
            from utils.snapshot_utils import create_snapshot, search_for_tokens
            
            # .android 격리 환경 연동을 위한 환경 변수 일치 작업
            avd_home_dir = os.path.join(self.current_dir, ".android")
            os.environ["ANDROID_AVD_HOME"] = avd_home_dir
            
            # 2. config.txt를 기반으로 순정 AppConfig 인스턴스 생성
            app_config = AppConfig()
            
            self.append_log("📸 [1/2] 에뮬레이터 메모리 동결 및 ram.bin 복사 생성 중...\n")
            # 3. 순정 함수 실행하여 물리 램 덤프 파일 빌드
            create_snapshot(app_config)
            
            self.append_log("🚀 [2/2] 원본 덤프 스캔 엔진 가동! 토큰 추출 시작...\n")
            # 4. 순정 서치 함수를 돌려 결과 가로채기
            g, bullet, session, ua, wv, country, lang, app_lang = search_for_tokens(app_config)
            
            self.append_log("\n--------------------------------------------------\n")
            if g and bullet:
                self.append_log("🎉 [추출 대성공] 스플래툰 3 인증 토큰을 성공적으로 낚아챘습니다!\n\n")
                
                # 가독성을 위해 정제 기호 치환 원복 처리 및 이쁘게 출력
                final_result = {
                    "g_token": g,
                    "bullet_token": bullet,
                    "session_token": session if session else "SKIPPED",
                    "user_agent": ua,
                    "web_view_version": wv,
                    "na_country": country,
                    "na_language": lang,
                    "app_language": app_lang
                }
                
                self.log_area.insert(tk.END, json.dumps(final_result, indent=4, ensure_ascii=False))
                self.log_area.see(tk.END)
                messagebox.showinfo("성공", "스플래툰 3 토큰 세트 추출에 성공했습니다! 아래 결과창에서 복사하세요.")
            else:
                self.append_log("❌ 실패: ram.bin 데이터 분석은 마쳤으나 토큰 찌꺼기를 검출하지 못했습니다.\n")
                self.append_log("⚠️ 원인: 에뮬레이터 내부 닌텐도 스위치 어카운트 앱에서 본인 계정 로그인이 완료되지 않았거나 화면이 꺼져있을 수 있습니다.\n")
                messagebox.showwarning("실패", "토큰 가로채기에 실패했습니다. 안내 문구를 확인해주세요.")
                
        except Exception as e:
            self.append_log(f"❌ 순정 연동 엔진 구동 실패: {e}\n")
            messagebox.showerror("오류", f"엔진 충돌 에러: {e}")
            
        self.root.after(0, lambda: self.btn_extract.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenExtractorGUI(root)
    root.mainloop()
