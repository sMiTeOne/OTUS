from copy import deepcopy
from fields import (
    BaseField,
    CharField,
    DateField,
    EmailField,
    PhoneField,
    GenderField,
    BirthDayField,
    ClientIDsField,
    ArgumentsField,
)
ADMIN_LOGIN = "admin"


class Serializer:
    def __init__(self, data: dict) -> None:
        self.data = deepcopy(data)
        self.valid_data = {}
        self.errors = []
        self.fields = []

        for property in dir(self):
            field = getattr(self, property)
            if isinstance(field, BaseField):
                self.fields.append(property)

    def validate_request(self):
        for field_name in self.fields:
            field_obj : BaseField = getattr(self, field_name)
            field_value = self.data.get(field_name)
            if error := field_obj.check(field_name, self.data):
                self.errors.append(error)
            if error := field_obj.validate(field_name, field_value):
                self.errors.append(error)


class ClientsInterestsRequest(Serializer):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Serializer):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(Serializer):

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)
    
    def validate_arguments(self) -> None:
        method = self.data['method']
        arguments = self.data['arguments']
        
        if not (request_method_class := METHODS_MAPPING.get(method)):
            return self.errors.append(f'Method {method} is not supported')
        
        request_method : Serializer = request_method_class(arguments)
        request_method.validate_request()
        self.errors.extend(request_method.errors)


METHODS_MAPPING : dict[str, Serializer] = {
    'clients_interests': ClientsInterestsRequest,
    'online_score': OnlineScoreRequest,
}
