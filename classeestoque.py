
class Estoque:
    def __init__(self, produto, quantidade = 0):
         self.produto = produto
         self.quantidade = quantidade
         
    def adicionar(self, add): 
        self.add = add
        if self.add> 0:
                self.quantidade += self.add
    def remover(self):  
        self.quantidade -= self.remove
# Testando a classe
    def consultar(self):
        print(f"Seu estoque de {self.produto} é igual {self.quantidade}")

p1 = Estoque ("Caneta", 0)   
p1.adicionar (100)
p1.consultar ()   