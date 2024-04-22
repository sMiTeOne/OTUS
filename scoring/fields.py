from abc import (
    ABC,
    abstractmethod,
)
from datetime import datetime as dt
from enums import Genders


class BaseField(ABC):
    def __init__(self, required: bool, nullable: bool) -> None:
        self.required = required
        self.nullable = nullable

    def check(self, name, data) -> str | None:
        if self.required and name not in data:
            return f'Field {name} is required'
        field_value = data.get(name)
        if not self.nullable and not field_value:
            return f'Field {name} is empty'
        if field_value and not self.is_correct_type(field_value):
            return f'Field {name} has wrong type'

    @abstractmethod
    def is_correct_type(self, value) -> bool:
        raise NotImplementedError

    def validate(self, name, value) -> str | None:
        return None


class IntField(BaseField):
    def is_correct_type(self, value) -> bool:
        return isinstance(value, int | None if self.nullable else int)


class CharOrIntField(BaseField):
    def is_correct_type(self, value) -> bool:
        return isinstance(value, str | int | None if self.nullable else str | int)


class CharField(BaseField):
    def is_correct_type(self, value) -> bool:
        return isinstance(value, str | None if self.nullable else str)


class ArgumentsField(BaseField):
    def is_correct_type(self, value) -> bool:
        return isinstance(value, dict | None if self.nullable else dict)


class ListField(BaseField):
    def is_correct_type(self, value) -> bool:
        return isinstance(value, list | None if self.nullable else list)


class DateField(BaseField):
    def is_correct_type(self, value) -> bool:
        if self.nullable and value is None:
            return True
        try:
            dt.strptime(value, '%d.%m.%Y')
        except (ValueError, TypeError):
            return False
        else:
            return True


class EmailField(CharField):
    def validate(self, name, value) -> str | None:
        if '@' not in value:
            return f'Field {name} has wrong format'


class PhoneField(CharOrIntField):
    def validate(self, name, value) -> str | None:
        phone_string = str(value)
        if len(phone_string) != 11:
            return f'Field {name} must be length 11'
        if not phone_string.startswith('7'):
            return f'Field {name} must start with 7'


class BirthDayField(DateField):
    def validate(self, name, value) -> str | None:
        timedelta = (dt.now() - dt.strptime(value, '%d.%m.%Y')).days
        if timedelta // 365 > 70:
            return f'Field {name} must be no more than 70 years old'


class GenderField(IntField):
    def validate(self, name, value) -> str | None:
        try:
            Genders(value)
        except ValueError:
            return f'Field {name} must be in range 0 to 2'


class ClientIDsField(ListField):
    def validate(self, name, value) -> str | None:
        for item in value:
            if not isinstance(item, int):
                return f'Field {name} must consist of integers'
