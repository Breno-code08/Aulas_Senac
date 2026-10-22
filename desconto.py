# Solução em Python
class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco
    def exibir_produto(self):
        print(f"Produto: {self.nome} | Preço R$ {self.preco:.2f}")
    def aplicar_desconto(self, percentual):
        self.preco -= self.preco * (percentual / 100)
# Instanciando e testando o objeto
p1 = Produto ("Notebook", 3500.00)
p1.exibir_produto()
p1.aplicar_desconto(10) # Aplica 10% de desconto
p1.exibir_produto() 

    