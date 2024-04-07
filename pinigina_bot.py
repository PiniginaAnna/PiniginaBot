from aiogram import executor, types
from additions import Keyboard, Handler, MyState
from start import bot, dispatcher


keyboard = Keyboard()
handler = Handler(bot)


@dispatcher.message_handler(commands='start')
async def start(message):
    user_name = message.from_user.id
    print(user_name)
    # if user_name is None:
    #     bot.database.insert_user(message.from_user.id, message.from_user.username, '0000-10-10')
    await message.answer('What is your name?')
    await MyState.wait_name.set()


@dispatcher.message_handler(state=MyState.wait_name)
async def add_user_data(message, state):
    name = message.text
    await state.update_data(name=name)
    await message.answer('What is your date of birth?')
    await MyState.wait_date.set()


@dispatcher.message_handler(state=MyState.wait_date)
async def add_user_data(message, state):
    date = message.text
    await state.update_data(date=date)
    user_data = await state.get_data()
    await message.answer('What do you want?', reply_markup=keyboard.mode_choice)
    await state.reset_state()


# dispatcher.register_message_handler(handler.start, commands='start')

dispatcher.register_callback_query_handler(handler.convert_smiles, text='Convert SMILES')
dispatcher.register_callback_query_handler(handler.extract_rule, text='Extract rule')

dispatcher.register_callback_query_handler(handler.molecule_or_cgr, text='Molecule or CGR')
dispatcher.register_callback_query_handler(handler.reaction, text='Reaction')

dispatcher.register_callback_query_handler(handler.picture, text='Picture')
dispatcher.register_callback_query_handler(handler.file, text='File')

dispatcher.register_message_handler(handler.smileses)


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=True)
