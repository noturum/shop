from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
import settings


class Keyboard:
    INLINE = 'inline'
    REPLY = 'reply'
    def_keyboard = {'inline': InlineKeyboardMarkup, 'reply': ReplyKeyboardMarkup}

    def __init__(self, type='inline'):
        self.__keyboard = self.def_keyboard[type]()

    def main(self, row_width=2):
        row=[]
        for btn in settings.get_dict(settings.String()).items():
            if 'btn' in btn[0]:
                if len(row) < row_width:
                    row.append(btn[1])
                else:
                    self.add_btn(row)
                    row=[btn[1]]
        self.add_btn(row)
        return self

    def counter(self, val):
        self.add_btn((InlineKeyboardButton(text=f'-', callback_data='counter_dec'),
                      InlineKeyboardButton(text=f'{val}', callback_data='chenge_count'),
                      InlineKeyboardButton(text=f'+', callback_data='counter_inc')))
        return self
    def add_item(self):
        self.add_btn((InlineKeyboardButton(text=f'+', callback_data='add_item'),))
        return self
    def delete_item(self):
        self.add_btn((InlineKeyboardButton(text=f'Удалить', callback_data='delete_item'),))
        return self
    def add_btn(self, func):
        self.__keyboard.add(*func)

    def get_keyboard(self):
        return self.__keyboard
