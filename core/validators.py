# django
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MinimumLowerCaseValidator:
    msg = _('Sua senha deve conter pelo menos {min_length} caractere(s) em caixa baixa.')

    def __init__(self, min_length):
        self.min_length = min_length

    def validate(self, password, user=None):
        lower_count = 0
        for c in password:
            lower_count += 1 if c.islower() else 0

        if lower_count < self.min_length:
            raise ValidationError(self.msg.format(min_length=self.min_length))

    def get_help_text(self):
        return self.msg.format(min_length=self.min_length)


class MinimumUpperCaseValidator:
    msg = _('Sua senha deve conter pelo menos {min_length} caractere(s) em caixa alta.')

    def __init__(self, min_length):
        self.min_length = min_length

    def validate(self, password, user=None):
        uppercase_count = 0
        for c in password:
            uppercase_count += 1 if c.isupper() else 0

        if uppercase_count < self.min_length:
            raise ValidationError(self.msg.format(min_length=self.min_length))

    def get_help_text(self):
        return self.msg.format(min_length=self.min_length)


class MinimumNumberValidator:
    msg = _('Sua senha deve conter pelo menos {min_length} caractere(s) em numéricos.')

    def __init__(self, min_length):
        self.min_length = min_length

    def validate(self, password, user=None):
        number_count = 0
        for c in password:
            number_count += 1 if c.isdigit() else 0

        if number_count < self.min_length:
            raise ValidationError(self.msg.format(min_length=self.min_length))

    def get_help_text(self):
        return self.msg.format(min_length=self.min_length)


class MinimumSpecialCharactersValidator:
    msg = _('Sua senha deve conter pelo menos {min_length} caractere(s) em especiais.')

    def __init__(self, min_length):
        self.min_length = min_length

    def validate(self, password, user=None):
        special_count = 0
        for c in password:
            special_count += 1 if c.isascii() and not c.isalnum() else 0

        if special_count < self.min_length:
            raise ValidationError(self.msg.format(min_length=self.min_length))

    def get_help_text(self):
        return self.msg.format(min_length=self.min_length)
