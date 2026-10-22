from conta import Conta
from contacorrente import ContaCorrente
from contapoupanca import ContaPoupanca

c1= ContaCorrente("Breno", 10, 1000)
c1.exibir_saldo()

c2= ContaPoupanca("Breno", 100, 0.1)
c2.exibir_juros()