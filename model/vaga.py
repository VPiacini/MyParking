from model import extra
import csv, math, datetime

# nome row 0
# endereco row 1
# disponibilidade row 2
# preco row 3
# latitude row 4
# longitude row 5
# locador row 6
# avaliacao row 7
# tipo_vaga row 8
# ponto_de_referencia row 9
# adicional row 10
# id row 11
# numero de avaliações row 12

# Classe que remete a Vaga e ações realizada por ou sobre ela
class Vaga:
    def __init__(self, nome, endereço, disponibilidade, preço, latitude, longitude,locador, avaliacao, tipo, referencia, adicional, id,numeroAvaliacoes):
        self.nome = nome
        self.endereço = endereço
        self.disponibilidade = disponibilidade #estado em que vaga está disponivel ou indisponivel
        self.preço = preço #preço por dia de aluguel
        self.latitude = latitude
        self.longitude = longitude
        self.distancia = 0 #distancia até o usuario
        self.locador = locador #proprietario da vaga
        self.avaliacao = avaliacao #avaliação atual da vaga
        self.tipo = tipo
        self.referencia = referencia
        self.adicional = adicional
        self.id = id
        self.numeroAvaliacoes = numeroAvaliacoes

    # Filtra vagas de acordo com distancia requerida elo usuário e disponibilidade
    def achaVagasProximas(user_latitude, user_longitude, radius):
        
        # recebe vagas disponiveis do banco de dados
        parking_spots = Vaga.leBancoVagas()

        # distância máxima do usuário até a vaga em kilometros 
        MAX_RADIUS = radius/1000  

        nearby_spots = []
        for spot in parking_spots:
            spot_latitude = float(spot.latitude)
            spot_longitude = float(spot.longitude)
            spot.distancia = Vaga.calculaDistancia(user_latitude, user_longitude, spot_latitude, spot_longitude)

            if spot.distancia <= MAX_RADIUS:
                spot.distancia = round(spot.distancia, 3)
                nearby_spots.append(spot)
        return nearby_spots

    # Cria uma lista com todas vagas que estão disponiveis
    def leBancoVagas():
        vagas=[]
        with open ('banco_vagas.csv', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[2] == 'disponivel':
                    vagas.append(Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11],row[12]))
            return vagas

    # calcula a distancia entre 2 pontos ao receber suas latitudes e longitdes respectivas
    def calculaDistancia(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Calculo de distancia a partir de longitude e latidude
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        raioTerra = 6371  # Raio da Terra
        distancia = raioTerra * c

        return distancia
    
    # Cria e retorna uma lista com todas vagas no sistema
    def todasVagas():
            vagas = []
            with open ('banco_vagas.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                next(csv_reader, None)
                for row in csv_reader:
                    vagas.append(Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8], row[9], row[10], row[11], row[12]))
                csv_file.close()
                return vagas

    # Encontra uma vaga no banco_vagas com base no seu ID e retorna um objeto vaga com seus dados
    def achaVaga(vaga):
        with open('banco_vagas.csv', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[11] == vaga:
                    return Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],float(row[7]),row[8],row[9],row[10], row[11],int(row[12]))
    
    # Encontra uma vaga no banco_vagas com base no username do seu locador e retorna um objeto vaga com seus dados
    def pesquisaLocador(locador):
        vagas = []
        with open('banco_vagas.csv', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[6] == locador:
                    vagas.append(Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11],row[12]))
            return vagas

    # Encontra uma vaga no banco_vagas e exclui essa
    def removeVaga(idVaga):
            banco = 'banco_vagas.csv'
            arquivoIntermediario = 'temp.csv'
            with open(banco, 'r', encoding="utf8") as csv_file, open(arquivoIntermediario, 'w+', newline='') as temp:
                csv_reader = csv.reader(csv_file, delimiter=';')
                csv_writer = csv.writer(temp, delimiter=';')
                for row in csv_reader:
                    if row[11] != idVaga:
                        csv_writer.writerow(row)

            extra.Biblioteca.devolveCSV(banco, arquivoIntermediario)

    # Cria e retorna uma lista de todas vagas que o locatario está ocupando
    def minhasReservas(username):
        idVagasOcupadas = Vaga.Reserva.minhasReservas(username) # encontra ID das vagas reservadas pelo locatario
        vagas = []
        # encontra as vagas no banco_vagas e retorna a lista de vagas reservadas
        with open ('banco_vagas.csv', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for id in idVagasOcupadas:
                for row in csv_reader:
                    if row[11] == id:
                        vagas.append(Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
                csv_file.seek(0)
            return vagas    

    # Torna a vaga que estava sendo reservada disponivel
    def liberaVaga(vaga_id):
        vagaParaLiberar = Vaga.achaVaga(vaga_id)
        reservaParaLiberar = Vaga.Reserva.achaReserva(vaga_id)
        
        # Atualiza as informações da vaga e reserva
        reservaParaLiberar.locatario = ''
        reservaParaLiberar.entrada = 0
        reservaParaLiberar.saida = 0

        vagaParaLiberar.disponibilidade = 'disponivel'
        
        # Atualiza os arquivos CSV
        Vaga.atualizaVaga(vagaParaLiberar)
        Vaga.Reserva.atualizaReserva(reservaParaLiberar)

    # Encontra a lista de vagas pertencentes ao locador em no banco_vagas
    def minhasVagas(locador):
        vagas = []
        with open ('banco_vagas.csv', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[6] == locador:
                    vagas.append(Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11],row[12]))
            return vagas

    # Adiciona uma vaga aos bancos de dados de vagas e de reservas,
    #  sendo que a vaga tem nota inicial maxima (5) e está disponivel
    def criaNovaVaga(locatario, nome, endereco, preco, tipoVaga, lat, long, pontoRef, adicionais):
        id = Vaga.novoId()
        if adicionais == '':
            adicionais = ' '
        novaVaga = [nome, endereco, 'disponivel', preco, lat, long, locatario, '5', tipoVaga, pontoRef, adicionais, id, '0']
        novaReserva = [id, 0, 0,'']
        extra.Biblioteca.escritorLihaCsv('banco_vagas.csv', novaVaga)
        extra.Biblioteca.escritorLihaCsv('reservas.csv', novaReserva)
    
    # Cria um novo ID para uma nova vaga, sendo que é igual ao ultimo ID adicionado de 1
    def novoId():
        with open('banco_vagas.csv', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                pass
            return int(row[11])+1
    
    # Atualiza um usuario dentro do banco_usuarios, recebendo um objeto do tipo Usuario
    def atualizaVaga(vaga):
        banco = 'banco_vagas.csv'
        arquivoIntermediario = 'temp.csv'
        with open(banco, 'r', encoding="utf8") as csv_file, open(arquivoIntermediario, 'w+', newline='') as temp:
            csv_reader = csv.reader(csv_file, delimiter=';')
            csv_writer = csv.writer(temp, delimiter=';')
            for row in csv_reader:
                if row[11] == vaga.id:
                    row[0] = vaga.nome
                    row[1] = vaga.endereço
                    row[2] = vaga.disponibilidade
                    row[3] = vaga.preço
                    row[4] = vaga.latitude
                    row[5] = vaga.longitude
                    row[6] = vaga.locador
                    row[7] = vaga.avaliacao
                    row[8] = vaga.tipo
                    row[9] = vaga.referencia
                    row[10] = vaga.adicional
                    row[11] = vaga.id
                    row[12] = vaga.numeroAvaliacoes
                csv_writer.writerow(row)

        extra.Biblioteca.devolveCSV(banco, arquivoIntermediario)

    # registra nos bancos de dados o alugeul de uma vaga
    def registraAluga(fVaga, entrada, saida, locatario):
        fVaga.disponibilidade = 'indisponivel'
        Vaga.atualizaVaga(fVaga)
        aluguel = Vaga.Reserva(fVaga.id, entrada, saida, locatario)
        Vaga.Reserva.atualizaReserva(aluguel)
    
    # calcula o preço total a ser cobrado a partir de uma data de checkin e uma data de checkout
    def calculaPrecoTotal(preco, entrada, saida):
        dataEntrada = datetime.datetime.strptime(entrada, "%Y-%m-%d")
        dataSaida = datetime.datetime.strptime(saida, "%Y-%m-%d")
        dias = abs((dataSaida - dataEntrada).days)
        precoDias = float(preco)*dias
        return precoDias*1.02

    # Sub Classe de Vaga que remete a uma nova Vaga e ações realizada por ou sobre ela,
    # possui maior parte dos atributos de Vaga, sem os que são adiocionados pelo sistema
    # utilizada como intermediario entre a submissão de uma nova vaga por um locador e uma vaga definitiva
    class novaVaga:
        def __init__(self, nome, endereço, preço, longitude, latitude, locador, tipo, referencia, adicional, id):
            self.nome = nome
            self.endereço = endereço
            self.preço = preço
            self.longitude = longitude
            self.latitude = latitude
            self.locador = locador
            self.tipo = tipo
            self.referencia = referencia
            self.adicional = adicional
            self.id = id

        # adiciona uma novaVaga ao banco vagas_novas
        def criaPossivelVaga(locador, nome, endereco, preco, tipoVaga, lat, long, pontoRef, adicionais):
            if adicionais == '':
                adicionais = ' '
            novaVaga = [nome, endereco, preco, lat, long, locador, tipoVaga, pontoRef, adicionais, Vaga.novaVaga.novaVagaId()]
            extra.Biblioteca.escritorLihaCsv('vagas_novas.csv', novaVaga)

        # Retorna todas novaVaga s esperando admissão
        def novasVagas():
            vagas = []
            with open ('vagas_novas.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                next(csv_reader, None)
                next(csv_reader,None)
                for row in csv_reader:
                    vagas.append(Vaga.novaVaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8], row[9]))
                return vagas
        
        # Atualiza novaVaga no banco de dados
        def atualizaNovaVaga(vaga):
            banco = 'vagas_novas.csv'
            arquivoIntermediario = 'temp.csv'
            with open(banco, 'r', encoding="utf8") as csv_file, open(arquivoIntermediario, 'w+', newline='') as temp:
                csv_reader = csv.reader(csv_file, delimiter=';')
                csv_writer = csv.writer(temp, delimiter=';')
                for row in csv_reader:
                    if row[10] == vaga.id:
                        row[0] = vaga.nome
                        row[1] = vaga.endereço
                        row[2] = vaga.preço
                        row[3] = vaga.latitude
                        row[4] = vaga.longitude
                        row[5] = vaga.locador
                        row[6] = vaga.tipo
                        row[7] = vaga.referencia
                        row[8] = vaga.adicional
                        row[9] = vaga.id
                    csv_writer.writerow(row)
            extra.Biblioteca.devolveCSV(banco, arquivoIntermediario)

        # Remove uma novaVaga a partir do seu id
        def removeNovaVaga(idVaga):
            banco = 'vagas_novas.csv'
            arquivoIntermediario = 'temp.csv'
            with open(banco, 'r', encoding="utf8") as csv_file, open(arquivoIntermediario, 'w+', newline='') as temp:
                csv_reader = csv.reader(csv_file, delimiter=';')
                csv_writer = csv.writer(temp, delimiter=';')
                for row in csv_reader:
                    if row[9] != idVaga:
                        csv_writer.writerow(row)
            extra.Biblioteca.devolveCSV(banco, arquivoIntermediario)

        # Cria um novo ID para uma novaVaga, sendo que é igual ao ultimo ID adicionado de 1
        def novaVagaId():
            with open('vagas_novas.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    pass
                return int(row[9])+1

        # Encontra e retorna uma novaVaga a partir de seu ID no banco vaags_novas
        def achaNovaVaga(vagaID):
            with open('vagas_novas.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    if row[9] == vagaID:
                        return Vaga.novaVaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6], row[7],row[8],row[9])
        
        # Passa uma novaVaga para ser adicionada ao banco_vagas
        def adicionaNovaVaga(vagaID):
            novaVaga = Vaga.novaVaga.achaNovaVaga(vagaID)
            Vaga.criaNovaVaga(novaVaga.locador, novaVaga.nome, novaVaga.endereço, novaVaga.preço, novaVaga.tipo, novaVaga.latitude, novaVaga.longitude, novaVaga.referencia, novaVaga.adicional)

    
    # Sub Classe de Vaga que remete a uma Avaliação de um locatario e ações realizada por ou sobre ela
    class Avaliação:
        # 0 data
        # 1 nota
        # 2 avaliador
        # 3 id_vaga
        # 4 comentario

        def __init__(self, data, nota, avaliador, idVaga, comentario):
            self.data = data
            self.nota = nota
            self.avaliador = avaliador
            self.id_vaga = idVaga
            self.comentario = comentario

        # Cria uma nova avalição a partir do id da vaag, a nota recebida, o locatario que avaliou e um possivel comentario adicional
        def avaliarVaga(vaga_id, nota, avaliador, comentario):
            vagaParaAvaliar = Vaga.achaVaga(vaga_id)
            vagaParaAvaliar.numeroAvaliacoes += 1
            vagaParaAvaliar.avaliacao = round(((vagaParaAvaliar.avaliacao)*(vagaParaAvaliar.numeroAvaliacoes-1) + int(nota))/(vagaParaAvaliar.numeroAvaliacoes),2)
            Vaga.atualizaVaga(vagaParaAvaliar)
            if comentario == '':
                comentario = ' '
            avaliacao = [datetime.datetime.now(), nota, avaliador, vaga_id, comentario]
            extra.Biblioteca.escritorLihaCsv('historico_avaliacoes.csv', avaliacao)

        def mostraAvaliacoes(vagaId):
            avaliacoes = []
            with open ('historico_avaliacoes.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    if row[3] == vagaId:
                        avaliacoes.append(Vaga.Avaliação(row[0],row[1],row[2],row[3],row[4]))
                return avaliacoes

    # vaga id row 0
    # entrada row 1
    # saida row 2
    # locatario row 3
    
    
    # Sub Classe de Vaga que remete a uma Reserva de uma vaga e ações realizada por ou sobre ela
    class Reserva:
        def __init__(self, id_vaga, entrada, saida, locatario):
            self.id_vaga = id_vaga
            self.entrada = entrada
            self.saida = saida
            self.locatario = locatario

        # Cria e retorna uma lista com id de todas vagas ocupadas por dado locatario a partir do banco reservas
        def minhasReservas(username):
            reservas = []
            with open ('reservas.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    if row[3] == username:
                        reservas.append(row[0])
                return reservas
        
        # Encontra uma reserva a partir do id da vaga
        def achaReserva(vaga_id):
            with open ('reservas.csv', encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    if row[0] == vaga_id:
                        return Vaga.Reserva(row[0], row[1], row[2], row[3])
            
        # Atualiza os dados de uma resrva o banco reservas
        def atualizaReserva(reserva):
            banco = 'reservas.csv'
            arquivoIntermediario = 'temp.csv'
            with open(banco, 'r', encoding="utf8") as csv_file, open(arquivoIntermediario, 'w', newline='') as temp:
                csv_reader = csv.reader(csv_file, delimiter=';')
                csv_writer = csv.writer(temp, delimiter=';')
                for row in csv_reader:
                    if row[0] == reserva.id_vaga:
                        row[1] = reserva.entrada
                        row[2] = reserva.saida
                        row[3] = reserva.locatario
                    csv_writer.writerow(row)
            extra.Biblioteca.devolveCSV(banco, arquivoIntermediario)
                    
        