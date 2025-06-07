class Diary:
    def __init__(self, title, content, weather, user_id):
        self.title = title
        self.content = content
        self.weather = weather
        self.user_id = user_id

    def save(self):
        print(f"일기 저장 완료: {self.title}, 작성자: {self.user_id}")