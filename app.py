from model import user, vaga, extra

from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for
)

import json

app = Flask(__name__, template_folder='view')
app.secret_key = 'secretkey'

# Condere se existe uma sessão atualmente com um usuario válido, para prevenir que uma pessoa aleatoria entre diretamente no meio do sistema
@app.before_request
def before_request():
    if 'username' in session:
        usuario = user.Usuario.achaUsuario(session['username'])
        g.usuario = usuario

# Redireciona para tela de login
@app.route('/')
def initial():
    return redirect(url_for('login', tipo='ignore', mensagem='ignore'))

# Tela de login
@app.route('/login/<tipo>/<mensagem>', methods=['GET', 'POST'])
def login(tipo, mensagem):
    if request.method == 'POST': # Espera o usuário enviar dados
        session.pop('username', None)

        formulario = request.form.to_dict()
        username = formulario['username'] 
        password = formulario['password']

         # Verifica se usuario e senha concedem entrada
        if  user.Usuario.verifyUsernamePassword(username, password):
            session['username'] = username
             # Redireciona para pagina principal
             # tipo se relaciona a mensagem que podem ser mostradas na tela de menu
             # mensagem é a mensagem em si
            return redirect(url_for('menu', tipo='ignore', mensagem='ignore'))
        
        # Retorna para própria tela com mensagem de erro
        return render_template('login.html', tipo='negativo', mensagem='Senha e/ou usuario incorretos')
    
    # Renderiza a pagina inicialmente
    return render_template('login.html', tipo=tipo, mensagem=mensagem)

# Tela de menu
@app.route('/menu/<tipo>/<mensagem>', methods=['GET'])
def menu(tipo, mensagem):
    session.get('username')
    username = session['username']
    return render_template('menu.html', tipo = tipo, mensagem = mensagem )

# Tela de inserção de localização e distancia de pesquisa
@app.route('/localizador')
def localizador():
    return render_template('localizador.html')

# Tela que apressenta os estacionamentos que estão dentro dos limites
@app.route('/mostraEstacionamentos')
def mostraEstacionamentos():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    radius = request.args.get('radius')

    if latitude is None or longitude is None:
        # Da erro caso não sejam fornecidos lat ou long
        return jsonify({'error': 'Localização inválida'})

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)

    # Filtra vagas disponíveis em base de sua distancia
    nearby_spots = vaga.Vaga.achaVagasProximas(latitude, longitude, radius)
    spots_json = json.dumps([spot.__dict__ for spot in nearby_spots])

    return render_template('mostraEstacionamentos.html', spots=spots_json, latitude = latitude,longitude = longitude, vagas=nearby_spots)

# Tela para inserir dados especificos do aluguel
@app.route('/alugar', methods = ['GET', 'POST'])
def alugar():
    vagaId = request.args.get('vaga')
    essaVaga = vaga.Vaga.achaVaga(vagaId)
    if request.method == 'POST':
        formulario = request.form.to_dict()
        inicio = formulario['dataEntrada']
        final = formulario['dataSaida']

        return redirect(url_for('pagamento', entrada = inicio, saida = final, vagaId = vagaId))
    return render_template('alugar.html', vaga = essaVaga)


@app.route('/pagamento/<entrada>/<saida>/<vagaId>', methods = ['GET', 'POST'])
def pagamento(entrada, saida, vagaId):
    essaVaga = vaga.Vaga.achaVaga(vagaId)
    precoTotal = vaga.Vaga.calculaPrecoTotal(essaVaga.preço, entrada, saida)
    posPagamento = float(g.usuario.creditos) - precoTotal
    if posPagamento <= 0:
        return redirect(url_for('menu', tipo='negativo', mensagem = 'Voce não possui creditos suficientes para realizar a reserva, por favor recarregue antes de proceder'))
    if request.method == 'POST':
        email = user.Usuario.achaUsuario(essaVaga.locador).email
        mensagem = 'Sua vaga de estacionamento ' + str(essaVaga.nome) + ' foi reservada pelo periodo de tempo \n    Inicio: ' + entrada + '\n    Saida: ' + saida
        extra.Biblioteca.enviaAviso(email, 'Vaga '+essaVaga.nome +' Alugada', mensagem)
        vaga.Vaga.registraAluga(essaVaga, entrada, saida, session['username'])
        if user.Usuario.realizaPagamento(precoTotal, (g.usuario.username), essaVaga.locador):
            return redirect(url_for('menu', tipo='positivo', mensagem = 'Reserva de vaga realizado com sucesso!!'))                
        else:
            return redirect(url_for('menu', tipo='negativo', mensagem = 'Voce não possui creditos suficientes para realizar a reserva, por favor recarregue antes de proceder'))
    return render_template('pagamento.html', precoTotal = precoTotal, posPagamento = posPagamento)


# Recebe id de uma vaga e retira a reserva existente dela
@app.route('/liberarVaga', methods=['POST'])
def liberarVaga():
    vaga_id = request.form['vaga_id']
    vaga.Vaga.liberaVaga(vaga_id)
    return redirect(url_for('avaliarVaga', vaga_id=vaga_id))

# Tela de avalição de vaga em que foi feiot o chekcout
@app.route('/avaliarVaga/<vaga_id>', methods=['GET', 'POST'])
def avaliarVaga(vaga_id):
    if request.method == 'POST':
        formulario = request.form.to_dict()
        nota = formulario['nota']
        comentario = formulario['comentario']
        usuario = session['username']

        vaga.Vaga.Avaliação.avaliarVaga(vaga_id, nota, usuario, comentario)
        return redirect(url_for('menu', tipo='positivo', mensagem='Avaliação realizada com sucesso!'))

    return render_template('avaliar.html', vaga_id=vaga_id)

# Tela que apresenta vagas alugadas pelo usuario e permite checkout dessas
@app.route('/checkout')
def checkout():
    vagas = vaga.Vaga.minhasReservas(g.usuario.username)
    return render_template('checkout.html',mVagas = vagas)

# Tela com formulario de criação de uma nova vaga pelo locador
@app.route('/novaVaga', methods=['GET', 'POST'])
def novaVaga():
    if request.method == 'POST':
        
        formulario = request.form.to_dict()
        nomeVaga = formulario['nome']
        endereco = formulario['endereco']
        preco = formulario['preco']
        tipoVaga = formulario['tipo']
        latitude = formulario['lat']
        longitude = formulario['long']
        referencia = formulario['referencia']
        adicionais = formulario['adicionais']
        
        vaga.Vaga.novaVaga.criaPossivelVaga(session['username'], nomeVaga, endereco, preco, tipoVaga,latitude,longitude, referencia, adicionais)

        return redirect(url_for('menu', tipo = 'positivo', mensagem = 'Nova vaga criada com sucesso!!'))
    return render_template('novaVaga.html')

# Tela que mostra vags pertencentes ao locador
@app.route('/minhasVagas', methods=['GET'])
def minhasVagas():
    vagas = vaga.Vaga.minhasVagas(session['username'])
    return render_template('mostraMinhasVagas.html', mVagas = vagas)

# Tela para inserir uma nova latitude e longitude de uma nova vaga
@app.route('/localNovaVaga')
def resgistre():
    return render_template('localNovaVaga.html')

@app.route('/novoUsuario', methods=['GET', 'POST'])
def novoUsuario():
    if request.method == 'POST': #espera o usuário enviar dados
        formulario = request.form.to_dict()
        email = formulario['email']
        nome = formulario['nome']
        username = formulario['username']
        senha = formulario['password']
        re_senha = formulario['repassword']

        novoUsername = user.Usuario.validateNewUser(username)
        senhasIguais = user.Usuario.validatePassword(senha, re_senha)

        if novoUsername and senhasIguais:
            user.Usuario.createNewUser(username, senha, email, nome)
            return redirect(url_for('login', tipo = 'positivo', mensagem = 'Usuario criado com sucesso!!'))
        else:
            return render_template('novoUsuario.html',
                                errorUsermaneExists = not novoUsername,
                                errorPassowrdsDontMatch = not senhasIguais)
    return render_template('novoUsuario.html')

# Tela para admin aceitar o rejeitar novas vagas
@app.route('/mostraConfirmaVagas', methods=['GET', 'POST'])
def confirmaVagas():
    if request.method == 'POST':
        id = request.form['vagaID']
        opcao = request.form['opcao']
        if opcao == 'rejeita':
            vaga.Vaga.novaVaga.removeNovaVaga(id)
        if opcao == 'aceita':
            vaga.Vaga.novaVaga.adicionaNovaVaga(id)
            vaga.Vaga.novaVaga.removeNovaVaga(id)
            
    cVagas = vaga.Vaga.novaVaga.novasVagas()
    return render_template('mostraConfirmaVagas.html', confirmVagas = cVagas)

# Tela para admin pesquisar vagas e visualizar histórico de avaliações dessas
@app.route('/analisaVagas', methods = ['GET', 'POST'])
def analisaVagas():
    if request.method == 'POST':
        formulario  = request.form.to_dict()
        if formulario['qualFormulario'] == 'form1':
            if formulario['tipoPesquisa'] == 'vagaId':
                pesquisaVagas = [vaga.Vaga.achaVaga(formulario['entrada'])]

            if formulario['tipoPesquisa'] == 'locador':
                pesquisaVagas = vaga.Vaga.pesquisaLocador(formulario['entrada'])
        
        if formulario['qualFormulario'] == 'form2':
            return redirect(url_for('mostraAvaliacoes', vaga_id = formulario['idVaga']))

        if formulario['qualFormulario'] == 'form3':
            vaga.Vaga.removeVaga(formulario['vagaAExcluir'])
            pesquisaVagas = vaga.Vaga.todasVagas()


    else:
        pesquisaVagas = vaga.Vaga.todasVagas()
    
    if ((pesquisaVagas == None) or (pesquisaVagas == [None]) or (pesquisaVagas == [])):
        pesquisaVagas = vaga.Vaga.todasVagas()
        return render_template('analisaVagas.html', erro = True, mensagem = formulario['entrada'] + ' não foi encontrado no banco de dados', pesquisaVagas = pesquisaVagas)
    return render_template('analisaVagas.html',erro = False, pesquisaVagas = pesquisaVagas)

# Tela que mostra avaliaçõees de dada vaga
@app.route('/mostraAvaliacoes/<vaga_id>')
def mostraAvaliacoes(vaga_id):
    avaliacoes = vaga.Vaga.Avaliação.mostraAvaliacoes(vaga_id)
    return render_template('mostraAvaliacoes.html', avaliacoes = avaliacoes)



