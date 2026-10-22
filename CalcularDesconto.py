valor = int (input("Digite o valor do produto: "))
def calcular_desconto (preco, pct=0.1):
    valor_desconto = preco * pct
    preco_final = preco - valor_desconto
    return preco_final
resultado = calcular_desconto (valor)
print(f"Valor: R${resultado:.2f}")
