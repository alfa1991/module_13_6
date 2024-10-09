import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import logging

# Токен вашего бота
API_TOKEN = '7707735615:AAGTv-6x0mrzo4wf8svUoJBPRNzCLA9r24Y'  # Замените на ваш токен

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объект бота
bot = Bot(token=API_TOKEN)

# Создаем объект диспетчера с хранилищем состояний
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Создаем объект роутера
router = Router()

# Определяем группу состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать'), KeyboardButton(text='Информация')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Создаем Inline-клавиатуру для расчета
inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
         InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)

# Обработчик команды /start
@router.message(Command(commands=['start']))
async def start(message: Message):
    logging.info("Команда /start обработана")
    await message.answer('Привет! Я бот, помогающий твоему здоровью. Выберите действие:', reply_markup=keyboard)

# Обработчик нажатия кнопки "Рассчитать"
@router.message(lambda message: message.text == 'Рассчитать')
async def main_menu(message: Message):
    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)

# Обработчик для получения формул
@router.callback_query(lambda call: call.data == 'formulas')
async def get_formulas(call):
    logging.info("Формулы расчета запрошены")  # Логирование
    await call.message.answer('Формула Миффлина-Сан Жеора: 10 * вес + 6.25 * рост - 5 * возраст + 5 (для мужчин).')
    await call.answer()  # Закрываем уведомление о нажатии кнопки

# Обработчик для расчета калорий
@router.callback_query(lambda call: call.data == 'calories')
async def set_age(call, state: FSMContext):
    await state.set_state(UserState.age)  # Устанавливаем состояние age
    await call.message.answer('Введите свой возраст:')
    await call.answer()  # Закрываем уведомление о нажатии кнопки

# Обработчик возраста
@router.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    await state.update_data(age=message.text)  # Обновляем данные состояния
    await state.set_state(UserState.growth)  # Устанавливаем состояние growth
    await message.answer('Введите свой рост:')

# Обработчик роста
@router.message(UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    await state.update_data(growth=message.text)  # Обновляем данные состояния
    await state.set_state(UserState.weight)  # Устанавливаем состояние weight
    await message.answer('Введите свой вес:')

# Обработчик веса и расчет калорий
@router.message(UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)  # Обновляем данные состояния
    data = await state.get_data()  # Получаем все данные

    # Извлекаем данные
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула для расчета нормы калорий (для мужчин)
    calories = 10 * weight + 6.25 * growth - 5 * age + 5  # Расчет

    await message.answer(f'Ваша норма калорий: {calories} ккал в день.')
    await state.clear()  # Завершаем состояние

# Обработчик всех остальных сообщений
@router.message()
async def all_messages(message: Message):
    await message.answer('Пожалуйста, используйте команду /start или нажмите кнопку "Рассчитать", чтобы продолжить.')

# Функция для правильного завершения работы бота
async def shutdown(dispatcher: Dispatcher):
    await bot.session.close()  # Закрываем сессию бота

# Основная функция
async def main():
    # Включаем роутер в диспетчер
    dp.include_router(router)

    # Запуск polling
    try:
        await dp.start_polling(bot)
    finally:
        await shutdown(dp)  # Закрываем ресурсы при завершении

if __name__ == '__main__':
    try:
        # Запускаем приложение
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
