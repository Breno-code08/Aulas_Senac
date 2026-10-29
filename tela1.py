import tkinter as tk
from tkinter import ttk, messagebox
from banco import salvar_nome, listar_nome, excluir_nome

def mostrar_tela2():
    frame_tela1.pack_forget() # Esconde a tela 1
    frame_tela2.pack(fill="both", expand=True) # Exibe a Tela 2
def mostrar_tela1():
    frame_tela2.pack_forget() #Esconde a tela 2
    frame_tela1.pack(fill="both", expand=True) # Exibe a Tela 1

janela= tk.Tk(); janela.title("Cadastro Simples"); janela.geometry("450x570")
# ---TELA 1---
frame_tela1 = tk.Frame(janela)
tk.Label(frame_tela1, text="TELA 1°", font=("Arial", 14)).pack (pady=30)
tk.Button(frame_tela1, text="Ir para Tela 2", command=mostrar_tela2).pack()
# ---TELA 2---
frame_tela2 = tk.Frame(janela)
tk.Label(frame_tela2, text="TELA 2°", font=("Arial", 14)).pack (pady=30)
tk.Button(frame_tela2, text="Ir para Tela 1", command=mostrar_tela1).pack()

frame_tela1.pack(fill="both", expand=True)  # Exibe a tela inicial


def cadastrar():
    nome = entry_nome.get().strip()
    telefone = entry_telefone.get().strip()

    if not nome or not telefone:
        messagebox.showwarning("Aviso", "Por favor, preencha o nome e o telefone!")
        return

    if not telefone.isdigit():
        messagebox.showwarning("Aviso", "O telefone deve conter apenas números!")
        return
    try:
        salvar_nome(nome, telefone)
        messagebox.showinfo("Sucesso", "Registro salvo com sucesso!")
        entry_nome.delete(0, tk.END)
        entry_telefone.delete(0, tk.END)
        atualizar_tabela()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar no banco: {e}")

def excluir():
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um registro na tabela para excluir!")
        return
    
    item = tree.item(selecionado)
    registro_id = item["values"] [0]
    registro_nome = item["values"] [1]

    if messagebox.askyesno("Confirmar", f"Deseja realmente excluir '{registro_nome}' (ID: {registro_id})?"):
        try:
            excluir_nome(registro_id)
            messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
            atualizar_tabela()
        except Exception as e:
            messagebox("Erro", f"Erro ao excluir: {e}")

def pesquisar():
    termo = entry_pesquisa.get().strip()
    atualizar_tabela(termo)

def limpar_pesquisa():
    entry_pesquisa.delete(0, tk.END)
    atualizar_tabela()

def atualizar_tabela(pesquisa=""):
    for item in tree.get_children():
        tree.delete(item)
    registros = listar_nome(pesquisa)
    for reg in registros:
        tree.insert("", tk.END,values=(reg.id, reg.nome, reg.telefone))    

label_instrucao = tk.Label(frame_tela2, text="Digite o nome:")
label_instrucao.pack(pady=(25, 5))

entry_nome = tk.Entry(frame_tela2, width=28)
entry_nome.pack(pady=5)

label_telefone = tk.Label(frame_tela2, text="Digite o telefone:")
label_telefone.pack(pady=2)

entry_telefone = tk.Entry(frame_tela2, width=30)
entry_telefone.pack(pady=2)

btn_salvar = tk.Button(frame_tela2, text="Salvar", width=12, command=cadastrar)
btn_salvar.pack(pady=20)

frame_pesquisa = tk.Frame(frame_tela2)
frame_pesquisa.pack(pady=10)

entry_pesquisa = tk.Entry(frame_pesquisa, width=20)
entry_pesquisa.pack(side="left", padx=2)

btn_todos = tk.Button(frame_pesquisa, text="Pesquisar", command=pesquisar)
btn_todos.pack(side="left", padx=2)

colunas = ("id", "nome", "telefone")
tree = ttk.Treeview(frame_tela2, columns=colunas, show="headings", height=8)
tree.heading("id", text="ID")
tree.heading("nome", text="Nome")
tree.heading("telefone", text="Telefone")
tree.column("id", width=40, anchor="center")
tree.column("nome", width=200)
tree.column("telefone", width=120, anchor="center")
tree.pack(padx=20, pady=5, fill="both", expand=True)

btn_excluir = tk.Button(frame_tela2, text="Excluir Selecionado", bg="#ffcccc", command=excluir)
btn_excluir.pack(pady=10)

try:
    atualizar_tabela()
except Exception as e:
    print(f"Erro ao carregar dados: {e}")

janela.mainloop