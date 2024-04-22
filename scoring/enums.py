from enum import Enum


class Methods(str, Enum):
    OnlineScore = 'online_score'
    ClientsInterests = 'clients_interests'


class Genders(int, Enum):
    Unknown = 0
    Male = 1
    Female = 2
