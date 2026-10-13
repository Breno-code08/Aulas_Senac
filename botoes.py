# Carrega bibliotecas necessárias
import tkinter as tk
from PIL import ImageTk, Image

# Janela Principal
app = tk.Tk()
app.geometry("350x250")

#1. Carrega e redimensiona o icone
img_pil = Image.open("images.jpg")
img_pil = img_pil.resize((300,200))

#2. Converte para o Tkinter
icone_tk = ImageTk.PhotoImage(img_pil)

#3. Cria o botão com Texto e ícone
btn = tk.Button(app, text=" Play",
image=icone_tk,
compound="left")

# Evita Garbage Collection
btn.image = icone_tk
btn.pack(pady=80)

app.mainloop()