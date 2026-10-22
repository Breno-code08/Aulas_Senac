import tkinter as tk
# Funções para alternar entre telas
def mostrar_tela2():
    frame_tela1.pack_forget() # Esconde a tela 1
    frame_tela3.pack_forget() # Esconde a tela 3
    frame_tela2.pack(fill="both", expand=True) # Exibe a Tela 2
def mostrar_tela1():
    frame_tela2.pack_forget() #Esconde a tela 2
    frame_tela3.pack_forget() # Esconde a tela 3
    frame_tela1.pack(fill="both", expand=True) # Exibe a Tela 1
def mostrar_tela3():
    frame_tela2.pack_forget() #Esconde a tela 2
    frame_tela1.pack_forget()
    frame_tela3.pack(fill="both", expand=True) # Exibe a Tela 3
#Configuração da Janela Principal
app = tk.Tk(); app.title("Aplicação Multi-Telas"); app.geometry("300x200")
# ---TELA 1---
frame_tela1 = tk.Frame(app)
tk.Label(frame_tela1, text="TELA 1°", font=("Arial", 14)).pack (pady=30)
tk.Button(frame_tela1, text="Ir para Tela 2", command=mostrar_tela2).place(x= 10, y= 50)
tk.Button(frame_tela1, text="Ir para Tela 3", command=mostrar_tela3).place(x= 10, y= 80)
# ---TELA 2---
frame_tela2 = tk.Frame(app)
tk.Label(frame_tela2, text="TELA 2°", font=("Arial", 14)).pack (pady=30)
tk.Button(frame_tela2, text="Ir para Tela 1", command=mostrar_tela1).place(x= 20, y= 300)
tk.Button(frame_tela2, text="Ir para Tela 3", command=mostrar_tela3).place(x= 20, y= 330)
# ---TELA 3---
frame_tela3 = tk.Frame(app)
tk.Label(frame_tela3, text="TELA 3°", font=("Arial", 14)).pack (pady=30)
tk.Button(frame_tela3, text="Ir para Tela 1", command=mostrar_tela1).place(x= 200, y= 325)
tk.Button(frame_tela3, text="Ir para Tela 2", command=mostrar_tela2).place(x= 200, y= 300)
# Inicia a aplicação na Tela 1
frame_tela1.pack(fill="both", expand=True); app.mainloop()
