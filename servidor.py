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
        busca = self.get_argument("busca", "")

        if busca:
            query = """
                SELECT id, nome, telefone, email
                FROM contatos
                WHERE nome LIKE ?
                   OR telefone LIKE ?
                   OR email LIKE ?
            """
            clientes = conexao_db(
                query,
                (f"%{busca}%", f"%{busca}%", f"%{busca}%")
            )
        else:
            query = "SELECT id, nome, telefone, email FROM contatos"
            clientes = conexao_db(query)

        self.render(
            "listar_cliente.html",
            clientes=clientes,
            busca=busca
        )

    def post(self):
        nome = self.get_argument("nome")
        telefone = self.get_argument("telefone")
        email = self.get_argument("email")
        status_id = self.get_argument("status_id")
        rua = self.get_argument("rua")
        cidade = self.get_argument("cidade")
        estado = self.get_argument("estado")

        conexao = sqlite3.connect("db/db.sqlite3")
        cursor = conexao.cursor()

        # INSERE CONTATO
        cursor.execute("""
            INSERT INTO contatos (nome, telefone, email, status_id)
            VALUES (?, ?, ?, ?)
        """, (nome, telefone, email, status_id))

        contato_id = cursor.lastrowid

        # INSERE ENDEREÇO
        cursor.execute("""
            INSERT INTO enderecos (contato_id, rua, cidade, estado)
            VALUES (?, ?, ?, ?)
        """, (contato_id, rua, cidade, estado))

        conexao.commit()
        conexao.close()

        self.redirect("/listar_cliente")

class ClientesCompletos(tornado.web.RequestHandler):
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
        self.render("clientes_completos.html", clientes=clientes)


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

class EditarClienteCompleto(tornado.web.RequestHandler):
    def get(self, cliente_id):
        query = """
            SELECT
                c.id,
                c.nome,
                c.email,
                c.telefone,
                c.status_id,
                e.rua,
                e.cidade,
                e.estado
            FROM contatos c
            LEFT JOIN enderecos e ON c.id = e.contato_id
            WHERE c.id = ?
        """
        cliente = conexao_db(query, (cliente_id,))
        self.render("editar_cliente.html", cliente=cliente[0])

    def post(self, cliente_id):
        nome = self.get_argument("nome")
        email = self.get_argument("email")
        telefone = self.get_argument("telefone")
        status_id = self.get_argument("status")
        rua = self.get_argument("rua")
        cidade = self.get_argument("cidade")
        estado = self.get_argument("estado")

        conexao_db("""
            UPDATE contatos
            SET nome=?, email=?, telefone=?, status_id=?
            WHERE id=?
        """, (nome, email, telefone, status_id, cliente_id))

        conexao_db("""
            UPDATE enderecos
            SET rua=?, cidade=?, estado=?
            WHERE contato_id=?
        """, (rua, cidade, estado, cliente_id))

        self.redirect("/clientes_completos")



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
        (r"/clientes_completos/?", ClientesCompletos),
        (r"/editar_cliente/?", EditarCliente),
        (r"/deletar_cliente/?", DeletarCliente),
        (r"/historico/?", Historico),
        (r"/editar_cliente_completo/([0-9]+)/?", EditarClienteCompleto),
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