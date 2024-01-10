from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from aiogram.dispatcher.filters.state import State, StatesGroup
from random import choice
from loader import dp, bot
from meta import WEB_APP, MESSAGE, CARDS, PASSWORD
from TOKEN import PAYMENTS_TOKEN
import database

# Список услуг
PRICE = types.LabeledPrice(label = "8 занятий", amount = 6800*100)  # в копейках (руб)
PRICE2 = types.LabeledPrice(label = "Поддержка куратора", amount = 0)
PRICE3 = types.LabeledPrice(label = "Защита проекта", amount = 0)
class Registration(StatesGroup):
    phone_registration = State()
    fullname_registration = State()

class TeacherRegistration(StatesGroup):
    name = State()

class AssignTeacher(StatesGroup):
    student = State()
    end = State()

class FinishLesson(StatesGroup):
    complete = State()
    about = State()

@dp.message_handler(commands=["cancel"], state="*")
@dp.callback_query_handler(text="cancel", state="*")
async def cancel(message, state: FSMContext):
    print(0)
    await state.finish()
    await bot.send_message(message.from_user.id, "Галя! У нас отмена💃")

# Состояния регистрации пользователя в личный кабинет
# ---------------------------------------------------
# ОТМЕНА
@dp.message_handler(text = ["Отмена"], state=[Registration.phone_registration, Registration.fullname_registration])
async def cancel(message: types.Message, state: FSMContext):
    keyboard = [[types.KeyboardButton("Посетить наш сайт😊", web_app=WebAppInfo(url=WEB_APP))],
                [types.KeyboardButton("Войти\Зарегистрироваться")]]
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await state.finish()
    await bot.send_message(message.from_user.id, "Отменяем💀", reply_markup=markup)

# РЕГИСТРАЦИЯ ФИО
@dp.message_handler(text = ["Войти\Зарегистрироваться"], state=None)
async def PersonalAccount(message: types.Message, state: FSMContext):
    keyboard = [[types.KeyboardButton("Отмена")]]
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await bot.send_message(message.from_user.id, "Давай познакомимся, придумай свой Уникальный никнейм😎", reply_markup=markup)
    await Registration.fullname_registration.set()

# РЕГИСТРАЦИЯ НОМЕРА
@dp.message_handler(state=Registration.fullname_registration)
async def get_fullname(message: types.Message, state: FSMContext):
    if database.check_fullname(message.text):
        keyboard = [[types.KeyboardButton(text="Отправить свой номер", request_contact=True)],
                    [types.KeyboardButton(text="Отмена")]]
        markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await state.update_data(fullname=message.text)
        await bot.send_message(message.from_user.id, "Приятно познакомиться!😃\nНам нужны твои контакты😗👉👈", reply_markup=markup)
        await Registration.phone_registration.set()
    else:
        await bot.send_message(message.from_user.id, text="К сожалению никнейм занят😥\nПопробуй другой ввести другой ник")

# ЗАВЕРШЕНИЕ РЕГИСТРАЦИИ
@dp.message_handler(content_types=types.ContentType.CONTACT, state=Registration.phone_registration)
async def get_phone(message: types.Message, state: FSMContext):
    keyboard = [[types.KeyboardButton("Посетить наш сайт😊", web_app=WebAppInfo(url=WEB_APP))],
                [types.KeyboardButton("Личный кабинет")]]
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    inline_keyboard = [types.InlineKeyboardButton("О нас", callback_data="About"),
                        types.InlineKeyboardButton("О курсах", callback_data="Courses")]
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(inline_keyboard[0], inline_keyboard[1])
    await state.update_data(phone_number=message.contact)
    data = await state.get_data()
    await bot.send_message(message.from_user.id, f"Регистрация завершена успешно!\nБудем на связи {data.get('fullname')}😉", reply_markup=markup)
    await bot.send_photo(message.from_user.id, photo=MESSAGE["Continue"]["url"], caption=MESSAGE["Continue"]["caption"], reply_markup=inline_markup)
    database.new_student(data.get("fullname"), message.from_user.id, data.get("phone_number")["phone_number"])
    await state.finish()
# ---------------------------------------------------

# Личный кабинет
@dp.message_handler(text=["Личный кабинет"])
async def personal_account(message: types.Message):
    info = database.show_student(message.from_user.id)[0]
    await bot.send_message(message.from_user.id,
    f"""Ваш ник: {info[0]}
Ваш преподаватель: {info[2]}
Ваш телефон: {info[3]}
Пройденные занятия: {info[4]}
Оплаченные занятия: {info[5]}
    """)
# ----------------------------------------------------------------

# К О М А Н Д Ы
# /start - Добавление кнопки ПОСЕТИТЬ НАШ САЙТ
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = [[types.KeyboardButton("Посетить наш сайт😊", web_app=WebAppInfo(url=WEB_APP))]]
    IsANewUser = database.check_fullname(message.from_user.id, tg_id = True)
    if IsANewUser:
        keyboard.append([types.KeyboardButton("Войти\Зарегистрироваться")])
        print(0)
    else:
        keyboard.append([types.KeyboardButton("Личный кабинет")])
        print(1)
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    inline_keyboard = [types.InlineKeyboardButton("О нас", callback_data="About"),
                        types.InlineKeyboardButton("О курсах", callback_data="Courses")]
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(inline_keyboard[0], inline_keyboard[1])
    await bot.send_photo(message.from_user.id,
                         photo=MESSAGE["Hi"]["url"],
                         caption=MESSAGE["Hi"]["caption"],
                         reply_markup=inline_markup)
    await bot.send_message(message.from_user.id, "Кстати! Мы сделали сайт, обязательно загляни к нам😄", reply_markup=markup)

# /about - Карточки с описанием плюсов школы
@dp.callback_query_handler(text=["About"])
@dp.message_handler(commands=["about"])
async def about(message: types.Message):
    # Отправка карточки
    photos = [
        types.InputMediaPhoto(media=CARDS[0]),
        types.InputMediaPhoto(media=CARDS[1]),
        types.InputMediaPhoto(media=CARDS[2]),
    ]
    keyboard = types.InlineKeyboardButton(text="Наши курсы", callback_data="Courses")
    markup = types.InlineKeyboardMarkup()
    markup.add(keyboard)
    await bot.send_media_group(chat_id=message.from_user.id, media=photos)
    await bot.send_message(message.from_user.id, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", reply_markup=markup)

# /courses - Список курсов
@dp.callback_query_handler(lambda c: c.data == "Courses")
@dp.message_handler(commands=["courses"])
async def about(message: types.Message):
    keyboard = [[types.InlineKeyboardButton(text="Python", callback_data="Python")],
                [types.InlineKeyboardButton(text="Construct", callback_data="Construct")]]
    markup = types.InlineKeyboardMarkup()
    markup.add(keyboard[0][0], keyboard[1][0])
    await bot.send_photo(message.from_user.id, photo = MESSAGE["Choice"]["url"], reply_markup=markup)

# /courses Обработка нажатия кнопок
@dp.callback_query_handler(lambda c: c.data in ('Python', "Construct"))
async def courses(data: types.CallbackQuery):
    keyboard = [
        types.InlineKeyboardButton(text="Python", callback_data="Python"),
        types.InlineKeyboardButton(text="Construct", callback_data="Construct"),
        types.InlineKeyboardButton(text="Пройти занятие бесплатно!", callback_data="Trial"),
        types.InlineKeyboardButton(text="Взять курс", callback_data="Buy")
        
    ]
    markup = types.InlineKeyboardMarkup()
    markup.add(keyboard[0], keyboard[1])
    markup.add(keyboard[2])
    markup.add(keyboard[3])
    await bot.edit_message_media(
        media=types.InputMediaPhoto(
            media=MESSAGE[data.data]["url"],
            caption=MESSAGE[data.data]["caption"]
        ),
        chat_id=data.message.chat.id,
        message_id=data.message.message_id,
        reply_markup=markup
    )

# Запись на пробник
@dp.callback_query_handler(lambda call: call.data == "Trial")
async def courses(call: types.CallbackQuery):
    IsANewUser = database.check_fullname(call.from_user.id, tg_id = True)
    if not(IsANewUser):
        await bot.edit_message_media(
            media=types.InputMediaPhoto(
                media=MESSAGE["Trial"]["url"],
                caption=MESSAGE["Trial"]["caption"]
            ),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        print(database.get_admin())
        await bot.send_message(choice(database.get_admin())[0], f"Номер ученика: {database.get_student(call.from_user.id)[0][3]}\n")
    else:
        keyboard = [[types.KeyboardButton("Отмена")]]
        markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await bot.send_message(call.from_user.id, "Вы ещё не зарегистрированы😥\nПожалуйста, напишите как вас зовут?", reply_markup=markup)
        await Registration.fullname_registration.set()
# ----------------------------------------------------------------

# П Р Е П О Д А В А Т Е Л Ь
# Ввод пароля
@dp.message_handler(text=["rsat200123"], state=None)
async def teacher_password(message, state: FSMContext):
    inline_keyboard = types.InlineKeyboardButton(text="Отмена",callback_data="cancel")
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(inline_keyboard)
    await bot.send_message(message.from_user.id, "Добро пожаловать в систему Restudy. Пожалуйста введите ваше ФИО", reply_markup=inline_markup)
    await TeacherRegistration.name.set()

# Ввод имени
@dp.message_handler(content_types=["text"], state=[TeacherRegistration.name])
async def teacher_password(message, state: FSMContext):
    inline_keyboard = types.InlineKeyboardButton(text="Отмена",callback_data="cancel")
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(inline_keyboard)
    if database.check_teachers_id(message.from_user.id):
        await bot.send_message(message.from_user.id, "Вы уже зарегистрированы")
        await state.finish()
    elif database.check_teachers_name(message.text):
        await bot.send_message(message.from_user.id, "Имя занято, напишите другое", reply_markup=inline_markup)
    else:
        await bot.send_message(message.from_user.id, f"Готово! Рады знакомству {message.text}\nТеперь вы зарегистрированы как преподаватель")
        database.add_teacher(message.text, message.from_user.id)
        await state.finish()
# ----------------------------------------------------------------

# К У Р А Т О Р
# Права куратора(администратор)
@dp.message_handler(text=[PASSWORD])
async def admin(message: types.Message):
    database.add_admin(message.from_user.id)
    await bot.send_message(message.from_user.id, f"Вы успешно зарегистрированы как администратор😊\nТеперь вы будете получать уведомление о пробных занятиях")

# Назначение преподавателя ученику
@dp.message_handler(commands=["assign"], state=None)
async def choose_teacher(message, state: FSMContext):
    admins = [i[0] for i in database.get_admins()]
    print(admins)
    if str(message.from_user.id) in admins:
        inline_keyboard = [types.InlineKeyboardButton(text=teacher[0],callback_data=teacher[0]) for teacher in database.all_teachers()]
        inline_markup = types.InlineKeyboardMarkup()
        for i in inline_keyboard:
            inline_markup.add(i)
        inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
        await state.set_state(AssignTeacher.student)
        await bot.send_message(message.from_user.id, "Какому преподавателю назначить ученика?", reply_markup=inline_markup)

# Выбрать ученика
@dp.callback_query_handler(lambda call: True, state=AssignTeacher.student)
async def choose_student(call: types.CallbackQuery, state: FSMContext):
    if call.data in [student[0] for student in database.all_teachers()]:
        message_id = call.message.message_id
        await state.update_data(teachers_name=call.data)
        inline_keyboard = [types.InlineKeyboardButton(text=student[0],callback_data=student[0]) for student in database.students_without_teacher()]
        inline_markup = types.InlineKeyboardMarkup()
        for i in inline_keyboard:
            inline_markup.add(i)
        inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=message_id, text = f"Выбери ученика для {call.data}",reply_markup=inline_markup)
        await state.set_state(AssignTeacher.end)

@dp.callback_query_handler(lambda call: True, state=AssignTeacher.end)
async def end(call, state: FSMContext):
    teachers_name = await state.get_data()
    teachers_name = teachers_name["teachers_name"]
    database.assign_teacher(teachers_name, call.data)
    await bot.send_message(call.from_user.id, f"Готово! Ученик {call.data} назначается преподавателю {teachers_name}")
    await state.finish()

# С Д А Т Ь   О Т Ч Е Т
# Вывод студентов для выбора по отчету за занятие
@dp.message_handler(commands=["mystudents"])
async def mystudents(message, state: FSMContext):
    if database.check_teachers_id(message.from_user.id):
        teacher_id = message.from_user.id
        teachers_name = database.get_teacher(teacher_id)
        print(teachers_name)
        inline_keyboard = [types.InlineKeyboardButton(text=student[0],callback_data=student[0]) for student in database.teachers_students(teachers_name)]
        inline_markup = types.InlineKeyboardMarkup()
        await state.set_state(FinishLesson.complete)
        for i in inline_keyboard:
            inline_markup.add(i)
        inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
        await bot.send_message(teacher_id, "Твои ученики:", reply_markup=inline_markup)

@dp.callback_query_handler(lambda call: True, state=FinishLesson.complete)
async def fisnish_lesson(call: types.CallbackQuery, state: FSMContext):
    teachers_name = database.get_teacher(call.from_user.id)
    if call.data in [student[0] for student in database.teachers_students(teachers_name)]:
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
        await state.set_state(FinishLesson.about)
        await state.update_data(fullname=call.data)
        await bot.send_message(call.from_user.id, f"{call.data}\nЧто сегодня проходили?😄", reply_markup=inline_markup)

# В отчет вводится о чем было занятие
@dp.message_handler(content_types=["text"], state=FinishLesson.about)
async def about(message, state: FSMContext):
    data = await state.get_data()
    students_name = data.get('fullname')
    database.complete_lesson(students_name, database.get_teacher(message.from_user.id), message.text)
    can_i_teach_you = database.is_lesson_paid(students_name)
    await bot.send_message(message.from_user.id, f"Отправили отчет в космос👽")
    if not(can_i_teach_you):
        await bot.send_message(database.get_student(students_name)[0][1], f"У вас закончились оплаченные занятия😿\nВы можете оплатить новый месяц по команде /pay")
        await bot.send_message(message.from_user.id, f"АХТУНГ! У ученика {students_name} кончились занятия. Сообщите об этом куратору")
    await state.finish()

# П О Л У Ч И Т Ь   О Т Ч Е Т
# Отчет для администрации за месяц
@dp.message_handler(commands=["report"])
async def report(message):
    admins = [i[0] for i in database.get_admins()]
    if str(message.from_user.id) in admins:
        lessons = database.report("administrator")
        if lessons != "":
            await bot.send_message(message.from_user.id, f"{lessons}")
        else:
            await bot.send_message(message.from_user.id, "Ой, пока занятий не было🍃")

# Отчет для преподавателя за месяц
@dp.message_handler(commands=["myreport"])
async def report(message):
    if database.check_teachers_id(message.from_user.id):
        lessons = database.report("teacher", message.from_user.id)
        if lessons:
            await bot.send_message(message.from_user.id, f"{lessons}")
        else:
            await bot.send_message(message.from_user.id, "Ой, у тебя не было занятий в этом месяце⛱")
    else:
        print("Попытка")    

@dp.message_handler(commands=["allstudents"])
async def allstudents(message):
    admins = [i[0] for i in database.get_admins()]
    if str(message.from_user.id) in admins:
        all_students =" \n".join([str(student) for student in database.all_students()])
        if all_students != "":
            await bot.send_message(message.from_user.id, all_students)
        else:
            await bot.send_message(message.from_user.id, "Упсень, учеников нэт🐛")

@dp.message_handler(commands=["check"], state=None)
async def check(message):
    await bot.send_message(message.from_user.id, database.show_database())
# --------------------------------------------------------

# О П Л А Т А   К У Р С О В
# Оплата месяца занятий
@dp.callback_query_handler(text=["Buy"])
@dp.message_handler(commands=["pay"])
async def buy(message: types.Message):
    print(0)
    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.from_user.id, "Тестовый платеж!!!")
    await bot.send_invoice(message.from_user.id,
        title = "Оплата обучения",
        description="Целый месяц занятий!",
        provider_token = PAYMENTS_TOKEN,
        currency = "rub",
        photo_url = "https://i.imgur.com/22IdLjg.jpg",
        photo_width = 416,
        photo_height = 234,
        photo_size = 416,
        is_flexible = False,
        prices = [PRICE, PRICE2, PRICE3],
        start_parameter = "one-month-subscription",
        payload = "test-invoice-payload")

# Проверка платежа
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# check succesful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")
    database.payment(message.from_user.id)
    await bot.send_message(message.from_user.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")

class RemoveStudent(StatesGroup):
    student = State()
    end = State()
# Снятие ученика с преподавателя
@dp.message_handler(commands=["removestudent"])
async def remove_student_0(message: types.Message, state: FSMContext ):
    inline_keyboard = [types.InlineKeyboardButton(text=teacher[0],callback_data=teacher[0]) for teacher in database.all_teachers()]
    inline_markup = types.InlineKeyboardMarkup()
    for i in inline_keyboard:
        inline_markup.add(i)
    inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
    await bot.send_message(message.from_user.id, "Выбери преподавателя, чтобы снять у него ученика", reply_markup=inline_markup)
    await state.set_state(RemoveStudent.student)

@dp.callback_query_handler(state=RemoveStudent.student)
async def remove_student_1(call: types.CallbackQuery, state: FSMContext):
    inline_keyboard = [types.InlineKeyboardButton(text=student[0],callback_data=student[0]) for student in database.teachers_students(call.data)]
    inline_markup = types.InlineKeyboardMarkup()
    for i in inline_keyboard:
        inline_markup.add(i)
    inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
    await bot.send_message(call.from_user.id, "Выберите ученика, чтобы снять его с преподавателя", reply_markup=inline_markup)
    await state.set_state(RemoveStudent.end)

@dp.callback_query_handler(state=RemoveStudent.end)
async def remove_student_2(call: types.CallbackQuery, state: FSMContext):
    await bot.send_message(call.from_user.id, "Ученик снят с учителя")
    database.remove_students_teacher(call.data)
    await state.finish()

class RemoveTeacher(StatesGroup):
    choice = State()

@dp.message_handler(commands=["removeteacher"])
async def remove_teacher_0(message: types.Message, state: FSMContext):
    inline_keyboard = [types.InlineKeyboardButton(text=teacher[0],callback_data=teacher[0]) for teacher in database.all_teachers()]
    inline_markup = types.InlineKeyboardMarkup()
    for i in inline_keyboard:
        inline_markup.add(i)
    inline_markup.add(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
    await bot.send_message(message.from_user.id, "Выбери преподавателя для снятия с работы", reply_markup=inline_markup)
    await state.set_state(RemoveTeacher.choice)

@dp.callback_query_handler(state=RemoveTeacher.choice)
async def remove_teacher_1(call: types.CallbackQuery, state: FSMContext):
    await bot.send_message(call.from_user.id, f"{call.data} снят с работы")
    database.remove_teacher(call.data)
    await state.finish()