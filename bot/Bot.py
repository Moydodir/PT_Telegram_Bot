import logging
import os
import re
import paramiko
import psycopg2
import subprocess

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from dotenv import load_dotenv

load_dotenv("../.env")

TOKEN = os.getenv("TOKEN")
PATH = "./log/postgresql.log"

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def connection(command):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


def connect_to_db(table, query='select', new_values=None, field_name=None, ins_type=None):
    # Получаем параметры подключения из окружения
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_DATABASE')

    connection = None
    answer = None
    cursor = None
    try:
        # Подключаемся к базе данных
        connection = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )

        cursor = connection.cursor()

        if query == 'insert':
            insert_query = f"INSERT INTO {table} ({field_name}) VALUES (%s);"

            field_data = [(field,) for field in new_values]

            cursor.executemany(insert_query, field_data)
            connection.commit()

        cursor.execute(f"SELECT * FROM {table};")

        # Получаем результаты
        answer = cursor.fetchall()

    except Exception as e:
        answer = f"Ошибка при подключении к базе данных: {e}"

    finally:
        # Закрываем соединение
        if connection:
            cursor.close()
            connection.close()
            return f"{answer} \n Соединение с базой данных закрыто."


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findMailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email-адресов: ')

    return 'findMail'


def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'verify_password'


def get_releaseCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    # return 'get_release'
    get_release(update, context)


def get_unameCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_uname(update, context)


def get_uptimeCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_uptime(update, context)


def get_dfCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_df(update, context)


def get_freeCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_free(update, context)


def get_mpstatCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_mpstat(update, context)


def get_wCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_w(update, context)


def get_authsCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_auths(update, context)


def get_criticalCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_critical(update, context)


def get_psCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_ps(update, context)


def get_ssCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_ss(update, context)


def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите название пакета для анализа: ')

    # get_apt_list(update, context)
    return 'get_apt_list'


def get_servicesCommand(update: Update, context):
    update.message.reply_text('Сбор информации о системе')

    get_services(update, context)


def get_repl_logsCommand(update: Update, context):
    update.message.reply_text('Сбор логов postgresql')

    get_repl_logs(update, context)

def get_emailsCommand(update: Update, context):
    update.message.reply_text('подключение к postgresql')

    get_emails(update, context)

def get_phone_numbersCommand(update: Update, context):
    update.message.reply_text('подключение к postgresql')

    get_phone_numbers(update, context)
def button(update, context):
    global formatted_numbers
    query = update.callback_query
    query.answer()

    # В зависимости от callback_data выполняем разные действия
    if query.data == '1':
        if ins_type == 'phone':
            result = connect_to_db('phone_numbres', 'insert', formatted_numbers, ins_type)
        else:
            result = connect_to_db('mail_address', 'insert', mailList, ins_type)
        query.edit_message_text(text=result)
    elif query.data == '2':
        query.edit_message_text(text="Данные не вставлены")

def findPhoneNumbers(update: Update, context):
    global formatted_numbers, ins_type
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(\+7|8)[\s-]?\(?(\d{3})\)?[\s-]?(\d{3})[\s-]?(\d{2})[\s-]?(\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    formatted_numbers = [''.join(match) for match in phoneNumberList]

    for i in range(len(formatted_numbers)):
        update.message.reply_text(f'{i + 1}.{formatted_numbers[i]}')  # Отправляем сообщение пользователю

    keyboard = [
        [InlineKeyboardButton("да", callback_data='1')],
        [InlineKeyboardButton("нет", callback_data='2')],
    ]

    ins_type = 'phone'

    # Создаём объект клавиатуры
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    update.message.reply_text('Записать данные в базу?(да/нет):', reply_markup=reply_markup)

    return ConversationHandler.END


def findMail(update: Update, context):
    global mailList, ins_type
    user_input = update.message.text  # Получаем текст, содержащий(или нет) почту

    mailRegex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

    mailList = mailRegex.findall(user_input)  # Ищем почту

    if not mailList:  # Обрабатываем случай, когда почты нет
        update.message.reply_text('Email-адреса не найдены')
        return  # Завершаем выполнение функции

    mails = ''  # Создаем строку, в которую будем записывать адреса
    for i in range(len(mailList)):
        mails += f'{i + 1}. {mailList[i]}\n'  # Записываем очередную почту

    update.message.reply_text(mails)  # Отправляем сообщение пользователю

    keyboard = [
        [InlineKeyboardButton("да", callback_data='1')],
        [InlineKeyboardButton("нет", callback_data='2')],
    ]

    ins_type = 'mail'
    # Создаём объект клавиатуры
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    update.message.reply_text('Записать данные в базу?(да/нет):', reply_markup=reply_markup)

    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_emails(update: Update, context):
    update.message.reply_text('Обработка')
    update.message.reply_text(connect_to_db('mail_address'))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END

def get_phone_numbers(update: Update, context):
    update.message.reply_text('Обработка')
    update.message.reply_text(connect_to_db('phone_numbres'))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def verify_password(update: Update, context):
    user_input = update.message.text

    passRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')

    if re.match(passRegex, user_input) is not None:
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')

    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_release(update: Update, context):
    command = 'hostnamectl'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_uname(update: Update, context):
    command = 'uname -a'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_uptime(update: Update, context):
    command = 'uptime'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_df(update: Update, context):
    command = 'df -h'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_free(update: Update, context):
    command = 'free'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_mpstat(update: Update, context):
    command = 'mpstat'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_w(update: Update, context):
    command = 'w'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_auths(update: Update, context):
    command = 'last'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_critical(update: Update, context):
    command = 'journalctl -p crit -n 5'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_ps(update: Update, context):
    command = 'ps'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_ss(update: Update, context):
    command = 'ss | head'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_services(update: Update, context):
    command = 'systemctl list-units --type=service --state=running'
    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input == '-':
        command = 'dpkg -l | head -n 20'
    else:
        command = f'dpkg -l {user_input} | head -n 20'

    update.message.reply_text('Обработка')
    update.message.reply_text(connection(command))
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def get_repl_logs(update, context):
    output = subprocess.run(["tail", PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = output.stdout + output.stderr
    update.message.reply_text('Обработка')
    update.message.reply_text(output)
    update.message.reply_text('Обработка завершена')
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    dp.add_handler(CallbackQueryHandler(button))

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )



    convHandlerFindMail = ConversationHandler(
        entry_points=[CommandHandler('findMail', findMailCommand)],
        states={
            'findMail': [MessageHandler(Filters.text & ~Filters.command, findMail)],
        },
        fallbacks=[]
    )

    convHandlerVerify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerGetRelease = ConversationHandler(
        entry_points=[CommandHandler('get_release', get_releaseCommand)],
        states={
            'get_release': [MessageHandler(Filters.text & ~Filters.command, get_release)],
        },
        fallbacks=[]
    )

    convHandlerGetUname = ConversationHandler(
        entry_points=[CommandHandler('get_uname', get_unameCommand)],
        states={
            'get_uname': [MessageHandler(Filters.text & ~Filters.command, get_uname)],
        },
        fallbacks=[]
    )

    convHandlerGetUptime = ConversationHandler(
        entry_points=[CommandHandler('get_uptime', get_uptimeCommand)],
        states={
            'get_uptime': [MessageHandler(Filters.text & ~Filters.command, get_uptime)],
        },
        fallbacks=[]
    )

    convHandlerGetDf = ConversationHandler(
        entry_points=[CommandHandler('get_df', get_dfCommand)],
        states={
            'get_df': [MessageHandler(Filters.text & ~Filters.command, get_df)],
        },
        fallbacks=[]
    )

    convHandlerGetFree = ConversationHandler(
        entry_points=[CommandHandler('get_free', get_freeCommand)],
        states={
            'get_free': [MessageHandler(Filters.text & ~Filters.command, get_free)],
        },
        fallbacks=[]
    )

    convHandlerGetMpstat = ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', get_mpstatCommand)],
        states={
            'get_mpstat': [MessageHandler(Filters.text & ~Filters.command, get_mpstat)],
        },
        fallbacks=[]
    )

    convHandlerGetW = ConversationHandler(
        entry_points=[CommandHandler('get_w', get_wCommand)],
        states={
            'get_w': [MessageHandler(Filters.text & ~Filters.command, get_w)],
        },
        fallbacks=[]
    )

    convHandlerGetAuths = ConversationHandler(
        entry_points=[CommandHandler('get_auths', get_unameCommand)],
        states={
            'get_auths': [MessageHandler(Filters.text & ~Filters.command, get_auths)],
        },
        fallbacks=[]
    )

    convHandlerGetCritical = ConversationHandler(
        entry_points=[CommandHandler('get_critical', get_criticalCommand)],
        states={
            'get_critical': [MessageHandler(Filters.text & ~Filters.command, get_critical)],
        },
        fallbacks=[]
    )

    convHandlerGetPs = ConversationHandler(
        entry_points=[CommandHandler('get_ps', get_psCommand)],
        states={
            'get_ps': [MessageHandler(Filters.text & ~Filters.command, get_ps)],
        },
        fallbacks=[]
    )

    convHandlerGetSs = ConversationHandler(
        entry_points=[CommandHandler('get_ss', get_ssCommand)],
        states={
            'get_ss': [MessageHandler(Filters.text & ~Filters.command, get_ss)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    convHandlerGetServices = ConversationHandler(
        entry_points=[CommandHandler('get_services', get_servicesCommand)],
        states={
            'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services)],
        },
        fallbacks=[]
    )

    convHandlerGetReplLogs = ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', get_repl_logsCommand)],
        states={
            'get_repl_logs': [MessageHandler(Filters.text & ~Filters.command, get_repl_logs)],
        },
        fallbacks=[]
    )

    convHandlerGetEmails = ConversationHandler(
        entry_points=[CommandHandler('get_emails', get_emailsCommand)],
        states={
            'get_emails': [MessageHandler(Filters.text & ~Filters.command, get_emails)],
        },
        fallbacks=[]
    )

    convHandlerGetPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('get_phone_numbers', get_phone_numbersCommand)],
        states={
            'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, get_phone_numbers)],
        },
        fallbacks=[]
    )


    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindMail)
    dp.add_handler(convHandlerVerify_password)
    dp.add_handler(convHandlerGetRelease)
    dp.add_handler(convHandlerGetUname)
    dp.add_handler(convHandlerGetUptime)
    dp.add_handler(convHandlerGetDf)
    dp.add_handler(convHandlerGetFree)
    dp.add_handler(convHandlerGetMpstat)
    dp.add_handler(convHandlerGetW)
    dp.add_handler(convHandlerGetAuths)
    dp.add_handler(convHandlerGetCritical)
    dp.add_handler(convHandlerGetPs)
    dp.add_handler(convHandlerGetSs)
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(convHandlerGetServices)
    dp.add_handler(convHandlerGetReplLogs)
    dp.add_handler(convHandlerGetEmails)
    dp.add_handler(convHandlerGetPhoneNumbers)


    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
