import os
import openai
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter


load_dotenv()


API_TOKEN = os.getenv("telkey")
openai.api_key = os.getenv("aikey")
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
adm = os.getenv('admins')
admins = [int(admin) for admin in adm.split(',')]


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.id in admins


@dp.message_handler(IsGroup(), commands=['image'])
async def create_ing(message: types.Message):
    print(message)
    message.text = message.text.split()[1:]
    message.text = ' '.join(message.text)
    try:
        response = openai.Image.create(
          prompt=message.text,
          n=1,
          size="1024x1024"
        )
        image_url = response['data'][0]['url']
        await message.answer_photo(image_url)
    except Exception:
        await message.reply('Не балуй')


@dp.message_handler(IsGroup(), lambda message: '@external_stupidity_bot' in message.text)
@dp.message_handler(IsGroup(), lambda message: message.reply_to_message, lambda message: message.reply_to_message.from_user.username == "external_stupidity_bot")
async def answer(message: types.Message):
    print(message)
    if '@external_stupidity_bot' in message.text:
        message.text = message.text.split()[1:]
        message.text = ' '.join(message.text)
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=message.text,
      temperature=0.3,
      max_tokens=1000,
      top_p=1.0,
      frequency_penalty=0.3,
      presence_penalty=0.0,
    )
    await message.reply(response['choices'][0]['text'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
