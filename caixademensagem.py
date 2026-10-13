import tkinter as tk
from tkinter import messagebox

app = tk.Tk()
app.title("Exemplo Messagebox")
app.geometry("250x100")

def mostrar_mensagem():
    messagebox.askquestion("Aviso", "Opração Realizada!")

btn = tk.Button(app, text="Clique Aqui", command=mostrar_mensagem)
btn.pack(pady=20)

app.mainloop()