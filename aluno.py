class Aluno:
    def __int__(self, nome):
        self.nome = nome
        self.livros_emprestado = []

    def pegar_livro(self, livro):
        self.livros_emprestados.append(livro)

    def devolver_livro(self, livro):
        if livro in self.livros_emprestados:
         self.livros_emprestados.remove(livro)
    def listar_livros(self):
        if not self.livros_emprestados:
            print(f"{self.nome} nao possui livros emprestados.")
            return
        print(f"Livros emprestados por {self.nome}:")
        for livro in self.livros_emprestados:
            print(f"-{livro.titulo} ({livro.autor})")