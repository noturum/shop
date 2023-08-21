from settings import String as string
from dataclasses import dataclass
from telebot import TeleBot
import db_controller
import logging

logging.basicConfig(filename='error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)

bot = TeleBot(string.API_KEY)
chats = {}
db=db_controller.Database()
@dataclass()
class State:
    HOME = string.btn_home
    ITEM = string.btn_item
    CART = string.btn_cart



class Message:
    def __init__(self, text, keyboard=None):
        self.__msg = None
        self.text=text
        self.keyboard=keyboard

    def send_message(self,chat_id):
        self.__msg=bot.send_message(chat_id=chat_id,text=self.text,reply_markup=self.keyboard)

    def delete_message(self):
        bot.delete_message(self.__msg.chat.id,self.__msg.id)

    def edit_message(self, text=None, keyboard=None):
        if text:
            bot.edit_message_text(text,self.__msg.chat.id,self.__msg.id)
        if keyboard:
            bot.edit_message_reply_markup(self.__msg.chat.id,self.__msg.id,reply_markup=keyboard)


class Cart:
    def __init__(self, id):
        self.id = id

    def get_cart_item(self):
        ...


    def clear_cart(self):
        ...


class Chat:
    def __init__(self, id):
        self.__state = State.HOME
        self.__id = id
        self.__type = self.get_type(id)
        self.__messages = []
        self.__cart = self.get_cart()

    def get_type(self):
        ...

    def add_message(self, msg: Message):
        ...

    def claer_chat(self):
        ...

    def get_cart(self):
        return Cart(self.id).get_cart_item()

    def set_state(self, state):
        ...


def init(id):
    ...


def main():
    @bot.message_handler(content_types=['text'])
    def point(message):
        # todo: delete message from user
        if message.chat.id in chats:
            init(message.chat.id)
        match message.text:
            case State.HOME | '/start':
                chats[message.chat.id].set_state(State.HOME)
                ...
            case State.ITEMS:
                ...
            case State.CART:
                ...
            case _:
                ...

    @bot.callback_query_handler(func=lambda call: call.data.find('counter_dec') == 0)
    def counter_dec(call):
        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('counter_inc') == 0)
    def counter_inc(call):
        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('chenge_count') == 0)
    def chenge_count(call):
        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('add_item') == 0)
    def add_item(call):
        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('delete_item') == 0)
    def delete_item(call):
        ...
    bot.polling(none_stop=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('error', exc_info=True)
        exit(1)