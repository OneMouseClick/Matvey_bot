import asyncio
import logging
import random
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Конфигурация бота
BOT_TOKEN = '7993392556:AAHnJnYR72czsj5jz-2Sm0acMJ6NfA8GaO8'
CHAT_ID = -1001910599516  # ID группового чата

# Путь к файлу для хранения состояния
STATE_FILE = 'duty_state.txt'

# Список дежурных с телеграм-никнеймами
DUTY_PERSONS = [
    "@balahonovv",  # Артем Балахонов
    "@akuznetsova7",  # Аня Кузнецова
    "@axvaminerale",  # Аня Алексеева
    "@dimovadi",  # Диана Димова
    "@mady1209",  # Максим Диброва
    "@ArtiomPrim",  # Примаков Артем
    "@mmmmmatch",  # Матвей Чичин
    "@tatasha1",  # Таня Сумакова
    "@matveykondratev",  # Матвей Кондратьев
    "@Egor_Below",  # Шалаевский Егор
    "@sofa_nova",  # Софа Иванова
    "@slezy_mitricha",  # Арина Маковская
    "@AndrewKononovv",  # Андрей Кононов
    "@slavchanskiy3000bulbulator",  # Слава Вороновский
    "@EATHE_SUS",  # Ваня Шмаков
    "@Matthew_Dlugy",  # Матвей Длуги
    "@stepanstepanstepanstepanstepa",  # Степа Лукашевич
    "@zavkseniaa",  # Ксюша Завалишина
    "@m0tyaB0ychik",  # Матвей Бойченко
    # Список без токена
    "Кирилл Шевцов",
    "Никита Спирин",
    "Саша Астахов",
    "Аня Штурман",
    "Анударь Сарантуяа"
]

# Список мотивирующих сообщений
MOTIVATIONAL_MESSAGES = [
    "Вы сегодня будете просто великолепны! 💪",
    "Сегодня ваш день - покажите все, на что способны! 🌟",
    "Верьте в себя, вы справитесь лучше всех! 🚀",
    "Дежурство - это не работа, а возможность блеснуть! ✨",
    "Вы готовы творить чудеса сегодня? 💡"
]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Scheduler для отправки ежедневных сообщений
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


def read_used_duty_persons():
    """Чтение использованных дежурных из файла"""
    try:
        with open(STATE_FILE, 'r') as f:
            return set(f.read().strip().split(','))
    except FileNotFoundError:
        return set()


def write_used_duty_persons(used_persons):
    """Запись использованных дежурных в файл"""
    with open(STATE_FILE, 'w') as f:
        f.write(','.join(used_persons))


def select_duty_persons():
    """Выбор двух дежурных, исключая ранее использованных"""
    # Читаем использованных дежурных
    used_duty_persons = read_used_duty_persons()

    # Если использованы все дежурные, очищаем файл
    if len(used_duty_persons) >= len(DUTY_PERSONS):
        used_duty_persons.clear()
        # Очистка файла
        with open(STATE_FILE, 'w') as f:
            f.write('')

    # Фильтруем список, исключая ранее использованных
    available_persons = [
        person for person in DUTY_PERSONS
        if person not in used_duty_persons
    ]

    # Выбираем двух случайных дежурных
    if len(available_persons) >= 2:
        duty_pair = random.sample(available_persons, 2)
        used_duty_persons.update(duty_pair)
    else:
        # Если недостаточно доступных, выбираем из всего списка
        duty_pair = random.sample(DUTY_PERSONS, 2)
        used_duty_persons.clear()
        used_duty_persons.update(duty_pair)

    # Сохраняем использованных дежурных
    write_used_duty_persons(used_duty_persons)

    return duty_pair


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer("Бот дежурств активирован!")


async def send_daily_duty_message():
    """Отправка ежедневного сообщения о дежурных"""
    today = datetime.now().weekday()

    # В воскресенье не дежурим
    if today == 6:
        return

    duty_persons = select_duty_persons()
    motivation = random.choice(MOTIVATIONAL_MESSAGES)

    message = (f"🕒 Сегодня дежурят:\n"
               f"• {duty_persons[0]}\n"
               f"• {duty_persons[1]}\n\n"
               f"{motivation}")

    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")


async def main():
    """Основная функция запуска бота"""
    # Добавление задачи в scheduler
    scheduler.add_job(
        send_daily_duty_message,
        CronTrigger(hour=7, minute=30, timezone='Europe/Moscow')
    )
    scheduler.start()

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
