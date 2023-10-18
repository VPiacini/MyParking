import csv, os, smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

senhaMuitoSecreta = 'bumbrfpbornycqbc'
# classe com funções basicas do sistema geral
class Biblioteca:
    # função que escreve uma linha no final do csv
    def escritorLihaCsv(nome_csv, dados):
        with open(nome_csv,'a', encoding='UTF8', newline='') as arquivo:
            new_data = csv.writer(arquivo, delimiter=';')
            new_data.writerow(dados)  

    # função de faz overwrite de um csv em outro e apaga o que foi copiado
    def devolveCSV(csv_original, temp):
        with open(temp, 'r') as temporario, open(csv_original, 'w', newline='') as original:
            csv_reader = csv.reader(temporario, delimiter=';')
            csv_writer = csv.writer(original, delimiter=';')
            for row in csv_reader:
                csv_writer.writerow(row)
        os.remove(temp)

    # envia e-mail a partir do Simple Mail Transfer Protocol(SMTP) do Gmail utilizando a conta criada para o sistema myparking312@gmail.com
    def enviaAviso(mail, subject, mensagem):
        sender_email = 'myparking312@gmail.com'
        sender_password = senhaMuitoSecreta
        receiver_email = mail

        message = MIMEMultipart()

        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(mensagem, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()