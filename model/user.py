from model import extra
import csv

# usuario row 0
# password row 1
# grupo row 2
# email row 3
# nome row 4
# creditos row 5

# Classe que remete a um usuario do sistema e ações realizadas por ou sobre esse
class Usuario:
    def __init__(self, username, password, grupo, email, nome, creditos):
        self.username = username
        self.password = password
        self.grupo = grupo #grupo do usuario que decide quanto do sistema ele tem acesso
        self.email = email
        self.nome = nome #nome real do usuario
        self.creditos = creditos #monetario utilizado internamente

    def __repr__(self):
        return f'<User: {self.username}>'
    
    # Verifica se usuario existe, caso exista checa se a senha fornecida é correta
    def verifyUsernamePassword(username, password):
        with open ('banco_usuarios.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[0] == username:
                    if row[1] == password:
                        return True
                    else:
                        return False
    
    # Procura o usuaro dentro do banco de dados e retorna o grupo do qual ele faz parte
    def getGroup(username):
        with open ('banco_usuarios.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[0] == username:
                    return row[2]
                
    # Valida o nome de usuario, considerando a premissa que dois usuarios não pdoem possuir mesmo username
    def validateNewUser(username):
        with open ('banco_usuarios.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[0] == username:
                    return False
            return True
                
    # Compara os dois campos de senha para garantir que as senhas são iguais
    def validatePassword(password, rePassword):
        if password != rePassword:
            return False
        else:
            return True
    
    # Encontra um usuario no banco_usuarios pelo seu username e retorna na forma de objeto
    def achaUsuario(username):
        with open ("banco_usuarios.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[0] == username:
                    return Usuario(row[0],row[1],row[2],row[3], row[4], row[5])
    
    # Atualiza um usuario dentro do banco_usuarios, recebendo um objeto do tipo Usuario
    def atualizaUsusario(usuario):
        banco = 'banco_usuarios.csv'
        arquivoIntermediario = 'temp.csv'
        with open(banco, 'r') as csv_file, open(arquivoIntermediario, 'w', newline='') as temp:
            csv_reader = csv.reader(csv_file, delimiter=';')
            csv_writer = csv.writer(temp, delimiter=';')
            for row in csv_reader:
                # encontra o usuario através do username e troca seus valores
                if row[0] == usuario.username:
                    row[0] = usuario.username
                    row[1] = usuario.password
                    row[2] = usuario.grupo
                    row[3] = usuario.email
                    row[4] = usuario.nome
                    row[5] = usuario.creditos
                # repassa a linha para um csv intermediario
                csv_writer.writerow(row)
        # retorna os dados para o csv de origem
        extra.Biblioteca.devolveCSV(banco, arquivoIntermediario)

    # Recebe os usernames do locatario e locador, além do valor de aluguel, e faz a transferencia de créditos entre esses
    def realizaPagamento(valor, locatarioNome, locadorNome):
        locatario = Usuario.achaUsuario(locatarioNome)
        creditos = float(locatario.creditos)
        locador = Usuario.achaUsuario(locadorNome)
        
        if creditos >= valor:
            locatario.creditos = round(creditos - valor, 2)
            Usuario.atualizaUsusario(locatario)
            locador.creditos = round(creditos + valor, 2)
            Usuario.atualizaUsusario(locador)
            return True
        else:
            return False

    # Cria um novo usuario a partir do dados passados e salva no banco de dados,
    # sendo que inicialmente usuario é cadastrado como locatario e seus créditos são 0
    def createNewUser(username, password, email, nome):
        novoUsuario = [username, password, 'locatario', email, nome, '0']
        extra.Biblioteca.escritorLihaCsv('banco_usuarios.csv', novoUsuario)
