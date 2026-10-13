import tkinter as tk
from tkinter import ttk

class TelaOrigem(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controlle = controller
        # Elementos da interface
        ttk.Label(self, text="Valor:").pack(pady=5)
        self.ent_val = ttk.Entry(self)
        self.ent_val.insert(0, "250")
        self.ent_val.pack(pady=5)
        btn = ttk.Button(self, text="Enviar", command=self.enviar)
        btn.pack(pady=10)
    def enviar(self):
        val = self.ent_val.get()
        self.controller.navegar("Destino", val)
class TelaDestino(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.lbl = ttk.Label(self, text="")
        self.lbl.pack(pady=20)
    def receber_dados(self, valor):
        self.lbl.config(text=f"Recebido: R$ {valor}")
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Duas Telas")
        self.geometry("300x200")
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.telas = {}
        self.telas ["Origem"] = TelaOrigem(container, self)
        self.telas["Destino"] = TelaDestino(container, self)
        for tela in self.telas.values():
            tela.grid(row=0, column=0, sticky="nsew")
        self.navegar("Origem")
    def navegar(self, nome_tela, dado=None):
        tela = self.telas [nome_tela]
        if hasattr(tela, 'receber_dados') and dado is not None:
            tela.receber_dados(dado)
        tela.tkaise()
app=App()
app.mainloop()

    
