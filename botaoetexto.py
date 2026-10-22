import tkinter as tk

janela = tk.Tk()
janela.title("Janela")
janela.geometry("400x300")


label = tk.Label (janela, text = "Olá, Mundo!", bg = "#000103", fg = "#DEE2E9")
label.pack (pady = 30)

tk.Button (janela, text= "Clique aqui", command=None).pack(pady=50)

janela.mainloop()