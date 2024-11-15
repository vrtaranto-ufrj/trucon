class SalaException(Exception):
    def __init__(self, message):
        self.message = message

class SalaCheiaException(SalaException):
    def __init__(self):
        super().__init__("Sala cheia")

class JogadorJaNaSalaException(SalaException):
    def __init__(self):
        super().__init__("Jogador já está na sala")

class JogadorJaEmOutraSalaException(SalaException):
    def __init__(self):
        super().__init__("Jogador já está em outra sala")
