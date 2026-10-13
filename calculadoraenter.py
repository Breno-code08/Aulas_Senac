import tkinter as tk

# Função para calcular a soma
def somar (event=None):
    try:
        n1 = float(entry1.get())
        n2 = float(entry2.get())
        lbl_res.config(text=f"Resultado: {n1 + n2}")
    except ValueError:
        lbl_res.config(text="Por favor, insira números válidos.")

#Configuração da Janela Principal
app = tk.Tk()
app.title("Calculadora de Soma")
app.geometry("300x200")
#Criação dos Widgets
entry1 = tk.Entry( app); entry1.pack( pady=5)
entry2 = tk.Entry(app); entry2.pack(pady=5)
btn = tk.Button(app, text="+", command=somar); btn.place(x=100, y=150) 
lbl_res = tk.Label(app, text="Resultado: "); lbl_res.pack(pady=10)

app.bind('<Return>', somar)

app.mainloop()