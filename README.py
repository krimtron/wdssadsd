import aiogram
from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.filters.state import State, StatesGroup
import random
import asyncio
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

bot = Bot(token='API TOKEN')
dp = Dispatcher()





@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    global correct_answers, incorrect_answers
    correct_answers = 0
    incorrect_answers = 0
    await message.reply("Привіт! Я готовий перевіряти твої знання математики. Готовий до першого питання?(введіть 'я готовий')")


    

# Define states
class States:
    START = 'start'
    LOCATION = 'location'
    RESULT = 'result'


# Define keyboard
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Get Weather'))


# Start command handler
@dp.message_handler(Command("start"), state="*")
async def cmd_start(message: types.Message):
    await message.reply("Welcome to the Weather Bot! Type /cancel any time to stop.", reply_markup=start_keyboard)
    await States.START.set()


# Start state handler
@dp.message_handler(state=States.START)
async def process_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
    await message.reply("Please enter the location for which you want to know the weather:")
    await States.LOCATION.set()


# Location state handler
@dp.message_handler(state=States.LOCATION)
async def process_location(message: types.Message, state: FSMContext):
    location = message.text
    try:
        weather_data = get_weather_data(location)
        temperature = weather_data['main']['temp'] - 273.15
        description = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']
        humidity = weather_data['main']['humidity']

        result_text = (
            f"Temperature: {temperature:.2f}°C\n"
            f"Weather: {description}\n"
            f"Wind Speed: {wind_speed} m/s\n"
            f"Humidity: {humidity}%"
        )

        await message.reply(result_text, reply_markup=ReplyKeyboardRemove())
        await States.RESULT.set()

    except Exception as e:
        logging.exception(f"Error getting weather data: {e}")
        await message.reply("Sorry, an error occurred while fetching weather data. Please try again.")

    await state.finish()


# Result state handler
@dp.message_handler(state=States.RESULT)
async def process_result(message: types.Message, state: FSMContext):
    await message.reply("What would you like to do next?", reply_markup=start_keyboard)
    await States.START.set()


# Function to get weather data from OpenWeatherMap API
def get_weather_data(location):
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}"
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()

    
    
async def main():
    print("Starting bot...")
    print("Bot username: @{}".format((await bot.me())))
    await dp.start_polling(bot)

asyncio.run(main())
