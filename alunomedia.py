# Solução em Python
class Aluno:
    def __init__(self, nome, n1, n2):
         self.nome = nome
         self.n1 = n1
         self.n2 = n2
    def media(self):  
        self.calculo_media = (self.n1 + self.n2) /2
# Testando a classe
    def aprovacao(self):
        if self.calculo_media >= 7 : print("Você foi aprovado")
        else : print("Reprovado")
m1 = Aluno ("Breno", 5, 7)
m1.media ()
m1.aprovacao ()