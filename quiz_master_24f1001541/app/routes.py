from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, Subject, Chapter, Quiz, Question, Score
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  

main = Blueprint('main', __name__)

# Home Page
@main.route('/')
def home():
    return render_template('home.html')

# Admin Login
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hardcoded admin credentials 
        if username == "admin" and password == "admin123":
            flash('Admin login successful!', 'success')
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin_login.html')

# Admin Dashboard
@main.route('/admin/dashboard')
def admin_dashboard():
    # Check if admin is logged in
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('main.admin_login'))

    # Get the search query from the request
    search_query = request.args.get('search_query', '').strip()

    # Initialize empty lists for subjects, chapters, and quizzes
    subjects = []
    chapters = []
    quizzes = []

    # Filter subjects, chapters, and quizzes based on the search query
    if search_query:
        # Use case-insensitive search for better usability
        subjects = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()
        chapters = Chapter.query.filter(Chapter.name.ilike(f'%{search_query}%')).all()
        quizzes = Quiz.query.filter(Quiz.remarks.ilike(f'%{search_query}%')).all()
    else:
        # If no search query, fetch all records
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()

    # Debugging: Print the number of results
    print(f"Subjects found: {len(subjects)}")
    print(f"Chapters found: {len(chapters)}")
    print(f"Quizzes found: {len(quizzes)}")

    # Render the admin dashboard template with the data
    return render_template(
        'admin_dashboard.html',
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
        search_query=search_query
    )





# List Subjects
@main.route('/admin/subjects')
def admin_subjects():
    subjects = Subject.query.all()
    return render_template('admin_subjects.html', subjects=subjects)

# Create Subject
@main.route('/admin/subjects/create', methods=['GET', 'POST'])
def admin_create_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        new_subject = Subject(
            name=name,
            description=description
        )
        db.session.add(new_subject)
        db.session.commit()

        flash('Subject created successfully!', 'success')
        return redirect(url_for('main.admin_subjects'))

    return render_template('admin_create_subject.html')

# Edit Subject
@main.route('/admin/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
def admin_edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')
        db.session.commit()

        flash('Subject updated successfully!', 'success')
        return redirect(url_for('main.admin_subjects'))

    return render_template('admin_edit_subject.html', subject=subject)

# Delete Subject
@main.route('/admin/subjects/<int:subject_id>/delete')
def admin_delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()

    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('main.admin_subjects'))



# List Chapters for a Subject
@main.route('/admin/subjects/<int:subject_id>/chapters')
def admin_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('admin_chapters.html', subject=subject, chapters=chapters)

# Create Chapter
@main.route('/admin/subjects/<int:subject_id>/chapters/create', methods=['GET', 'POST'])
def admin_create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        new_chapter = Chapter(
            name=name,
            description=description,
            subject_id=subject_id
        )
        db.session.add(new_chapter)
        db.session.commit()

        flash('Chapter created successfully!', 'success')
        return redirect(url_for('main.admin_chapters', subject_id=subject_id))

    return render_template('admin_create_chapter.html', subject=subject)

# Edit Chapter
@main.route('/admin/chapters/<int:chapter_id>/edit', methods=['GET', 'POST'])
def admin_edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()

        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('main.admin_chapters', subject_id=chapter.subject_id))

    return render_template('admin_edit_chapter.html', chapter=chapter)

# Delete Chapter
@main.route('/admin/chapters/<int:chapter_id>/delete')
def admin_delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()

    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('main.admin_chapters', subject_id=chapter.subject_id))



# List Quizzes for a Chapter
@main.route('/admin/chapters/<int:chapter_id>/quizzes')
def admin_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('admin_quizzes.html', chapter=chapter, quizzes=quizzes)

# Create Quiz
@main.route('/admin/chapters/<int:chapter_id>/quizzes/create', methods=['GET', 'POST'])
def admin_create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        date_of_quiz_str = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        # Convert the date string to a Python date object
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('main.admin_create_quiz', chapter_id=chapter_id))

        new_quiz = Quiz(
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks,
            chapter_id=chapter_id
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz created successfully!', 'success')
        return redirect(url_for('main.admin_quizzes', chapter_id=chapter_id))

    return render_template('admin_create_quiz.html', chapter=chapter)

# Edit Quiz
@main.route('/admin/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
def admin_edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        date_of_quiz_str = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        # Convert the date string to a Python date object
        try:
            quiz.date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('main.admin_edit_quiz', quiz_id=quiz_id))

        quiz.time_duration = time_duration
        quiz.remarks = remarks
        db.session.commit()

        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('main.admin_quizzes', chapter_id=quiz.chapter_id))

    return render_template('admin_edit_quiz.html', quiz=quiz)

# Delete Quiz
@main.route('/admin/quizzes/<int:quiz_id>/delete')
def admin_delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()

    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('main.admin_quizzes', chapter_id=quiz.chapter_id))



# List Questions for a Quiz
@main.route('/admin/quizzes/<int:quiz_id>/questions')
def admin_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin_questions.html', quiz=quiz, questions=questions)

# Create Question
@main.route('/admin/quizzes/<int:quiz_id>/questions/create', methods=['GET', 'POST'])
def admin_create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')

        new_question = Question(
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            quiz_id=quiz_id
        )
        db.session.add(new_question)
        db.session.commit()

        flash('Question created successfully!', 'success')
        return redirect(url_for('main.admin_questions', quiz_id=quiz_id))

    return render_template('admin_create_question.html', quiz=quiz)

# Edit Question
@main.route('/admin/questions/<int:question_id>/edit', methods=['GET', 'POST'])
def admin_edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = request.form.get('correct_option')
        db.session.commit()

        flash('Question updated successfully!', 'success')
        return redirect(url_for('main.admin_questions', quiz_id=question.quiz_id))

    return render_template('admin_edit_question.html', question=question)

# Delete Question
@main.route('/admin/questions/<int:question_id>/delete')
def admin_delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()

    flash('Question deleted successfully!', 'success')
    return redirect(url_for('main.admin_questions', quiz_id=question.quiz_id))



# User Registration
@main.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        # Handle user registration logic
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')  # Get the date as a string

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('main.user_register'))

        # Convert the date string to a Python date object
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('main.user_register'))

        # Hash the password before saving (using the default method: pbkdf2:sha256)
        hashed_password = generate_password_hash(password)

        # Create a new user
        new_user = User(
            username=username,
            password=hashed_password,  # Store the hashed password
            full_name=full_name,
            qualification=qualification,
            dob=dob  # Use the date object
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.user_login'))

    return render_template('user_register.html')

# User Login
@main.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('user_login.html')
#user dashboard
@main.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id'):
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('main.user_login'))

    # Fetch the logged-in user's details
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('main.user_login'))

    # Fetch all quizzes from the database
    quizzes = Quiz.query.all()

    # Pass the user and quizzes to the template
    return render_template('user_dashboard.html', user=user, quizzes=quizzes)
# Quiz Page
@main.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz(quiz_id):
    if not session.get('user_id'):
        flash('Please log in to take the quiz.', 'error')
        return redirect(url_for('main.user_login'))

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        score = 0
        for question in quiz.questions:
            selected_option = request.form.get(f'question_{question.id}')
            print(f"Question ID: {question.id}, Selected Option: {selected_option}, Correct Option: {question.correct_option}")  # Debugging
            if int(selected_option) == int(question.correct_option):
                score += 1

        print(f"Total Score: {score}")  # Debugging

        # Save the score to the database
        new_score = Score(
            quiz_id=quiz_id,
            user_id=session['user_id'],
            time_stamp_of_attempt=datetime.utcnow(),
            total_scored=score
        )
        db.session.add(new_score)
        db.session.commit()

        flash(f'Quiz submitted! Your score is {score}/{len(quiz.questions)}', 'success')
        return redirect(url_for('main.scores'))

    return render_template('quiz.html', quiz=quiz)

# Scores Page
@main.route('/scores')
def scores():
    if not session.get('user_id'):
        flash('Please log in to view your scores.', 'error')
        return redirect(url_for('main.user_login'))

    user_scores = Score.query.filter_by(user_id=session['user_id']).all()
    return render_template('scores.html', scores=user_scores)

# User Logout
@main.route('/user/logout')
def user_logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))


from flask import Flask, render_template, request, redirect, url_for, flash, session
from app.models import User, Subject, Chapter, Quiz, Question, Score
from app import db
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg' (non-GUI)
import matplotlib.pyplot as plt
import io
import base64

# Admin Summary Page
@main.route('/admin/summary')
def admin_summary():
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin summary.', 'error')
        return redirect(url_for('main.admin_login'))

    # Fetch all scores from the database
    scores = Score.query.all()

    # Prepare data for the bar graph
    quiz_ids = [score.quiz_id for score in scores]
    total_scores = [score.total_scored for score in scores]

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    plt.bar(quiz_ids, total_scores, color='blue')
    plt.xlabel("Quiz ID")
    plt.ylabel("Total Score")
    plt.title("Quiz ID vs Total Score")
    plt.xticks(quiz_ids)

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Render the summary page with the graph
    return render_template("admin_summary.html", plot_url=plot_url)

# User Summary Page
@main.route('/user/summary')
def user_summary():
    if not session.get('user_id'):
        flash('Please log in to access your summary.', 'error')
        return redirect(url_for('main.user_login'))

    user_id = session.get('user_id')

    # Fetch scores for the specific user
    scores = Score.query.filter_by(user_id=user_id).all()

    # Prepare data for the bar graph
    quiz_ids = [score.quiz_id for score in scores]
    user_scores = [score.total_scored for score in scores]

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    plt.bar(quiz_ids, user_scores, color='green')
    plt.xlabel("Quiz ID")
    plt.ylabel("Your Score")
    plt.title("Quiz ID vs Your Score")
    plt.xticks(quiz_ids)

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Render the user summary page with the graph
    return render_template("user_summary.html", plot_url=plot_url)

