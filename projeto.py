from tkinter import *
import tkinter as tk
from datetime import datetime
from pytz import timezone
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf"])
from fpdf import FPDF 
import csv

## Criando tela principal
class tela_opcoes():
    #construtor
    def __init__(self,master):
        #pega o identificador único do cliente de acordo com o arquivo relatorio_mesa.csv
        self.get_id()
        self.nomeuser = StringVar() #nome de usuário
        self.master = master #janela mestre
        self.frame = tk.Frame(self.master) #cria o frame
        self.nomeuser = "não identificado" #inicia com nome de usuário não identificado
        #self.nomeuser = "admin"
        self.estoque_aviso = 5 #valor para o qual se o estoque de um produto estiver abaixo gera um aviso
        self.usuarios = {}#diconário de usuários
        self.mesas_atendidas = 0#mesas atendidas
        self.lista_categorias = ["Entrada","Principal","Sobremesa","Bebida"] #lista de categorias
        self.produtos = {} #diconário de produtos, inicialmente vazio
        self.mesas = {"Mesa 1":{},"Mesa 2":{},"Mesa 3":{},"Mesa 4":{},"Mesa 5":{}}#diconário de produtos para mesas
        #leitura do arquivo de usuários
        with open("username.txt", "r") as reader:
            username = reader.readlines()
        #leitura do arquivo de produtos
        with open("produtos.txt","r") as reader:
            lista_produtos = reader.readlines()
        #cria diconário com usuários e senhas
        for user in username:
            split = user.split(' ')
            self.usuarios[split[0]] = split[1][:-1]
        #cria dicionário de produtos
        #split[0] = nome do produto, split[1] = estoque do produto, split[2] = preço do produto, split[3] = categoria
        for produto in lista_produtos:
            split = produto.split(' ')
            self.produtos[split[0]] = [split[1],split[2],split[3][:-1],"0"]#"0" para a quantidade vendida inicial
        #cria estruturas de dados adicionais    
        self.get_lista_produtos()
        self.get_produtos_categorias()

        #coletando data e hora local       
        self.get_data()
        
        # TITULO
        
        self.master.geometry("1350x700+0+0")
        self.master.configure(bg='slate gray')
        self.master.title("Billing System")
        title=Label(self.master,text="RESTAURANTE TUDO DE BOM",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
        
        # TELA DESCRICAO
        
        details=LabelFrame(self.master,text="Detalhes",font=("Arial Black",12),bg="dark slate gray",fg="white",relief=GROOVE,bd=10)
        details.place(x=0,y=80,relwidth=1)
        
        detalhe_data=Label(details,text="Data",font=("Arial Black",14),bg="dark slate gray",fg="white").grid(row=0,column=0,padx=15)
        cust_entry=Label(details,text=self.data_e_hora_sao_paulo_em_texto,font=("Arial Black",14),bg="dark slate gray",fg="white").grid(row=0,column=1,padx=8)
        
        detalhe_name=Label(details,text="Usuário: ",font=("Arial Black",14),bg="dark slate gray",fg="white").grid(row=0,column=2,padx=10)
        self.contact_entry=Label(details,text=self.nomeuser,font=("Arial Black",14),bg="dark slate gray",fg="white")
        self.contact_entry.grid(row=0,column=3,padx=8)
        
        
        # OPÇOES BUTOES
        self.login_button=Button(self.master,text="Login",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.login(self.login_button))
        self.login_button.place(x=100,y=180,width=150,height=100)
        self.logado = False
        
        self.produtos_button=Button(self.master,text="Produtos",font=("Arial Black",15),bg="dim gray",fg="white",command = self.produtos_button)
        self.produtos_button.place(x=100,y=280+50,width=150,height=100)
        
        self.relatorios_button=Button(self.master,text="Relatórios",font=("Arial Black",15),bg="dim gray",fg="white",command = self.relatorios_button)
        self.relatorios_button.place(x=100,y=380+100,width=150,height=100)
        
        billing_menu=LabelFrame(self.master,text="Mesas",font=("Arial Black",12),relief=GROOVE,bd=10,bg="midnight blue",fg="white")
        billing_menu.place(x=350,y=200,width=545,height=320)
        
        
        button_frame=Frame(billing_menu,bd=7,relief=GROOVE,bg="dark slate gray")
        button_frame.place(x=5,width=510,height=280)
        self.criar_mesas(button_frame)
        
        avisos_frame=LabelFrame(self.master,text="Avisos",font=("Arial Black",12),relief=GROOVE,bd=10,bg="midnight blue",fg="white")
        avisos_frame.place(x=350+545+30,y=180,width=350,height=500)
        
        self.avisos_estoque=Label(avisos_frame,text="",font=("Arial Black",8),bg="dark slate gray",fg="white")
        self.avisos_estoque.pack()

        self.avisos=Label(avisos_frame,text="",font=("Arial Black",8),bg="dark slate gray",fg="red")
        self.avisos.pack()        

    #método para gerar um identificador único a partir do arquivo relatorio_mesa.csv
    def get_id(self):
      #lê arquivo
      with open("relatorio_mesa.csv", "r") as reader:
        linhas = reader.readlines()
      #se o arquivo estiver vazio
      if linhas == []:
        #primeiro identificador igual a 1
        self.cliente_id = 1
      else:#se não estiver vazio
        #identificador igual o identificador mais recente mais um
        self.cliente_id = int(linhas[-1].split(';')[1])+1
      print(self.cliente_id)
            
    #método para calcular a data e hora no fuso horário de São Paulo
    def get_data(self):
      data_e_hora_atuais = datetime.now()
      fuso_horario = timezone("America/Sao_Paulo")
      data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
      self.data_e_hora_sao_paulo_em_texto = data_e_hora_sao_paulo.strftime("%d/%m/%Y %H:%M")
      return self.data_e_hora_sao_paulo_em_texto

    #método para criar um botão para cada mesa
    def criar_mesas(self,frame):
        space = 50 # espaçamento
        width = 100 #largura do botão
        posicoes = [[50,40],[50+space+width,40],[50+2*(space+width),40],[130,145],[280,145]]
        self.mesa_1 = Button(frame,text="Mesa 1",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.janela_mesa(self.mesa_1))
        self.mesa_1.place(x=posicoes[0][0],y=posicoes[0][1],width=width,height=80)
        self.mesa_2 = Button(frame,text="Mesa 2",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.janela_mesa(self.mesa_2))
        self.mesa_2.place(x=posicoes[1][0],y=posicoes[1][1],width=width,height=80)
        self.mesa_3 = Button(frame,text="Mesa 3",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.janela_mesa(self.mesa_3))
        self.mesa_3.place(x=posicoes[2][0],y=posicoes[2][1],width=width,height=80)
        self.mesa_4 = Button(frame,text="Mesa 4",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.janela_mesa(self.mesa_4))
        self.mesa_4.place(x=posicoes[3][0],y=posicoes[3][1],width=width,height=80)
        self.mesa_5 = Button(frame,text="Mesa 5",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.janela_mesa(self.mesa_5))
        self.mesa_5.place(x=posicoes[4][0],y=posicoes[4][1],width=width,height=80)
        
    #método para criar janela com opções de mesa
    def janela_mesa(self,mesa):
        janela = Toplevel()#cria janela
        #checa se usuário está logado
        if self.nomeuser == "não identificado":
            title=Label(janela,text="Faça login para utilizar os serviços",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
        else:
            #botões com opções de mesa
            title=Label(janela,text=mesa['text'],bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
            janela.configure(bg='slate gray')
            Button(janela,text="Adicionar Produto",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.add_rm(mesa,"add")).pack(fill=X)
            Button(janela,text="Remover Produto",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.add_rm(mesa,"rm")).pack(fill=X)
            Button(janela,text="Parcial",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.parcial(mesa)).pack(fill=X)
            Button(janela,text="Fechar Conta",font=("Arial Black",15),bg="dim gray",fg="white",command = lambda: self.janela_fechar_conta(mesa,janela)).pack(fill=X)
            
    #método para criar menu de opções com categorias e seus produtos
    def set_OptionMenu(self,janela):
        font = ("Calibri", "9", "bold")#escolhe a fonte
        #variáveis de texo
        self.txt_nome_produto = StringVar()
        self.txt_categoria_produto = StringVar()
        self.txt_categoria_produto.set(self.lista_categorias[0])#valor inicial é entrada
        #menu de categorias
        msg_categoria = Label(janela, text="Categoria do produto:",font=font, width=10).grid(row=0,column=0,padx=8,ipadx=100)
        menu_categoria = OptionMenu(janela, self.txt_categoria_produto, *self.lista_categorias)
        menu_categoria.grid(row=0,column=1,padx=8,ipadx=100)
        #menu de produtos que muda com a categoria
        msg_categoria = Label(janela, text="Produto:",font=font, width=10).grid(row=1,column=0,padx=8,ipadx=100)
        self.menu_produto = OptionMenu(janela, self.txt_nome_produto, *self.produtos_categorias[self.txt_categoria_produto.get()])
        self.menu_produto.grid(row=1,column=1,padx=8,ipadx=100)
        
        self.txt_categoria_produto.trace('w', self.update_OptionMenu)
        
    #método para criar janela para remover ou adicionar produtos em um mesa 
    def add_rm(self,mesa,flag):
        janela = Toplevel()#cria janela
        font = ("Calibri", "9", "bold")#escolhe a fonte
        #variável de texto
        self.txt_quantidade = StringVar()
        self.txt_quantidade.set('1')
        #lista com quantidades de 1 a 10
        self.lista_quantidades = [i for i in range(1,11)]
        #cria menu de opções com categorias e seus produtos
        self.set_OptionMenu(janela)
        #menu com opções de quantidades
        msg_categoria = Label(janela, text="Quantidade:",font=font, width=10).grid(row=2,column=0,padx=8,ipadx=100)
        menu_quantidade = OptionMenu(janela, self.txt_quantidade, *self.lista_quantidades)
        menu_quantidade.grid(row=2,column=1,padx=8,ipadx=100)
        #mensagem de sucesso ou erro
        self.add_msg = Label(janela, text=" ",font=font,fg="red", width=100)
        self.add_msg.grid(row=5,column=0,columnspan=3,padx=8,ipadx=100)
        #cria botão para adicionar ou remover
        if flag == "add":
            botao_add = Button(janela, text="Adicionar", command=lambda: self.add_produto(mesa))
            botao_add.grid(row=6,column=0,columnspan=2,ipadx=100,padx=8)
        else:
            botao_add = Button(janela, text="Remover", command=lambda: self.rm_produto(mesa))
            botao_add.grid(row=6,column=0,columnspan=2,ipadx=100,padx=8)
       
    #método que registra toda compra no arquivo relatorio_mesa.csv
    def relatorio_mesa_csv(self,n_mesa,n_cliente,produto,quantidade):
        
        data_cadastro = self.get_data()
        valor_unit_produto = float(self.produtos[produto][1])
        valor_total = valor_unit_produto * int(quantidade)
        #é salvo no arquivo a data do cadastro, o id do cliente, o número da mesa, o produto pedido, a quantidade, o valor unitário e o valor total
        msg = [data_cadastro,n_cliente,n_mesa,produto,quantidade,valor_unit_produto,valor_total]
        #abre arquivo para escrever no fim
        with open('relatorio_mesa.csv', 'a') as arquivo:
            writer = csv.writer(arquivo, delimiter=';')
            writer.writerow(msg)

    #método para adicionar produto em uma mesa
    def add_produto(self,mesa):
        #checa se existem produtos disponíveis no estoque
        if int(self.produtos[self.txt_nome_produto.get()][0]) >=  int(self.txt_quantidade.get()):
            #checa se mesa já foi aberta:
        
            if mesa["bg"] == "dim gray":
              #para cada nova atribuir um identificador (cliente_id) e incrementar o cliente_id para a próxima mesa ter um identificador único
              self.mesas[mesa['text']]['cliente'] = self.cliente_id
              self.cliente_id += 1
            #salva pedido no arquivo relatorio_mesa.csv
            self.relatorio_mesa_csv(mesa['text'],self.mesas[mesa['text']]['cliente'],self.txt_nome_produto.get(),self.txt_quantidade.get())
            #se produto já foi pedido, incrementar quantidade da mesa
            if self.txt_nome_produto.get() in self.mesas[mesa['text']]:
                self.mesas[mesa['text']][self.txt_nome_produto.get()] = str(int(self.mesas[mesa['text']][self.txt_nome_produto.get()])+int(self.txt_quantidade.get()))
            #se não, adicionar ao dicionário com a quantidade pedida 
            else:
                self.mesas[mesa['text']][self.txt_nome_produto.get()] = self.txt_quantidade.get()
            self.produtos[self.txt_nome_produto.get()][0]=str(int(self.produtos[self.txt_nome_produto.get()][0]) - int(self.txt_quantidade.get()))#atualiza a quantidade disponível em estoque
            self.atualizar_produto_arquivo()#atualiza o estoque no arquivo de produtos
            self.add_msg['text'] = "Produto adcionado com sucesso."#mensagem de sucesso
            mesa["bg"]="RoyalBlue4"#muda cor da mesa para mesa em atendimento
            self.estoque_check()#se algum produto estiver com baixo estoque gera um aviso
        else:
            self.add_msg['text'] = "Não existem itens suficientes no estoque."
            
    #método para remover produto de uma mesa
    def rm_produto(self,mesa):
        #checa se produto foi pedido
        if self.txt_nome_produto.get() in self.mesas[mesa['text']]:
            #checa se quantidade que deseja remover é menor ou igual a quantidade registrada na mesa
            if int(self.txt_quantidade.get()) > int(self.mesas[mesa['text']][self.txt_nome_produto.get()]):
                self.add_msg['text'] = "Não é possível remover mais de "+ self.mesas[mesa['text']][self.txt_nome_produto.get()] +" produtos."
            else:
                #salva pedido no arquivo relatorio_mesa.csv, no caso de remoções a quantidade e valor total são números negativos
                self.relatorio_mesa_csv(mesa['text'],self.mesas[mesa['text']]['cliente'],self.txt_nome_produto.get(),str(-int(self.txt_quantidade.get())))
                self.mesas[mesa['text']][self.txt_nome_produto.get()] = str(int(self.mesas[mesa['text']][self.txt_nome_produto.get()])-int(self.txt_quantidade.get())) #atualiza a quantidade do produto na mesa
                self.produtos[self.txt_nome_produto.get()][0]=str(int(self.produtos[self.txt_nome_produto.get()][0]) + int(self.txt_quantidade.get()))#atualiza a quantidade disponível em estoque
                self.atualizar_produto_arquivo()#atualiza o estoque no arquivo de produtos
                self.add_msg['text'] = "Produto removido com sucesso."#mensagem de sucesso
                self.estoque_check()#se algum produto estiver com baixo estoque gera um aviso
        else:
            self.add_msg['text'] = "Produto ainda não adicionado nessa mesa."
                                 
    #método auxiliar para atualizar menu de produtos de acordo com a categoria            
    def update_OptionMenu(self,*args):
        menu = self.menu_produto['menu']
        menu.delete(0, "end")
        #para cada produto da categoria
        for value in self.produtos_categorias[self.txt_categoria_produto.get()]:
            #adiciona produto no menu
            menu.add_command(label=value, command=lambda v=value: self.txt_nome_produto.set(v))
        self.txt_nome_produto.set(self.produtos_categorias[self.txt_categoria_produto.get()][0])
        
    #método para gerar texto da parcial    
    def get_parcial(self,mesa):
        msg = "DATA: \t"+self.data_e_hora_sao_paulo_em_texto+"\n"
        msg += mesa['text']+"\n"
        msg += "Produto \t\t Quantidade \t Preço \t\t Valor \n"
        msg += "---------------------------------------------------------------------------------------\n"
        total = 0
        #para cada produto pedido
        for produto, quantidade in self.mesas[mesa['text']].items():
                if produto != 'cliente':
                  preco = self.produtos[produto][1]
                  valor = round(int(quantidade)*float(preco),2)
                  total += valor
                  #msg += produto+' \t\t '+quantidade+' \t\t '+preco+' \t\t '+str(valor)+'\n'
                  msg += '{} \t\t {} \t\t {:.2f} \t\t {:.2f}\n'.format(produto,quantidade,float(preco),valor)
        msg += "---------------------------------------------------------------------------------------\n"
        msg += "Total: \t{:.2f}\n".format(total)
        return msg
    
    #método para criar janela para mostrar parcial de uma mesa  
    def parcial(self,mesa):
        janela = Toplevel()#cria janela
        font = ("Calibri", "12", "bold")#escolhe a fonte
        #título da janela
        title=Label(janela,text="Parcial",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
        #texto da parcial        
        msg = self.get_parcial(mesa)
        label = Label(janela, text=msg,font=font, justify=tk.LEFT).pack(side="left")
        
    #método para fechar a conta de uma mesa e gerar um pdf com a conta

    def janela_fechar_conta(self,mesa,janela):
        janela_conta = Toplevel()#cria janela
        font = ("Calibri", "12", "bold")#escolhe a fonte
        #título da janela
        title=Label(janela_conta,text="Fechar Conta",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
        #texto da parcial        
        msg = self.get_parcial(mesa)
        label = Label(janela_conta, text=msg,font=font, justify=tk.LEFT).pack(fill=X)
        self.fechar_msg = Label(janela_conta, text=" ",font=font,fg="red", width=10)
        self.fechar_msg.pack(fill=X)
        #cria botão para atualizar
        butao_cadastrar = Button(janela_conta,fg="white", bg="RoyalBlue4", text="Confirmar", command = lambda: self.fechar_conta(mesa,janela,janela_conta,"confirmar"))
        butao_cadastrar.pack(side="left",ipadx=100)
        butao_cadastrar = Button(janela_conta,fg="white", bg="RoyalBlue4", text="Imprimir", command = lambda: self.fechar_conta(mesa,janela,janela_conta,"imprimir"))
        butao_cadastrar.pack(side="right",ipadx=100)

    def fechar_conta(self,mesa,janela,janela_conta,flag):
        msg = self.get_parcial(mesa)#gera a conta com o parcial atual
        #gera pdf com a conta da mesa
        with open(mesa['text']+".txt", "w") as reader:
            reader.write(msg)
        arquivo = open(mesa['text']+".txt", "r")
        pdf = FPDF() 
        pdf.add_page() 
        pdf.set_font("Arial", size = 12) 
        for linha in arquivo: 
            pdf.cell(200, 10, txt = linha, ln = 1, align = 'L')
        pdf.output(mesa['text']+".pdf")
        if flag == "confirmar":
          janela_conta.destroy()
          janela.destroy()#fecha janela
          mesa["bg"]="dim gray"#muda para cor de mesa vaga
          self.mesas_atendidas+=1#incrementa quantidade de mesas atenddas
          #para cada produto vendido para a mesa, incrementar a quantidade vendida  
          for produto, quantidade in self.mesas[mesa['text']].items():
            if produto != 'cliente':
              self.produtos[produto][3] = str(int(quantidade)+int(self.produtos[produto][3])) 
          self.mesas[mesa['text']]={}
        else:
          self.fechar_msg["text"] = "Conta impressa com sucesso"
    
    #método para criar janela do menu de produtos 
    def produtos_button(self):
        janela = Toplevel()#cria janela
        #restrição para ser apenas acessável pelo admin
        if self.nomeuser == "admin":
            #botões para abrir janelas de cadastro, remoção, atualização e estoque
            title=Label(janela,text="Produtos",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
            Button(janela,text="Cadastrar Produto",font=("Arial Black",15),bg="dim gray",fg="white",command = self.cadastrar_produto).pack(fill=X)
            Button(janela,text="Remover Produto",font=("Arial Black",15),bg="dim gray",fg="white",command = self.remover_produto).pack(fill=X)
            Button(janela,text="Atualizar Produto",font=("Arial Black",15),bg="dim gray",fg="white",command = self.atualizar_produto).pack(fill=X)
            Button(janela,text="Estoque",font=("Arial Black",15),bg="dim gray",fg="white",command = self.estoque).pack(fill=X)
        else:
            title=Label(janela,text="Acesso não autorizado, logar como admin.",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
    
    #método para criar janela de cadastro de produto 
    def cadastrar_produto(self):
        janela = Toplevel()#cria janela
        font = ("Calibri", "9", "bold")#escolhe a fonte
        #variáveis de texto
        self.txt_nome_produto = StringVar()
        self.txt_estoque = StringVar()
        self.txt_preco = StringVar()
        self.txt_categoria_produto = StringVar()
        self.txt_categoria_produto.set(self.lista_categorias[0])
        #cria entradas de texto para nome do produto, estoque e preço
        rotulos = ["Nome do Produto","Estoque inicial","Preço"]
        variaveis = [self.txt_nome_produto,self.txt_estoque,self.txt_preco]
        self.create_entry(rotulos,variaveis,janela,font,1)
        #menu de opções para escolha de categoria
        msg_categoria = Label(janela, text="Categoria do produto:",font=font, width=10).grid(row=4,column=0,padx=8,ipadx=100)
        self.categoria_produto = OptionMenu(janela, self.txt_categoria_produto, *self.lista_categorias)
        self.categoria_produto.grid(row=4,column=1,padx=8,ipadx=100)
        #mensagem de sucesso ou falha
        self.produto_msg = Label(janela, text=" ",font=font,fg="red", width=10)
        self.produto_msg.grid(row=5,column=0,columnspan=3,padx=8,ipadx=100)
        #cria botão para cadastrar
        botao_cadastrar = Button(janela, text="Cadastrar", command=self.cadastro_produto_check)
        botao_cadastrar.grid(row=6,column=0,columnspan=2,ipadx=100,padx=8)
        
    #método para criar janela de atualização de produto 
    def atualizar_produto(self):
        janela = Toplevel()#cria janela
        font = ("Calibri", "9", "bold")#escolhe a fonte
        #variáveis de texto
        self.txt_estoque = StringVar()
        self.txt_preco = StringVar()
        #cria menu de opções com categorias e seus produtos
        self.set_OptionMenu(janela)
        #cria entradas de texto para novo estoque e preço
        rotulos = ["Novo estoque","Novo preço"]
        variaveis = [self.txt_estoque,self.txt_preco]
        self.create_entry(rotulos,variaveis,janela,font,2)
        #mensagem de sucesso ou falha
        self.produto_msg = Label(janela, text=" ",font=font,fg="red", width=10)
        self.produto_msg.grid(row=5,column=0,columnspan=3,padx=8,ipadx=100)
        #cria botão para atualizar
        butao_cadastrar = Button(janela, text="Atualizar", command=self.atualizar_produto_check)
        butao_cadastrar.grid(row=6,column=0,columnspan=2,ipadx=100,padx=8)
        
    #método para criar janela de remoção de produto    
    def remover_produto(self):
        janela = Toplevel()#cria janela
        font = ("Calibri", "9", "bold")#escolhe a fonte
        self.nome_produto_remover = StringVar()
        #cria entrada de texto para escolher o produto que será removido
        self.create_entry(['Nome do Produto'],[self.nome_produto_remover],janela,font,0)
        #mensagem de sucesso ou falha
        self.msg_remover = Label(janela, text=" ",font=font,fg="red", width=10)
        self.msg_remover.grid(row=1,column=0,columnspan=3,padx=8,ipadx=100)
        #cria botão para remover
        butao_remover = Button(janela, text="Remover", command=self.remover_produto_check)
        butao_remover.grid(row=2,column=0,columnspan=2,ipadx=100,padx=8)
        
    #texto para o estoque
    def get_estoque(self):
        msg = "Produto \t\t Quantidade \t Preço \n"
        msg += "--------------------------------------------------------------\n"
        #percorre todos os produtos no dicionário | lista[0] = qnt em estoque, lista[1] = preço, lista[2] = categoria, lista[3] = valor
        for chave, lista in self.produtos.items():
                msg += '{} \t\t {} \t\t {:.2f}\n'.format(chave,lista[0],float(lista[1]))
        return msg
        
    #método para criar janela para visualizar o estoque
    def estoque(self):
        janela = Toplevel()#cria janela
        font = ("Calibri", "12", "bold")#escolhe a fonte
        title=Label(janela,text="Estoque",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
        msg = self.get_estoque()#pega o texto do estoque
        label = Label(janela, text=msg,font=font, justify=tk.LEFT).pack(side="left")
        
    #método para checar se um produto tem estoque baixo, avisa se tem 
    def estoque_check(self):
        self.avisos_estoque["text"] = self.get_estoque()
        #percorre todos os produtos no dicionário | lista[0] = qnt em estoque, lista[1] = preço, lista[2] = categoria, lista[3] = valor
        msg = ""
        for produto, lista in self.produtos.items():
            if int(lista[0]) < self.estoque_aviso:#se estoque menor que um valor limite
                msg += "Estoque de "+produto+" abaixo de "+str(self.estoque_aviso)+"! Unidades restantes: "+lista[0]+"\n"
        self.avisos["text"] = msg

    #método para gerar lista de produtos a partir do dicionário de produtos
    def get_lista_produtos(self):
        self.lista_produtos = []#lista vazia
        for key in self.produtos.keys():#para todo produto
            self.lista_produtos.append(key)#inserir produto na lista
            
    #método para atualizar dicionário de produtos por categorias. ex: {"entrada":[pastel,espeto],"principal":[bife],"sobremesa":[pudim],"bebida":[coca]}
    def get_produtos_categorias(self):
        self.produtos_categorias = {}#dicionário vazio
        for categoria in self.lista_categorias:#para cada categoria
            self.produtos_categorias[categoria] = []#criar lista vazia
        for chave, lista in self.produtos.items():#para todo produto
            self.produtos_categorias[self.produtos[chave][2]].append(chave)#adicionar produto a lista de sua categoria
        print(self.produtos_categorias)
        
    #método auxiliar para criar entradas de texto    
    def create_entry(self,rotulos,variaveis,janela,font,row):
        #para todos os rótulos de entradas
        for i, rotulo in enumerate(rotulos):
            #cria mensagem do lado esquerdo da entrada de texto
            msg = Label(janela, text=rotulo+":",font=font, width=10).grid(row=row+i,column=0,padx=8,ipadx=100)
            #cria entrada de texto
            entrada = Entry(janela,width=25,font=font,textvariable=variaveis[i])
            #se for uma senha mostrar como *
            if rotulo == 'Senha':
                entrada['show'] = '*'
            entrada.grid(row=row+i,column=1,padx=8) # posicionamento da entrada de texto
    
    #método para gerar texto do relatório
    def get_relatorio(self):
        print(self.produtos)
        msg = "DATA: \t"+self.data_e_hora_sao_paulo_em_texto+"\n\n"
        msg += "Produtos vendidos hoje:\n\n"
        msg += "Produto \t\t Estoque \t\t Qtd Vendida \t Preço \t\t Valor \n"
        msg += "---------------------------------------------------------------------------------------------------------------\n"
        total = 0
        max_vendas = ["None","0"]
        max_faturamento = ["None","0"]
        #percorre todos os produtos | lista[0] = qnt em estoque, lista[1] = preço, lista[2] = categoria, lista[3] = valor
        for produto, lista in self.produtos.items():
                if int(lista[3]) > 0:
                    estoque = lista[0]
                    preco = lista[1]
                    quantidade = lista[3]
                    valor = int(quantidade)*float(preco)
                    total += valor
                    #msg += produto+' \t\t '+estoque+' \t\t '+quantidade+' \t\t '+preco+' \t\t '+str(valor)+'\n'
                    msg += '{} \t\t {} \t\t {} \t\t {:.2f} \t\t {:.2f}\n'.format(produto,estoque,quantidade,float(preco),valor)
                    #identifica produto mais vendido e produto com maior faturamento
                    if int(quantidade) > int(max_vendas[1]):
                        max_vendas = [produto,quantidade]
                    if valor > float(max_faturamento[1]):
                        max_faturamento = [produto,str(valor)]
        msg += "---------------------------------------------------------------------------------------------------------------\n"
        msg += "Total vendido: \t{:.2f}\n".format(total)
        msg += "Total de mesas atendidas: \t"+str(self.mesas_atendidas)+"\n"
        if self.mesas_atendidas == 0:
            msg += "Ticket médio: \t0.00\n"
        else:
            msg += "Ticket médio: \t{:.2f}\n".format(total/self.mesas_atendidas)
        msg += "Produto mais vandido: \t"+max_vendas[0]+"\t Vendas: \t"+max_vendas[1]+"\n"
        msg += "Produto de maior faturamento: \t"+max_faturamento[0]+"\t Total: \t{:.2f}\n".format(float(max_faturamento[1]))
        return msg

    #método para gerar texto próprio para o formato csv
    def get_relatorio_csv(self):
        print(self.produtos)
        msg = "DATA,"+self.data_e_hora_sao_paulo_em_texto+"\n"
        msg += "Produtos vendidos hoje\n"
        msg += "Produto,Estoque,Qtd Vendida,Preço,Valor \n"
        total = 0
        max_vendas = ["None","0"]
        max_faturamento = ["None","0"]
        #percorre todos os produtos | lista[0] = qnt em estoque, lista[1] = preço, lista[2] = categoria, lista[3] = valor
        for produto, lista in self.produtos.items():
                if int(lista[3]) > 0:
                    estoque = lista[0]
                    preco = lista[1]
                    quantidade = lista[3]
                    valor = int(quantidade)*float(preco)
                    total += valor
                    msg += produto+','+estoque+','+quantidade+','+preco+','+str(valor)+'\n'
                    #identifica produto mais vendido e produto com maior faturamento
                    if int(quantidade) > int(max_vendas[1]):
                        max_vendas = [produto,quantidade]
                    if valor > float(max_faturamento[1]):
                        max_faturamento = [produto,str(valor)]
        msg += "Total vendido,"+str(total)+"\n"
        msg += "Total de mesas atendidas,"+str(self.mesas_atendidas)+"\n"
        if self.mesas_atendidas == 0:
            msg += "Ticket médio,"+str(0)+"\n"
        else:
            msg += "Ticket médio,"+str(total/self.mesas_atendidas)+"\n"
        msg += "Produto mais vandido,"+max_vendas[0]+",Vendas,"+max_vendas[1]+"\n"
        msg += "Produto de maior faturamento,"+max_faturamento[0]+",Total,"+max_faturamento[1]+"\n"
        self.relatorio_msg["text"] = "csv gerado com sucesso"
        return msg
            
    #método para construir a janela de relatório
    def relatorios_button(self):
        janela = Toplevel()#cria janela
        font = ("Calibri", "12", "bold")#escolhe a fonte
        title=Label(janela,text="Relatório",bd=12,relief=RIDGE,font=("Arial Black",20),bg="RoyalBlue4",fg="white").pack(fill=X)
        msg = self.get_relatorio()#pega o texto do relatório
        label = Label(janela, text=msg,font=font, justify=tk.LEFT).pack(fill=X)#mostra texto na janela
        self.relatorio_msg = Label(janela, text=" ",font=font,fg="red", width=15)
        self.relatorio_msg.pack(fill=X)
        self.loginButton = Button(janela,font=font,fg="white", text="Gerar csv", command=self.gera_csv,bg="RoyalBlue4").pack(fill=X)

    #método para gerar o csv com o relatório
    def gera_csv(self):
      with open("relatorio.csv", "w") as reader:
        reader.write(self.get_relatorio_csv())

    #método para construir janela de login
    def login(self,button):
        #se não está logado
        if self.logado == False:
            self.janela_login = Toplevel()#cria janela
            font = ("Calibri", "9", "bold")#escolhe a fonte
            
            self.txtusuario = StringVar()#variável para nome de usuário
            self.txtsenha = StringVar()#variável para senha de usuário
            rotulos = ["Usuário","Senha"] #nome dos campos da entrada de texto
            variaveis = [self.txtusuario, self.txtsenha]
            self.create_entry(rotulos,variaveis,self.janela_login,font,0)#cria entradas de texto
            #mensagem de sucesso ou falha
            self.login_msg = Label(self.janela_login, text=" ",font=font,fg="red", width=10)
            self.login_msg.grid(row=2,column=0,columnspan=3,ipadx=100)
            #botão de login
            self.loginButton = Button(self.janela_login, text="Login", command=self.login_check)
            self.loginButton.grid(row=3,column=0,padx=8)
            #botão de cadastro
            cadastroButton = Button(self.janela_login, text="Cadastro", command=self.cadastro_usuario).grid(row=3,column=1,padx=8)
        #se está logado
        else:
            #deslogar
            self.logado = False
            self.login_button['text'] = "Login"
            self.contact_entry['text'] = "não identificado"
            self.nomeuser = "não identificado"
            
    #método para verificar o login e pegar o nome de usuário        
    def login_check(self):
        #check se usuário está cadastrado
        if self.txtusuario.get() in self.usuarios:
            #teste para verificar se senha está correta
            if self.txtsenha.get() == self.usuarios[self.txtusuario.get()]:
                self.nomeuser = self.txtusuario.get()#pega o nome de usuário inserido
                self.contact_entry['text'] = self.nomeuser#muda o nome de usuário
                self.logado = True #muda estado para logado
                self.login_button['text'] = "Logout"#muda o texto do botão para Logout
                self.estoque_check()
                self.janela_login.destroy() # fecha janela de login
            else:
                self.login_msg['text'] = "Senha incorreta."
        else:
            self.login_msg['text'] = "Usuário não encontrado."
    
    #método para cadastrar um novo produto
    def cadastro_produto_check(self):
        #check para verificar se o produto ainda não foi cadasrado
        if self.txt_nome_produto.get().lower() in self.produtos:
            self.produto_msg['text'] = "Produto já cadastrado."
        else:
            #check para verificar se o novo estoque e preço possuem valores compatíveis (inteiro e real)
            try: 
                #insere novo produto no dicionário de produtos
                self.produtos[self.txt_nome_produto.get().lower()] = [str(int(self.txt_estoque.get())),str(float(self.txt_preco.get())),self.txt_categoria_produto.get(),"0"]
                self.atualizar_checar("Produto cadastrado com sucesso.",self.produto_msg)
            except Exception:
                self.produto_msg['text'] = "Valor para estoque e/ou preço inválido."
    
    #método para atualizar o preço e estoque de um produto cadastrado
    def atualizar_produto_check(self):
        #check para verificar se o novo estoque e preço possuem valores compatíveis (inteiro e real)
        try: 
            #atualiza dicionário de produtos
            self.produtos[self.txt_nome_produto.get()] = [str(int(self.txt_estoque.get())),str(float(self.txt_preco.get())),self.txt_categoria_produto.get(),self.produtos[self.txt_nome_produto.get()][3]]
            self.atualizar_checar("Produto atualizado com sucesso.",self.produto_msg)
        except Exception:
                self.produto_msg['text'] = "Valor para estoque e/ou preço inválido."

    #método para remover um produto cadastrado        
    def remover_produto_check(self):
        #check para verificar se o produto está cadastrado
        if self.nome_produto_remover.get().lower() in self.produtos:
            self.produtos.pop(self.nome_produto_remover.get().lower())#remove produto do dicionário
            self.atualizar_checar("Produto removido com sucesso.",self.msg_remover)
        else:
            self.msg_remover['text'] = "Esse produto não foi cadastrado."
            
    #método auxiliar que atualizar arquivos, estruturas de dados e imprime mensagem de sucesso        
    def atualizar_checar(self,msg,janela):
        self.atualizar_produto_arquivo()#atualiza arquivo de produtos
        janela['text'] = msg#mensagem de sucesso
        self.get_lista_produtos()#atualiza a lista de produtos
        self.get_produtos_categorias()#gera lista de produtos separados por categorias
        self.estoque_check()#verifica se algum produto tem estoque baixo
            
    #método para cadastrar um novo usuário
    def cadastro_usuario(self):
        #check para ver se usuário já está cadastrado
        if self.txtusuario.get() in self.usuarios:
            self.login_msg['text'] = "Usuário já cadastrado."
        else:
            self.usuarios[self.txtusuario.get()] = self.txtsenha.get() #adiciona senha e usuário ao dicionário de usuários
            self.salvar_usuario(self.txtusuario.get(), self.txtsenha.get()) #método para salvar novo usuário
            self.nomeuser = self.txtusuario.get() 
            self.contact_entry['text'] = self.nomeuser #muda nome de usuário
            self.logado = True #consdera que está logado
            self.login_button['text'] = "Logout" #muda o texto do botão para Logout
            self.estoque_check()
            self.janela_login.destroy() #fecha a janela
            
    #método para salvar novo usuário no arquivo .txt dos usuários
    def salvar_usuario(self,usuario,senha):
        #abre arquivo no modo append
        with open("username.txt", "a") as reader:
            reader.write(usuario+' '+senha+'\n')
            
    #método para atualizar o arquivo .txt dos produtos
    def atualizar_produto_arquivo(self):
        #abre arquivo no modo write
        with open("produtos.txt", "w") as reader:
            #loop para percorrer todos os elementos do dicionário de produtos
            for produto, lista in self.produtos.items():
                #lista[0] = qnt em estoque, lista[1] = preço, lista[2] = categoria
                reader.write(produto+' '+lista[0]+' '+lista[1]+' '+lista[2]+'\n')
    
    #método para fechar o app
    def close_windows(self):
        self.master.destroy()
        
#função principal que chama o app 
def main(): 
    root = Tk()
    app = tela_opcoes(root)
    root.mainloop()

main()
