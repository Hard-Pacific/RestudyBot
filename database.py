import sqlite3
from datetime import datetime

def create_data():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    # id, fullname, completed_lessons, purchased_lessons, teacher, phone
    cur.execute(f"""CREATE TABLE IF NOT EXISTS students(
                fullname TEXT UNIQUE,
                tg_id TEXT,
                teacher TEXT,
                phone TEXT,
                completed_lessons INTEGER,
                purchased_lessons INTEGER)
                """)
    cur.execute(f"""CREATE TABLE IF NOT EXISTS lessons(
                fullname TEXT,
                teacher TEXT,
                date_time TEXT,
                about TEXT

    )""")
    cur.execute(f"CREATE TABLE IF NOT EXISTS admins(tg_id TEXT)")
    cur.execute(f"""CREATE TABLE IF NOT EXISTS teachers(
                fullname TEXT UNIQUE,
                tg_id TEXT,
                completed_lessons INTEGER,
                payd_lessons INTEGER)
    """)
    con.commit()

def teachers_students(teachers_name):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM students WHERE teacher = '{teachers_name}'")
    students = cur.fetchall()
    con.commit()
    print(students)
    return students

def check_teachers_id(tg_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    query = f"SELECT * FROM teachers WHERE tg_id = '{tg_id}'"
    cur.execute(query)
    IsExists = len(cur.fetchall())
    cur.close()
    con.commit()
    return IsExists > 0

def check_teachers_name(teachers_name):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    query = f"SELECT * FROM teachers WHERE fullname = '{teachers_name}'"
    cur.execute(query)
    IsExists = len(cur.fetchall())
    cur.close()
    con.commit()
    return IsExists > 0

def all_teachers():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM teachers")
    teachers = cur.fetchall()
    return teachers

def assign_teacher(teacher_name, fullname):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"UPDATE students SET teacher = '{teacher_name}' WHERE fullname = '{fullname}'")
    con.commit()

# Админ получает уведомления о пробных занятиях
def add_admin(tg_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO admins(tg_id) VALUES('{tg_id}')")
    con.commit()

def add_teacher(fullname, tg_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO teachers (fullname, tg_id, completed_lessons, payd_lessons) VALUES('{fullname}', '{tg_id}', 0, 0)")
    con.commit()

def all_students():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM students WHERE teacher NOT NULL")
    students = cur.fetchall()
    print(students)
    
    return students    

# Не существует ли пользователь?
def check_fullname(fullname, tg_id = False):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    if tg_id:
        query = f"SELECT COUNT(*) FROM students WHERE tg_id = '{fullname}'"
    else:
        query = f"SELECT COUNT(*) FROM students WHERE fullname = '{fullname}'"
    cur.execute(query)
    IsANewUser = cur.fetchone()[0]
    cur.close()
    con.commit()
    return IsANewUser == 0

def new_student(fullname, tg_id, phone):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO students(fullname, tg_id, teacher, phone, completed_lessons, purchased_lessons) VALUES('{fullname}', '{tg_id}', NULL, '{phone}', 0, 0)")
    con.commit()

def students_without_teacher():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM students WHERE teacher is NULL")
    students = cur.fetchall()
    con.commit()
    return students

def complete_lesson(fullname, teacher, about):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    today = datetime.now()
    today = today.strftime("%H:%M %d %B %Y")
    cur.execute(f"SELECT * FROM students WHERE fullname == '{fullname}'")
    cur.execute(f"UPDATE students SET completed_lessons = completed_lessons + 1")
    cur.execute(f"INSERT INTO lessons(fullname, teacher, date_time, about) VALUES('{fullname}', '{teacher}', '{today}', '{about}')")
    con.commit()

def get_teacher(tg_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM teachers WHERE tg_id = {tg_id}")
    teachers_name = cur.fetchone()[0]
    con.commit()
    return teachers_name

def get_admins():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM admins")
    tg_id = cur.fetchall()
    con.commit()
    return tg_id

def get_student(fullname=None, tg_id=None):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM students WHERE tg_id == '{tg_id}' OR fullname = '{fullname}'")
    info = cur.fetchall()
    con.commit()
    return info

def payment(tg_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM students WHERE tg_id == '{tg_id}'")
    cur.execute(f"UPDATE students SET purchased_lessons = purchased_lessons + 8")
    con.commit()

def is_lesson_paid(fullname):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM students WHERE fullname == '{fullname}'")
    student = cur.fetchall()
    complete_lesson = int(student[0][3])
    purchased_lessons = int(student[0][4])
    if purchased_lessons <= complete_lesson:
        return False
    else:
        return True

# И З М Е Н Е Н И Е   И   У Д А Л Е Н И Е
def remove_students_teacher(fullname):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"UPDATE students SET teacher = NULL WHERE fullname = '{fullname}'")
    con.commit()

def remove_teacher(fullname):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"DELETE FROM teachers WHERE fullname = '{fullname}'")
    cur.execute(f"UPDATE students SET teacher = NULL WHERE teacher = '{fullname}'")
    con.commit()
    

def show_student(tg_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM students WHERE tg_id = '{tg_id}'")
    return cur.fetchall()

def show_database():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM lessons")
    data = f"lessons\n{cur.fetchall()}\n"
    cur.execute("SELECT * FROM students")
    data += f"students\n{cur.fetchall()}\n"
    cur.execute("SELECT * FROM teachers")
    data += f"teachers\n{cur.fetchall()}\n"
    cur.execute("SELECT * FROM admins")
    data += f"admins\n{cur.fetchall()}\n"
    return data

def report(level, teacher_id=None):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    if level == "administrator":
        cur.execute("SELECT * FROM lessons")
        lessons = cur.fetchall()
        lessons.sort(key=lambda x: x[1])
    if level == "teacher":
        teachers_name = get_teacher(teacher_id)
        cur.execute(f"SELECT * FROM lessons WHERE teacher == '{teachers_name}'")
        lessons = cur.fetchall()
    lessons = list(filter(lambda x:
                        datetime.strptime(x[2],"%H:%M %d %B %Y").month == current_month and
                        datetime.strptime(x[2],"%H:%M %d %B %Y").year == current_year, lessons))
    lessons = "\n".join([" | ".join(lesson) for lesson in lessons])
    return lessons

