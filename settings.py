import dataclasses
from dataclasses import dataclass


@dataclass
class String:
    API_KEY:str='2113467244:AAFSOi8Dj1INRWLBEIuuFwuOqkwYhtJoHL0'
    chg_count='chg_count'
    btn_home:str='На главную'
    btn_cart:str='Корзина'
    btn_item:str='Каталог'
    sqlite='sqlite:///data.db'
    text_home:str='Home '

def get_dict(cls):
    return dataclasses.asdict(cls)
