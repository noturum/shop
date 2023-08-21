import dataclasses
from dataclasses import dataclass


@dataclass
class String:
    API_KEY:str=''
    btn_home:str='На главную'
    btn_cart:str='Корзина'
    btn_item:str='Каталог'
    sqlite='sqlite:///data.db'

def get_dict(cls):
    return dataclasses.asdict(cls)
