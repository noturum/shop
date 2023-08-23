from settings import String as string, dataclass

from telebot import TeleBot
from db_controller import User, Item, UserCart, Database
from keyboard import Keyboard as buttons
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
    ITEMS = string.btn_item
    CART = string.btn_cart
    CHG_COUNT = string.chg_count


class Message:
    def __init__(self, text, keyboard=None, item=None):
        self.__msg = None
        self.text = text
        self.id = None
        self.keyboard = keyboard
        self.item = item

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
        self.__id = id
        self.__state = State.HOME
        self.__messages = []
        self.selected_item = None

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
        msg.send_message(self.__id)
        self.__messages.append(msg)

    def claer_chat(self):
        for msg in self.__messages:
            msg.delete_message()
        self.__messages.clear()

    def set_state(self, state):
        self.claer_chat()
        self.__state = state

    def get_state(self):
        return self.__state

    def select_item(self, id):
        self.selected_item = id


def init(message):
    if db.select(User, [User.chat_id == id], True):
        db.session.add(User(chat_id=message.chat.id, name=message.from_user.username, type='user'))
        db.session.commit()
    chats[message.chat.id] = Chat(message.chat.id)


def main():
    @bot.message_handler(content_types=['text'])
    def point(message):
        bot.delete_message(message.chat.id, message.id)
        chat = chats[message.chat.id]
        if message.chat.id not in chats:
            init(message)
        match message.text:
            case State.HOME | '/start':
                chat.set_state(State.HOME)
                chat.add_message(Message(string.text_home, buttons().main(2).get_keyboard()))
            case State.ITEMS:
                chat.set_state(State.ITEMS)
                if len(items := db.select(Item)) > 0:
                    for item in items:
                        keyboard = buttons(buttons.INLINE)
                        if item.count==0:
                            keyboard.needed()
                        else:
                            keyboard.add_item(len(chat.get_message()))
                        chat.add_message(Message(str(item), keyboard.get_keyboard(), item))
                ...
            case State.CART:

                chat.set_state(State.CART)
                if len(items := chat.get_user().items) > 0:
                    for item in items:
                        keyboard = buttons(buttons.INLINE)
                        keyboard.counter(item.count).delete_item(len(chat.get_message(True)))

                        chat.add_message(Message(str(item), keyboard.get_keyboard(), item))
                ...

            case _:

                match chat.get_state():
                    case State.CHG_COUNT:
                        if message.text.is_digit():
                            item = (msg := chat.get_message(chat.selected_item)).item.id
                            db.update(UserCart, [UserCart.uid == message.chat.id, UserCart.item == item],
                                      {'count': int(message.text)})
                            keyboard = buttons(buttons.INLINE)
                            keyboard.counter(int(message.text))
                            msg.edit_message(keyboard=keyboard.get_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data.find('counter_dec') == 0)
    def counter_dec(call):

        id_msg = int(call.data.split('@')[1])
        item = (msg := chats[call.message.chat.id].get_message(id_msg)).item.id
        if count := db.select(UserCart.count, (UserCart.uid == call.message.chat.id, UserCart.item == item), one=True)[
                        0] > 1:
            db.update(UserCart, [UserCart.uid == call.message.chat.id, UserCart.item == item],
                      {'count': UserCart.count - 1})
            keyboard = buttons(buttons.INLINE)
            keyboard.counter(count - 1)
            msg.edit_message(keyboard=keyboard.get_keyboard())
        else:
            call.data = f'delete_item@{id_msg}'
            delete_item(call)
        # todo: logics inc count item on cart

    @bot.callback_query_handler(func=lambda call: call.data.find('counter_inc') == 0)
    def counter_inc(call):
        id_msg = int(call.data.split('@')[1])
        item = (msg := chats[call.message.chat.id].get_message(id_msg)).item.id
        if db.is_available_items(msg.item.id, 1):
            count = db.select(UserCart.count, (UserCart.uid == call.message.chat.id, UserCart.item == item), one=True)[0]
            db.update(UserCart, [UserCart.uid == call.message.chat.id, UserCart.item == item],
                      {'count': UserCart.count + 1})
            db.update(Item, [Item.id == msg.item.id, ], {'count': Item.count - 1})
            keyboard = buttons(buttons.INLINE)
            keyboard.counter(count + 1)
            msg.edit_message(keyboard=keyboard.get_keyboard())
        else:
            bot.answer_callback_query(call.id, f'Товар кончился', show_alert=True)

        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('chenge_count') == 0)
    def chenge_count(call):
        id_msg = int(call.data.split('@')[1])
        bot.answer_callback_query(call.id, f'Введите колличество товара', show_alert=True)
        chats[call.message.chat.id].set_state(State.CHG_COUNT)
        chats[call.message.chat.id].select_item(id_msg)

    @bot.callback_query_handler(func=lambda call: call.data.find('add_item') == 0)
    def add_item(call):
        id_msg = int(call.data.split('@')[1])
        msg = chats[call.message.chat.id].get_message(id_msg)
        if db.is_available_items(msg.item.id, 1):
            keyboard = buttons(buttons.INLINE)
            keyboard.counter(1)

            msg.edit_message(
                keyboard=keyboard.get_keyboard())
            db.insert(UserCart, uid=call.message.chat.id, item=msg.item.id)
            db.update(Item, [Item.id == msg.item.id,], {'count': Item.count - 1})
            bot.answer_callback_query(call.id, f'{msg.item.name} в корзине', show_alert=True)
        else:
            keyboard = buttons(buttons.INLINE)
            keyboard.needed()
            msg.edit_message(
                keyboard=keyboard.get_keyboard())

        # todo: try use relation

        ...

    @bot.callback_query_handler(func=lambda call: call.data.find('delete_item') == 0)
    def delete_item(call):
        id_msg = int(call.data.split('@')[1])
        (msg := chats[call.message.chat.id].get_message(id_msg)).delete_message()
        count = db.delete(UserCart, [UserCart.uid == call.message.chat.id, UserCart.item == msg.item.id],
                          UserCart.count)
        db.update(Item, [Item.id == msg.item.id, ], {'count': Item.count + count})

    bot.polling(none_stop=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('error', exc_info=True)
        exit(1)
