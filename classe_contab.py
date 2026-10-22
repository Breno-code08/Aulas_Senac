# Solução em python
class ContaBancaria:
    def __init__(self, titular, saldo):
         self.nome = titular
         self.__saldo = saldo
    def depositar(self, deposito):
      self.deposito = deposito
      if self.deposito > 0:
         self.saldo += self.deposito
    def sacar(self, saque):
         self.saque = saque
         self.saldo -= self.saque
# Testando a classe
    def consultar_saldo(self):
       print(f"Seu saldo é igual {self.saldo}")


