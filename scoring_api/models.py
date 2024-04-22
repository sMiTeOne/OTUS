from abc import (
    ABC,
    abstractmethod,
)
from copy import deepcopy

from enums import HTTPStatus
from fields import (
    BaseField,
    CharField,
    DateField,
    EmailField,
    PhoneField,
    GenderField,
    BirthDayField,
    ArgumentsField,
    ClientIDsField,
)
from scoring import (
    get_score,
    get_interests,
)

ADMIN_LOGIN = 'admin'


class Serializer(ABC):
    def __init__(self, data: dict) -> None:
        self.data = deepcopy(data)
        self.errors = []
        self.fields = []

        for property in dir(self):
            field = getattr(self, property)
            if isinstance(field, BaseField):
                self.fields.append(property)

    def validate_request(self):
        for field_name in self.fields:
            field_obj: BaseField = getattr(self, field_name)
            if error := field_obj.check(field_name, self.data):
                self.errors.append(error)
                continue
            if field_value := self.data.get(field_name):
                if error := field_obj.validate(field_name, field_value):
                    self.errors.append(error)

    @abstractmethod
    def execute(self, arguments: dict, context: dict | None = None) -> tuple[dict | HTTPStatus]:
        raise NotImplementedError


class ClientsInterestsRequest(Serializer):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def execute(self, arguments: dict, context: dict | None = None) -> tuple[dict | HTTPStatus]:
        self.validate_request()
        if self.errors:
            return self.errors, HTTPStatus.INVALID_REQUEST
        context["nclients"] = len(arguments['client_ids'])
        return {client_id: get_interests() for client_id in arguments['client_ids']}, HTTPStatus.OK


class OnlineScoreRequest(Serializer):
    ONLINE_SCORE_PAIRS = (
        {'phone', 'email'},
        {'gender', 'birthday'},
        {'first_name', 'last_name'},
    )

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def execute(self, arguments: dict, context: dict | None = None) -> tuple[dict | HTTPStatus]:
        self.validate_request()
        if self.errors:
            return self.errors, HTTPStatus.INVALID_REQUEST
        if not any((pair <= set(context["has"]) for pair in self.ONLINE_SCORE_PAIRS)):
            return 'Missing pairs of fields', HTTPStatus.INVALID_REQUEST
        if context["login"] == ADMIN_LOGIN:
            score = 42
        else:
            score = get_score(context, **arguments)
        return {'score': score}, HTTPStatus.OK


class MethodRequest(Serializer):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def execute(self):
        pass
