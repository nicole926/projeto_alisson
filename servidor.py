import tornado
import sqlite3

# ------------------ CONEXÃO COM O BANCO ------------------
def conexao_db(query, valores=None):
    print(query)
    conexao = sqlite3.connect("db/db.sqlite3")
    cursor = conexao.cursor()

    if valores:
        cursor.execute(query, valores)
    else:
        cursor.execute(query)

    resultado = cursor.fetchall()
    conexao.commit()
    conexao.close()
    return resultado


# ------------------ LOGIN ------------------
class Login(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/login.html")

    def post(self):
        usuario = self.get_argument("usuario")
        senha = self.get_argument("senha")
        query = "SELECT * FROM usuario WHERE nome=? AND senha=?"
        valores = (usuario, senha)
        resultado = conexao_db(query, valores)
        if resultado:
            self.render("templates/index.html")
        else:
            self.write("Usuário ou senha não encontrados.")


# ------------------ LISTAR / ADICIONAR CLIENTES ------------------
class Clientes(tornado.web.RequestHandler):

    def get(self):
        query = "SELECT * FROM cliente"
        resultados = conexao_db(query)
        self.render("templates/listar_clientes.html", clientes=resultados)

    def post(self):
        # adicionar cliente
        nome = self.get_argument("nome")
        telefone = self.get_argument("telefone")
        email = self.get_argument("email")

        query = "INSERT INTO cliente (nome, telefone, email) VALUES (?, ?, ?)"
        valores = (nome, telefone, email)
        conexao_db(query, valores)

        self.redirect("/listar_clientes")


# ------------------ EDITAR CLIENTE ------------------
class EditarCliente(tornado.web.RequestHandler):
    def post(self):
        id_cliente = self.get_argument("id")
        nome = self.get_argument("nome")
        telefone = self.get_argument("telefone")
        email = self.get_argument("email")

        query = """
            UPDATE cliente
            SET nome=?, telefone=?, email=?
            WHERE id=?
        """
        valores = (nome, telefone, email, id_cliente)
        conexao_db(query, valores)

        self.redirect("/listar_clientes")


# ------------------ DELETAR CLIENTE ------------------
class DeletarCliente(tornado.web.RequestHandler):
    def post(self):
        id_cliente = self.get_argument("id")

        query = "DELETE FROM cliente WHERE id=?"
        valores = (id_cliente,)
        conexao_db(query, valores)

        self.redirect("/listar_clientes")


# ------------------ ROTAS ------------------
app = tornado.web.Application([
    (r"/", Login),
    (r"/listar_clientes", Clientes),
    (r"/editar_cliente", EditarCliente),
    (r"/deletar_cliente", DeletarCliente),
])


# ------------------ INICIAR SERVIDOR ------------------
if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
