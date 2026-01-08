import os
import sqlite3
import tornado.ioloop
import tornado.web


# ------------------ CONEXÃO COM O BANCO ------------------
def conexao_db(query, valores=None):
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
        self.render("login.html")

    def post(self):
        usuario = self.get_argument("usuario")
        senha = self.get_argument("senha")

        query = "SELECT * FROM usuarios WHERE usuario=? AND senha=?"
        resultado = conexao_db(query, (usuario, senha))

        if resultado:
            self.redirect("/index")
        else:
            self.write("Usuário ou senha inválidos")


# ------------------ INDEX ------------------
class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


# ------------------ CLIENTES ------------------
class Clientes(tornado.web.RequestHandler):
    def get(self):
        query = "SELECT id, nome, telefone, email FROM contatos"
        clientes = conexao_db(query)
        self.render("listar_cliente.html", clientes=clientes)

    def post(self):
        nome = self.get_argument("nome")
        telefone = self.get_argument("telefone")
        email = self.get_argument("email")

        query = "INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)"
        conexao_db(query, (nome, telefone, email))

        self.redirect("/listar_cliente")


# ------------------ EDITAR CLIENTE ------------------
class EditarCliente(tornado.web.RequestHandler):
    def post(self):
        id_cliente = self.get_argument("id")
        nome = self.get_argument("nome")
        telefone = self.get_argument("telefone")
        email = self.get_argument("email")

        query = """
            UPDATE contatos
            SET nome=?, telefone=?, email=?
            WHERE id=?
        """
        conexao_db(query, (nome, telefone, email, id_cliente))

        self.redirect("/listar_cliente")


# ------------------ DELETAR CLIENTE ------------------
class DeletarCliente(tornado.web.RequestHandler):
    def post(self):
        id_cliente = self.get_argument("id")

        query = "DELETE FROM contatos WHERE id=?"
        conexao_db(query, (id_cliente,))

        self.redirect("/listar_cliente")


# ------------------ HISTÓRICO ------------------
class Historico(tornado.web.RequestHandler):
    def get(self):
        query = "SELECT id, tabela, operacao, data_hora, descricao FROM logs ORDER BY data_hora DESC"
        logs = conexao_db(query)
        self.render("logs.html", logs=logs)

# ------------------ CLIENTES (VIEW COMPLETA) ------------------
class ClientesView(tornado.web.RequestHandler):
    def get(self):
        query = """
        SELECT
            cliente_id,
            nome,
            email,
            telefone,
            status,
            rua,
            cidade,
            estado
        FROM vw_clientes_completos
        """
        clientes = conexao_db(query)
        self.render("clientes_view.html", clientes=clientes)


# ------------------ APLICAÇÃO ------------------

app = tornado.web.Application(
    [
        (r"/", Login),
        (r"/index/?", Index),
        (r"/listar_cliente/?", Clientes),
        (r"/editar_cliente/?", EditarCliente),
        (r"/deletar_cliente/?", DeletarCliente),
        (r"/historico/?", Historico),
        (r"/clientes_view/?", ClientesView),

    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=True
)

# ------------------ SERVIDOR ------------------
if __name__ == "__main__":
    app.listen(8888)
    print("Servidor rodando em http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()