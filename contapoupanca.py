from conta import Conta

class ContaPoupanca(Conta):
    def __init__(self, nome, saldo, taxa_juros):
        super().__init__(nome, saldo)
        self.taxa_juros = taxa_juros

    def exibir_juros(self):        
        print(f"Seu saldo com a taxa atual de juros é {self.saldo + (self.saldo * self.taxa_juros)}")