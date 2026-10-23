"""Aplicação Tkinter com um botão de reprodução."""

import tkinter as tk


class App(tk.Tk):
    """Janela principal concreta da aplicação."""

    def __init__(self):
        super().__init__()
        self.icone_tk = self.criar_icone()
        self.btn = self.criar_botao()

    def criar_icone(self):
        """Cria o ícone de reprodução usando recursos nativos do Tkinter."""
        largura = 16
        altura = 16
        pixels = ["255 255 255"] * (largura * altura)
        for y in range(2, 14):
            tamanho = y - 2
            inicio = 3 + tamanho // 2
            fim = inicio + (13 - y) // 2
            for x in range(inicio, fim + 1):
                pixels[y * largura + x] = "32 160 64"

        ppm = f"P3 {largura} {altura} 255 " + " ".join(pixels)
        return tk.PhotoImage(master=self, data=ppm, format="PPM")

    def criar_botao(self):
        """Cria e posiciona o botão com texto e ícone."""
        botao = tk.Button(self, text=" Play", image=self.icone_tk,
                          compound="left", command=self.reproduzir)
        botao.image = self.icone_tk
        botao.pack(pady=80)
        return botao

    def reproduzir(self):
        """Alterna o texto do botão para indicar seu estado atual."""
        novo_texto = " Pausando" if self.btn["text"] == " Play" else " Play"
        self.btn.config(text=novo_texto)


if __name__ == "__main__":
    app = App()
    app.geometry("350x250")
    app.resizable(False, False)
    app.mainloop()