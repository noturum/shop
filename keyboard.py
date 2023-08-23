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
                    self.__add_btn(row)
                    row=[btn[1]]
        self.__add_btn(row)

        return self

    def counter(self, val,ind):
        self.__add_btn((InlineKeyboardButton(text=f'-', callback_data=f'counter_dec@{ind}'),
                      InlineKeyboardButton(text=f'{val}', callback_data=f'chenge_count@{ind}'),
                      InlineKeyboardButton(text=f'+', callback_data=f'counter_inc@{ind}')))
        return self
    def add_item(self,ind):
        self.__add_btn((InlineKeyboardButton(text=f'+', callback_data=f'add_item@{ind}'),))
        return self
    def delete_item(self,ind):
        self.__add_btn((InlineKeyboardButton(text=f'Удалить', callback_data='delete_item'),))
        return self
    def __add_btn(self, func):
        self.__keyboard.add(*func)

    def get_keyboard(self):
        return self.__keyboard

    def needed(self):
        pass
