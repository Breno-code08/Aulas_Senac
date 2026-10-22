class Biblioteca:
    def __int__(self): 
        self.livros=[]    
    def cadastra_livro(self, livro):
        self.livros.append (livro)
        print (f"livro '{livro.titulo}' cadastro com sucesso!")
    def listar_livros(self): 
        print("\n ---LIVROS DA BIBLIOTECA---")
        if not self.livros: 
            print("nenhum livro cadastrado.")
            return
    
    for livro in self.livros: 
        print (livro)
    def emprestar_livro(self, livro, aluno):
        if livro not in self.livros:
            print ("Livro não cadastrado na biblioteca.")
            return 
        if not livro.disponivel: 
            print ("Este livro já esta emprestado.")   
            return         

        livro.disponivel = False 
        aluno.adicionar_livro(livro)

        print(f"livro '{livro.titulo}'empresta para{aluno.nome}")
    def devolver_livro(self, livro, aluno):
        if livro not in aluno.livros_emprestados:
            print ("Este aluno não possui esse livro emprestado")


