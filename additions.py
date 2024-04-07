from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from CGRtools import smiles, MoleculeContainer, CGRContainer, ReactionContainer, SDFWrite, RDFWrite
from os import system
from pickle import dumps
from io import StringIO, BytesIO


class MyState(StatesGroup):
    wait_name = State()
    wait_date = State()
    wait_smiles = State()


class Keyboard:
    mode_buttons = (('Convert SMILES', 'Convert SMILES'), ('Extract rule', 'Extract rule'))
    structure_buttons = (('Molecule or CGR', 'Molecule or CGR'), ('Reaction', 'Reaction'))
    type_buttons = (('File', 'File'), ('Picture', 'Picture'))

    @staticmethod
    def new_keyboard(button_names):
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=text, callback_data=data) for text, data in button_names]
        keyboard.add(*buttons)
        return keyboard

    @property
    def structure_choice(self):
        return self.new_keyboard(self.structure_buttons)

    @property
    def type_choice(self):
        return self.new_keyboard(self.type_buttons)

    @property
    def mode_choice(self):
        return self.new_keyboard(self.mode_buttons)


class Handler():
    def __init__(self, bot):
        self.bot = bot
        self.structure_buffer = {}
        self.users_queries = {}


    async def convert_smiles(self, query: types.CallbackQuery):
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=Keyboard().structure_choice)


    async def extract_rule(self, query: types.CallbackQuery):
        await query.answer('v razrabotke')
        # await query.message.edit_reply_markup(reply_markup=Keyboard().type_choice)


    async def molecule_or_cgr(self, query: types.CallbackQuery):
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=Keyboard().type_choice)


    async def reaction(self, query: types.CallbackQuery):
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=Keyboard().type_choice)


    async def picture(self, query: types.CallbackQuery):
        # await query.answer()
        # await query.message.edit_reply_markup()
        # await query.message.answer('Write SMILES')
        # await query.answer('Write SMILES')
        # await MyState().wait_smiles.set()

        print(self.structure_buffer)
        print(self.users_queries)

        structure_smiles = self.users_queries[query.from_user.id]
        structure = self.structure_buffer[structure_smiles]
        structure.depict_settings(aam=False)

        file_name = hash(structure)
        with open(f'0{file_name}.svg', 'w') as file:
            file.write(structure.depict())
        system(f'inkscape --export-png=0{file_name}.png --export-dpi=1000 0{file_name}.svg')

        # picture_string = dumps(f'0{file_name}.png')
        # self.bot.database.insert_picture(query.message.text, picture_string)

        await query.message.answer_photo(types.input_file.InputFile(f'0{file_name}.png'), caption=f'Your structure {structure_smiles}')
        await query.message.delete_reply_markup()


    async def file(self, query: types.CallbackQuery):
        # await query.answer()
        # await query.message.edit_reply_markup()
        # await query.answer('Write SMILES')
        # await MyState().wait_smiles.set()

        structure_smiles = self.users_queries[query.from_user.id]
        structure = self.structure_buffer[structure_smiles]
        pseudo_file = StringIO()
        
        if isinstance(structure, (MoleculeContainer, CGRContainer)):
            with SDFWrite(pseudo_file) as molecule_file:
                molecule_file.write(structure)
                pseudo_file.seek(0)
                bytes_pseudo_file = BytesIO(pseudo_file.read().encode('utf-8'))
            await query.message.answer_document(types.input_file.InputFile(bytes_pseudo_file, filename='your_molecule.sdf'), caption=f'Your molecule {structure_smiles}')

        elif isinstance(structure, ReactionContainer):
            with RDFWrite(pseudo_file) as reaction_file:
                reaction_file.write(structure)
                pseudo_file.seek(0)
                bytes_pseudo_file = BytesIO(pseudo_file.read().encode('utf-8'))
            await query.message.answer_document(types.input_file.InputFile(bytes_pseudo_file, filename='your_reaction.rdf'), caption=f'Your reaction {structure_smiles}')
        await query.message.delete_reply_markup()


    async def smileses(self, message: types.Message):
        try:
            structure = smiles(message.text)
            structure.clean2d()
        except Exception:
            await message.reply("It's not SMILES")
            await message.answer('Write SMILES')
        else:
            self.users_queries[message.from_user.id] = message.text
            self.structure_buffer[message.text] = structure
            if isinstance(structure, (MoleculeContainer, CGRContainer)):
                await message.answer('In what format do you want to get the molecule?', reply_markup=Keyboard().type_choice)
            elif isinstance(structure, ReactionContainer):
                await message.answer('In what format do you want to get the reaction?', reply_markup=Keyboard().type_choice)
