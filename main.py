from settings import String as string
from dataclasses import dataclass
from telebot import TeleBot
from db_controller import User, Item, UserCart, Database
import keyboard as buttons
import logging

logging.basicConfig(filename='error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)

bot = TeleBot(string.API_KEY)
chats = {}
db = Database()


@dataclass()
class State:
    HOME = string.btn_home
    ITEM = string.btn_item
    CART = string.btn_cart


class Message:
    def __init__(self, text, keyboard=None, item=None):
        self.__msg = None
        self.text = text
        self.id = None
        self.keyboard = keyboard

    def send_message(self, chat_id):
        self.__msg = bot.send_message(chat_id=chat_id, text=self.text, reply_markup=self.keyboard)

    def delete_message(self):
        bot.delete_message(self.__msg.chat.id, self.__msg.id)

    def edit_message(self, text=None, keyboard=None):
        if text:
            bot.edit_message_text(text, self.__msg.chat.id, self.__msg.id)
        if keyboard:
            bot.edit_message_reply_markup(self.__msg.chat.id, self.__msg.id, reply_markup=keyboard)


class Chat:
    def __init__(self, id):
        self.__state = State.HOME
        self.__messages = []
        self.__select_item = None

    def get_user(self, id):
        return db.select(User, [User.chat_id == id], one=True)[0]

    def get_message(self, all=True):
        if all:
            return self.__messages
        else:
            for msg in self.__messages:
                if msg.id == all:
                    return msg

    def add_message(self, msg: Message):
        msg.id = len(self.__messages)
        msg.send_message()
        self.__messages.append(msg)

    def claer_chat(self):
        for msg in self.__messages:
            msg.delete_message
        self.__messages.clear()

    def set_state(self, state):
        self.claer_chat()
        self.__state = state

    def select_item(self, id):
        self.__select_item = id


def init(message):
    if db.select(User, [User.chat_id == id], True):
        db.session.add(User(chat_id=message.chat.id, name=message.from_user.username, type='user'))
        db.session.commit()
    chats[message.chat.id] = Chat(message.chat.id)


def main():
    @bot.message_handler(content_types=['text'])
    def point(message):
        bot.delete_message(message.chat.id, message.id)
        if message.chat.id not in chats:
            init(message)
        match message.text:
            case State.HOME | '/start':
                chats[message.chat.id].set_state(State.HOME)
                chats[message.chat.id].add_message(Message(string.text_home, buttons.Keyboard().main(2).get_keyboard()))
            case State.ITEMS:
                chats[message.chat.id].set_state(State.ITEM)
                if len(items := db.select(Item)) > 0:
                    for item in items:
                        keyboard = buttons.Keyboard(buttons.Keyboard.INLINE)
                        keyboard.add_btn(keyboard.add_item(len(chats[message.chat.id].get_message())))
                        chats[message.chat.id].add_message(Message(item, keyboard.get_keyboard()))
                ...
            case State.CART:
                chats[message.chat.id].set_state(State.CART)
                chats[message.chat.id].get_user()
                ...
            case _:
                ...

    @bot.callback_query_handler(func=lambda call: call.data.find('counter_dec') == 0)
    def counter_dec(call):
        id_msg = int(call.data.split('@')[1])
        if len(items:=chats[call.message.chat.id].get_user().items)>1:
            ...
        else:
            ...
        # todo: logics inc count item on cart

    @bot.callback_query_handler(func=lambda call: call.data.find('counter_inc') == 0)
    def counter_inc(call):

        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('chenge_count') == 0)
    def chenge_count(call):
        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('add_item') == 0)
    def add_item(call):
        id_msg = int(call.data.split('@')[1])
        (msg := chats[call.message.chat.id].get_message(id_msg)).edit_message(
            keyboard=buttons.add_btn(buttons.counter(1)))
        db.insert(UserCart, uid=call.message.chat.id, item=msg.item.id)
        # todo: try use relation

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
