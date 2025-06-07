from backend.diary import Diary
from backend.admin import Admin 

class MainStrengthDiary:
    def __init__(self):
        self.current_user = None  
        self.is_authenticated = False 
        self.current_view = "login"  

    def start_app(self):
        """사이트 초기화 시 호출. 로그인 화면부터 시작."""
        self.is_authenticated = False
        self.current_view = "login"
        print("서비스를 시작합니다. 로그인 화면으로 이동합니다.")

    def navigate_to(self, view_name: str):
        """사용자 요청에 따라 다른 화면으로 이동"""
        self.current_view = view_name
        print(f"📄 현재 화면: {self.current_view}")

    def handle_request(self, action: str):
        """사용자 동작에 따른 기능 분기 처리"""
        if action == "write_diary":
            if not self._check_session():
                return

            title = "오늘의 일기"
            content = "오늘은 정말 기분이 좋았다. 친구들과 맛있는 점심도 먹었다."
            weather = "맑음"

            diary = Diary(title, content, weather, self.current_user.id)
            diary.save()
            self.navigate_to("diary_detail")  

        elif action == "view_community":
            self.navigate_to("community")

        elif action == "admin_dashboard":
            if self.is_authenticated and isinstance(self.current_user, Admin):
                self.navigate_to("admin_dashboard")
            else:
                print("관리자만 접근 가능합니다.")

        else:
            print("알 수 없는 요청입니다.")

    def logout(self):
        """현재 사용자 로그아웃"""
        print(f"👤 {self.current_user}님이 로그아웃했습니다.")
        self.current_user = None
        self.is_authenticated = False
        self.current_view = "login"

    def _check_session(self):
        """내부용: 세션 유효성 확인"""
        if not self.is_authenticated:
            print("로그인 상태가 아닙니다.")
            return False
        return True

    def _reload_user_data(self):
        """(상속용) 사용자 데이터를 갱신"""
        print("사용자 정보를 갱신합니다.")