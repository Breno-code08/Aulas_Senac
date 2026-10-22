from conta import Conta

class ContaCorrente(Conta):
    def __init__(self, nome, saldo, limite):
        super().__init__(nome, saldo)
        self.limite = limite
    def exibir_saldo(self):
        print(f"Seu saldo é {self.saldo + self.limite}")
