from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class Diary:
    def __init__(self, title, content, weather, user_id):
        self.title = title
        self.content = content
        self.weather = weather
        self.user_id = user_id

    def save(self):
        print(f"일기 저장 완료: {self.title}, 작성자: {self.user_id}")

@app.route('/write_diary', methods=['GET', 'POST'])
def write_diary():
    date = request.args.get('date') 

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        weather = request.form['weather']
        user_id = 1 

        diary = Diary(title=title, content=content, weather=weather, user_id=user_id)
        diary.save()

        return redirect(url_for('dashboard'))  

    return render_template('write_diary.html', date=date)
