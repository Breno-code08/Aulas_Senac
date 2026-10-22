# Entrada de dados
opcao = int(input("Escolha 1 opção : [1] [2] [3]"))
# Estrutura mach
match opcao:
    case 1:
     print("Iniciando o jogo...")
    case 2:
     print("Carregando configurações")
    case 3: 
     print("Saindo do programa. Até logo!")
    case _:
     print ("Opção invalida")