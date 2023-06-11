from abc import ABC, abstractmethod, abstractproperty
from random import choice, randint

CALCULATIONS = {
    '*': lambda a, b: a * b,
    '+': lambda a, b: a + b,
    "-": lambda a, b: a - b,
}
OPERATORS = tuple(CALCULATIONS)


class MathCaptcha:
    def __init__(self):
        self.numbers: list[int] = self.get_prandom_numbers()
        self.operator: str = self.get_prandom_operator()
        self.question = 'What is {} {} {} ? '.format(
            self.numbers[1], self.operator, self.numbers[0]
        )
        self.answer = self.get_answer()

    def get_prandom_numbers(self) -> list[int]:
        one = randint(1, 10)
        two = randint(one, 10)
        return [one, two]

    def get_prandom_operator(self) -> str:
        return choice(OPERATORS)

    def get_answer(self) -> int:
        return CALCULATIONS[self.operator](self.numbers[1], self.numbers[0])

    def __str__(self):
        return f'{self.numbers[1]} {self.operator} {self.numbers[0]} = {self.answer}'


class MathCaptchaManager:
    def __init__(self):
        self.captcha = self.generate()

    def generate(self) -> MathCaptcha:
        self.captcha = MathCaptcha()
        return self.captcha

    def check_answer(self, attempt: str) -> bool:
        try:
            attempt = int(attempt)
        except ValueError:
            return False
        return True if attempt == self.captcha.answer else False
