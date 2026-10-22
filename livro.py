class Livro:
    def __int__(self, titulo, autor):
        self.titulo = titulo
        self.autor = autor
        self.disponivel = True
    def __str__(self):
        if self.disponivel: 
            status = "Disponível"
        else:
           status = "Emprestado"
        return f"{self.titulo} - {self.autor} | {status}"