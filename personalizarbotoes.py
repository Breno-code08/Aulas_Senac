import tkinter as tk

# Janela principal
janela = tk.Tk()
janela.title("Botão Personalizado")
janela.geometry("300x200")
janela.configure(bg="#fdfbfb")

# Criando um botão personalizado
btn = tk.Button(
janela,
text="Clique Aqui",
bg="#0647D1", # Cor de fundo (azul)
fg="#EAE9F3", # Cor do texto (branco)
activebackground="#1CB44F", # Cor de fundo quando o botão é pressionado
activeforeground="#000000", # Cor do texto quando o botão é pressionado
font=('Arial', 12, 'bold'), # Fonte do texto
)
btn.pack(pady=30)

janela.mainloop

