class AccountNameError(Exception):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return 'Имя пользователя {} должно быть не более 25 символов'.format(self.accountname)


class ResponseCodeError(Exception):
    def __init__(self, response_code):
        self.response_code = response_code

    def __str__(self):
        return 'Неверная длина кода ответа сервера {}. Длина кода должна составлять 3 символа.'.format(self.response_code)



