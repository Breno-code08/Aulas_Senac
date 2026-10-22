frutas = ["maçã", "Banana"]
# Adiciona novo elemento a lista.
frutas.append ("Uva")
# pop remove elemento da lista por indice ex: frutas.pop(0); Para remover por valo usamos o remove ex: frutas.remove("maçã")
frutas.pop(1)
print(f"Primeira: {frutas[0]}")
print(f"Última: {frutas[-1]}")
# Iterando sobre a lista
for f in frutas:
    print(f"item: {f}")
