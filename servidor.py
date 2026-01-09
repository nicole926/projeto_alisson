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


# ------------------ CLIENTES (LISTAGEM + CADASTRO) ------------------
class Clientes(tornado.web.RequestHandler):
    def get(self):
        busca = self.get_argument("busca", "")

        query = """
            SELECT
                c.id,
                c.nome,
                c.telefone,
                c.email,
                c.status_id,
                e.rua,
                e.cidade,
                e.estado
            FROM contatos c
            LEFT JOIN enderecos e ON c.id = e.contato_id
        """

        valores = []

        if busca:
            query += " WHERE c.nome LIKE ?"
            valores.append(f"%{busca}%")

        clientes = conexao_db(query, valores)

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


# ------------------ EDITAR CLIENTE (INLINE) ------------------
class EditarCliente(tornado.web.RequestHandler):
    def post(self):
        id_cliente = self.get_argument("id")
        nome = self.get_argument("nome")
        telefone = self.get_argument("telefone")
        email = self.get_argument("email")
        status_id = self.get_argument("status_id")
        rua = self.get_argument("rua")
        cidade = self.get_argument("cidade")
        estado = self.get_argument("estado")

        # Atualiza contato
        conexao_db("""
            UPDATE contatos
            SET nome=?, telefone=?, email=?, status_id=?
            WHERE id=?
        """, (nome, telefone, email, status_id, id_cliente))

        # Atualiza endereço
        conexao_db("""
            UPDATE enderecos
            SET rua=?, cidade=?, estado=?
            WHERE contato_id=?
        """, (rua, cidade, estado, id_cliente))

        self.redirect("/listar_cliente")


# ------------------ CLIENTES COMPLETOS ------------------
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


# ------------------ DELETAR CLIENTE ------------------
class DeletarCliente(tornado.web.RequestHandler):
    def post(self):
        id_cliente = self.get_argument("id")

        conexao_db("DELETE FROM contatos WHERE id=?", (id_cliente,))

        self.redirect("/listar_cliente")


# ------------------ HISTÓRICO ------------------
class Historico(tornado.web.RequestHandler):
    def get(self):
        query = """
            SELECT id, tabela, operacao, data_hora, descricao
            FROM logs
            ORDER BY data_hora DESC
        """
        logs_brutos = conexao_db(query)

        logs = []
        for id, tabela, operacao, data_hora, descricao in logs_brutos:
            logs.append((
                id,
                tabela,
                operacao,
                operacao.lower(),  # 👈 cria versão minúscula
                data_hora,
                descricao
            ))

        self.render("logs.html", logs=logs)

# ------------------ APLICAÇÃO ------------------
def make_app():
    return tornado.web.Application(
        [
            (r"/", Login),
            (r"/index/?", Index),
            (r"/listar_cliente/?", Clientes),
            (r"/editar_cliente/?", EditarCliente),
            (r"/deletar_cliente/?", DeletarCliente),
            (r"/clientes_completos/?", ClientesCompletos),
            (r"/historico/?", Historico),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )


# ------------------ SERVIDOR ------------------
if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Servidor rodando em http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
