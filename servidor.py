import tornado
import sqlite3

def conexao_db(query,valores):
        print(query)
        conexao = sqlite3.connect("db/db.sqlite3")
        cursor= conexao.cursor()
        try:
            if valores:
                cursor.execute(query,valores)
            else:
                cursor.execute(query)
            resultado = cursor.fetchall()
            conexao.commit()
        except Exception:
                raise
        conexao.close()
        return resultado

class Login(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/login.html")

    def post(self):
        usuario = self.get_argument("usuario")
        senha = self.get_argument("senha")
        query = "SELECT * FROM usuario WHERE nome=? AND senha=?"
        valores = (usuario,senha)
        resultado = conexao_db(query,valores)
        if resultado:
            self.render("templates/index.html")
        else:
            self.write("Usuário ou senha não encontrados.")


class Clientes(tornado.web.RequestHandler):

    def get(self):
        query = "select * from cliente"
        valores = None
        resultados = conexao_db(query,valores)
        self.render("templates/listar_clientes.html",clientes=resultados)

# cria as rotas
app = tornado.web.Application([
         (r"/", Login),
         (r"/listar_clientes", Clientes),
         ])

if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()