import tkinter as tk
from tkinter import messagebox
from banco import salvar_nome

def cadastrar():
    nome = entry_nome.get().strip()

    if not nome:
        messagebox.showwarning("Aviso"," Por favor, digite um nome!")
        return

    try:
        salvar_nome(nome)
        messagebox.showinfo("Sucesso", "Nome salvo com sucesso!")
        entry_nome.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar no banco: {e}")

janela = tk.Tk()
janela.title("Cadastro Simples")
janela.geometry ("300x180")

label_instrucao = tk.Label(janela, text="Digite o nome:")
label_instrucao.pack(pady=(25, 5))

entry_nome = tk.Entry(janela, width=28)
entry_nome.pack(pady=5)

btn_salvar = tk.Button(janela, text="Salvar", width=12, command=cadastrar)
btn_salvar.pack(pady=20)

janela.mainloop()