from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import asyncio

# Токен вашего бота
API_TOKEN = 'YOUR_BOT_TOKEN'

# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Создаем класс состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Функция для расчета калорий по формуле Миффлина-Сан Жеора (для женщин)
def calculate_calories(age, growth, weight):
    # Формула для женщин
    return (10 * weight) + (6.25 * growth) - (5 * age) - 161

# Функция для отправки формулы
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("Формула Миффлина-Сан Жеора (для женщин):\n(10 * вес) + (6.25 * рост) - (5 * возраст) - 161")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Рассчитать']
    keyboard.add(*buttons)
    await message.answer('Привет! Хочешь рассчитать норму калорий?', reply_markup=keyboard)

# Обработчик нажатия на кнопку "Рассчитать"
@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
        types.InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
    ]
    keyboard.add(*buttons)
    await message.answer('Выберите опцию:', reply_markup=keyboard)

# Обработчик для ввода возраста
@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Введите свой возраст:')
    await state.set_state(UserState.age)

# Обработчик для получения формулы
@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await get_formulas(call)

# ... остальные обработчики (set_growth, set_weight) остаются без изменений ...

# Запуск бота
async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())