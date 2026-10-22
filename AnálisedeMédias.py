n1 = float(input("Digite a 1° nota: "))
n2 = float(input("Digite a 2° nota: "))
n3 = float(input("Digite a 3° nota: "))

media = (n1+n2+n3) / 3

if media <7: print (f"Sua media foi {media:.1f} você não passou!")
if media >= 7: print (f"Sua media foi {media:.1f} você passou!")