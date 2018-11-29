from app import app
import sqlite3, os
from flask import g, request
from flask import render_template

DATABASE = os.path.join(os.path.dirname(__file__), '../school.db')


def connect_db():
    return sqlite3.connect(DATABASE)


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [
        dict((cur.description[idx][0], value) for idx, value in enumerate(row))
        for row in cur.fetchall()
    ]
    g.db.commit()
    return (rv[0] if rv else None) if one else rv


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/students')
def get_students():
    students = query_db('select * from students')
    return render_template('students.html', students=students)


@app.route('/classes')
def get_classes():
    classes = query_db('select * from classes')
    return render_template('classes.html', classes=classes)


@app.route('/grades')
def get_final_grades():
    grades = query_db(
        '''select students.sno as no, students.sname as name, count(*) as sum, round(avg(SC.grade), 2) as avg, sum(classes.credit) as total
     from students join SC on students.sno = SC.sno join classes on sc.cno = classes.cno
     where SC.grade is not null
     group by students.sno''')
    return render_template('grades.html', grades=grades)


@app.route('/student-grade', methods=['POST'])
def get_single_student_grade():
    sno = request.form.get('sno')
    names = query_db("select sname from students where sno = '{}'".format(sno))
    if len(names) == 0:
        return render_template('info.html', message="没有找到该学号的学生，请确认学号是否正确")
    name = names[0]['sname']
    avg = query_db(
        "select round(avg(grade),2) as avg from sc where sno = '{}'".format(
            sno))[0]['avg']
    credit = query_db(
        "select sum(classes.credit) as total from sc join classes on sc.cno = classes.cno where SC.grade is not null and sc.sno = '{}'"
        .format(sno))[0]['total']
    query = '''select sc.cno as no, classes.cname name, classes.credit as credit, round(sc.grade, 2) as grade
    from sc join classes on sc.cno = classes.cno
    where sc.sno = '''
    query += "'{}'".format(sno)
    grades = query_db(query)
    return render_template(
        'student-grade.html',
        no=sno,
        name=name,
        grades=grades,
        credit=credit,
        avg=avg)


@app.route('/add-grade')
def submit_grade():
    return render_template('submit-grade.html')


@app.route('/add-grade-result', methods=['POST'])
def add_grade():
    sno = request.form.get('sno')
    search_sno_result = query_db(
        "select * from students where sno = '{}'".format(sno))
    if len(search_sno_result) == 0:
        return render_template('info.html', message="没有找到该学号的学生，请确认学号是否正确")
    cno = request.form.get('cno')
    search_cno_result = query_db(
        "select * from classes where cno = '{}'".format(cno))
    if len(search_cno_result) == 0:
        return render_template('info.html', message="没有找到该课程号的课程，请确认课程号是否正确")
    grade = request.form.get('grade')
    old_grade = query_db(
        "select * from sc where sno = '{}' and cno = '{}'".format(sno, cno))
    if len(old_grade) == 0:
        query_db("insert into sc values ('{}', '{}', {})".format(
            sno, cno, grade))
        return render_template('info.html', message="成绩已经成功录入")
    else:
        return render_template('info.html', message="该学生已经有该门课的成绩，无法重新录入")


@app.route('/delete-grade')
def submit_delete_grade():
    return render_template('delete-grade.html')


@app.route('/delete-grade-result', methods=['POST'])
def delete_grade():
    sno = request.form.get('sno')
    search_sno_result = query_db(
        "select * from students where sno = '{}'".format(sno))
    if len(search_sno_result) == 0:
        return render_template('info.html', message="没有找到该学号的学生，请确认学号是否正确")
    cno = request.form.get('cno')
    search_cno_result = query_db(
        "select * from classes where cno = '{}'".format(cno))
    if len(search_cno_result) == 0:
        return render_template('info.html', message="没有找到该课程号的课程，请确认课程号是否正确")
    result = query_db("delete from sc where sno = '{}' and cno = '{}'".format(
        sno, cno))
    print(result)
    return render_template('info.html', message="成绩已删除")
