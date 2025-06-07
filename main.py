from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User, Diary, Report, Advantage, CommunityPost, Comment
from backend.advantage_extractor import extract_advantages
from flask_migrate import Migrate
from datetime import datetime
from flask import flash
import logging
from backend.model_manager import ModelManager
import os
from flask import send_from_directory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///strength_diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'

db.init_app(app)
migrate = Migrate(app, db)
MODEL_FOLDER = os.path.join(os.getcwd(), 'models')

def is_admin():
    user_id = session.get('user_id')
    if not user_id:
        return False
    user = User.query.get(user_id)
    return user and getattr(user, 'is_admin', False)

@app.route('/initdb')
def init_db():
    db.create_all()
    return "데이터베이스 초기화 완료!"

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nickname = request.form['nickname']
        hashed_pw = generate_password_hash(password)

        if User.query.filter_by(username=username).first():
            return "이미 존재하는 사용자입니다."

        is_admin = True if username == 'admin' else False

        new_user = User(username=username, password=hashed_pw, nickname=nickname, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            return "로그인 실패: 아이디 또는 비밀번호를 확인하세요."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    if user.is_admin:
        return redirect('/admin_dashboard')

    latest_diary = Diary.query.filter_by(user_id=user.id).order_by(Diary.created_at.desc()).first()
    current_date = datetime.now().strftime('%A, %d %B').upper()

    return render_template('dashboard.html', username=user.username, current_date=current_date, latest_diary=latest_diary)

@app.route('/write_diary', methods=['GET', 'POST'])
def write_diary():
    if 'user_id' not in session:
        return redirect('/login')

    selected_date = request.args.get('date')
    date_display = None
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            date_display = date_obj.strftime('%Y년 %m월 %d일')
        except ValueError:
            date_display = "날짜 형식 오류"

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        weather = request.form['weather']
        user_id = session['user_id']

        diary = Diary(title=title, content=content, weather=weather, user_id=user_id)
        db.session.add(diary)
        db.session.commit()

        try:
            keywords = extract_advantages(content)
        except Exception as e:
            logging.error(f"[장점 분석 실패] {e}")
            flash("장점 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
            keywords = ["임시 장점"]

        if not keywords:
            keywords = ["기타"]

        for keyword in keywords:
            adv = Advantage(keyword=keyword, diary_id=diary.id)
            db.session.add(adv)
        db.session.commit()

        return redirect(f"/diary/{diary.id}")

    return render_template('write_diary.html', selected_date=date_display)

@app.route('/diary/<int:diary_id>')
def diary_detail(diary_id):
    if 'user_id' not in session:
        return redirect('/login')

    diary = Diary.query.get_or_404(diary_id)
    if diary.user_id != session['user_id']:
        return "권한이 없습니다."

    advantages = Advantage.query.filter_by(diary_id=diary.id).all()
    return render_template('diary_detail.html', diary=diary, advantages=advantages)

@app.route('/edit_diary/<int:diary_id>', methods=['GET', 'POST'])
def edit_diary(diary_id):
    if 'user_id' not in session:
        return redirect('/login')

    diary = Diary.query.get_or_404(diary_id)
    if diary.user_id != session['user_id']:
        return "권한이 없습니다."

    if request.method == 'POST':
        diary.title = request.form['title']
        diary.content = request.form['content']
        diary.weather = request.form['weather']

        Advantage.query.filter_by(diary_id=diary.id).delete()
        keywords = extract_advantages(diary.content)
        for keyword in keywords:
            adv = Advantage(keyword=keyword, diary_id=diary.id)
            db.session.add(adv)

        db.session.commit()
        return redirect(f"/diary/{diary.id}")

    return render_template('edit_diary.html', diary=diary)

@app.route('/delete_diary/<int:diary_id>', methods=['POST'])
def delete_diary(diary_id):
    if 'user_id' not in session:
        return redirect('/login')

    diary = Diary.query.get_or_404(diary_id)
    if diary.user_id != session['user_id']:
        return "권한이 없습니다."

    Advantage.query.filter_by(diary_id=diary.id).delete()
    db.session.delete(diary)
    db.session.commit()

    return redirect('/dashboard')

@app.route('/community/write', methods=['GET', 'POST'])
def community_write():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        post = CommunityPost(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()

        return redirect('/community')

    return render_template('community_write.html')

@app.route('/community')
def community():
    if 'user_id' not in session:
        return redirect('/login')

    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return render_template('community.html', posts=posts)

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect('/login')

    content = request.form.get('comment')
    if not content:
        return "댓글 내용이 없습니다."

    comment = Comment(content=content, post_id=post_id, user_id=session['user_id'])
    db.session.add(comment)
    db.session.commit()
    return redirect('/community')

@app.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):
    post = CommunityPost.query.get(post_id)
    if post:
        if post.like_count is None:
            post.like_count = 0
        post.like_count += 1
        db.session.commit()
    return redirect(url_for("community"))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])
    if not user or not getattr(user, 'is_admin', False):
        return "접근 권한이 없습니다."

    return render_template('admin_dashboard.html', user=user)

@app.route('/admin/users')
def admin_users():
    if not is_admin(): return redirect('/login')

    users = User.query.all()
    reports = Report.query.all()

    for r in reports:
        if r.report_type == 'post':
            post = CommunityPost.query.get(r.target_id)
            r.author_id = post.user_id if post else None
        elif r.report_type == 'comment':
            comment = Comment.query.get(r.target_id)
            r.author_id = comment.user_id if comment else None

    post_dict = {p.id: p for p in CommunityPost.query.all()}
    comment_dict = {c.id: c for c in Comment.query.all()}

    return render_template('admin_users.html', users=users, reports=reports,
                           post_dict=post_dict, comment_dict=comment_dict)

@app.route('/admin/users/toggle/<int:user_id>', methods=['POST'])
def toggle_user_status(user_id):
    if 'user_id' not in session:
        return redirect('/login')

    admin = User.query.get(session['user_id'])
    if not admin or not admin.is_admin:
        return "접근 권한이 없습니다."

    user = User.query.get_or_404(user_id)
    user.is_suspended = not user.is_suspended
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route("/report_post/<int:post_id>", methods=["POST"])
def handle_report_post(post_id):
    report = Report(report_type='post', target_id=post_id)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for("community"))

@app.route("/report_comment/<int:comment_id>", methods=["POST"])
def handle_report_comment(comment_id):
    report = Report(report_type='comment', target_id=comment_id)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for("community"))

@app.route('/admin/report/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    if not is_admin():
        return redirect('/login')

    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/models')
def manage_models():
    if not is_admin():
        return redirect('/login')

    manager = ModelManager() 
    models = manager.list_models()
    return render_template('admin_models.html', models=models)


@app.route('/admin/models/upload', methods=['POST'])
def upload_model():
    if not is_admin():
        return redirect('/login')

    file = request.files.get('model_file')
    if not file:
        flash("파일이 선택되지 않았습니다.")
        return redirect('/admin/models')

    manager = ModelManager()  
    success, message = manager.upload_model(file)
    flash(message)
    return redirect('/admin/models')

@app.route('/admin/models/delete/<filename>', methods=['POST'])
def delete_model(filename):
    if not is_admin():
        return redirect('/login')

    manager = ModelManager()  
    success, message = manager.delete_model(filename)
    flash(message)
    return redirect('/admin/models')

@app.route('/admin/community')
def admin_community():
    if not is_admin():
        return redirect('/login')

    reports = Report.query.all()
    post_dict = {p.id: p for p in CommunityPost.query.all()}
    comment_dict = {c.id: c for c in Comment.query.all()}
    user_dict = {u.id: u for u in User.query.all()}

    for r in reports:
        if r.report_type == 'post' and r.target_id in post_dict:
            r.author_id = post_dict[r.target_id].user_id
        elif r.report_type == 'comment' and r.target_id in comment_dict:
            r.author_id = comment_dict[r.target_id].user_id
        else:
            r.author_id = None

    return render_template(
        'admin_community.html',
        reports=reports,
        post_dict=post_dict,
        comment_dict=comment_dict,
        user_dict=user_dict
    )

@app.route('/admin/community/delete/<string:report_type>/<int:target_id>', methods=['POST'])
def delete_content(report_type, target_id):
    try:
        if report_type == 'post':
            target = CommunityPost.query.get_or_404(target_id)
        elif report_type == 'comment':
            target = Comment.query.get_or_404(target_id)
        else:
            flash("잘못된 요청입니다.")
            return redirect(url_for('admin_community'))

        db.session.delete(target)
        db.session.commit()
        flash("삭제되었습니다.")
    except Exception as e:
        flash("삭제에 실패했습니다. 다시 시도해주세요.")
    return redirect(url_for('admin_community'))

if __name__ == '__main__':
    app.run(debug=True)
    
    
