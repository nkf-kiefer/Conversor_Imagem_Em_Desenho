#biblioteca tkinter para interface gráfica
from tkinter import *
from tkinter import Tk, ttk, filedialog
from tkinter.ttk import Combobox
#biblioteca para manipulação e processamento de imagem
from PIL import ImageTk, Image, ImageEnhance, ImageFilter
#biblioteca para manipulação e processamento de imagem e visão computacional
import cv2
#biblioteca que interage com o sistema operacional
import os

#cores usadas no projeto 
co0 = "#f0f3f5"  # Preto
co1 = "#feffff"  # Branco
co2 = "#4fa882"  # Verde
co3 = "#38576b"  # Valor
co4 = "#403d3d"  # Letra
co5 = "#e06636"  # Profit
co6 = "#038cfc"  # Azul

#criando janela
janela = Tk()
janela.title('Conversor para desenho a lápis')
janela.geometry('450x650') #tamanho da janela
janela.configure(background=co1)
janela.resizable(width=FALSE, height=FALSE) #para não conseguir alterar o tamanho da janela 

#inicio da lógica (Variaveis globais)
global imagem_original, imagem_convertida, combo_cor
imagem_original = None
imagem_convertida = None
#garantindo que as variáveis não serão alteradas incorretamente

#criação de funções

# Criar combobox para escolha da cor
def escolher_cor():
 combo_cor = Combobox(frame_controls, values=["vermelho", "azul", "verde"], state="readonly")
 combo_cor.set("vermelho")  # Valor padrão
 combo_cor.grid(row=7, column=1)

# Dentro de converter_imagem:
 cor = combo_cor.get()  # Pega a cor selecionada pelo usuário

#função para escolher imagem
def escolher_imagem():
    global imagem_original
    caminho = filedialog.askopenfilename() #pegando o caminho da imagem dentro do pc da pessoa
    if caminho: # se ela informar um caminho
        imagem_original = Image.open(caminho)
        imagem_preview = imagem_original.resize((200, 200))#agora a imagem selecionada tem um tamanho unico
        imagem_preview = ImageTk.PhotoImage(imagem_preview) #preparando a imagem para o tkinter
        l_preview_original.configure(image=imagem_preview) #atualizando e mostrando a imagem com as dimensões redefinidas 
        l_preview_original.image = imagem_preview #jogou a imagem original na variavel l_preview_original.image


#função para converter a imagem
def converter_imagem(event=None):
    global imagem_original, imagem_convertida

    if imagem_original is None: #se não tiver imagem nenhuma ele retorna ao inicio
        return

    # Ajustes do usuário/ coletando o nivel que ele deixou la na barrinha de deslize
    intensidade = s_intensidade.get()
    brilho = s_brilho.get() / 100
    contraste = s_contraste.get() / 100
    tonalidade = s_tonalidade.get() / 100
    desfoque = s_desfoque.get()
    vintage = s_vintage.get()

    # Conversão para desenho a lápis
    imagem_cv = cv2.cvtColor(cv2.imread(imagem_original.filename), cv2.COLOR_BGR2GRAY) #convertendo a cor para preto e branco
    blur = cv2.GaussianBlur(imagem_cv, (21, 21), 0) #metodo de suavização da imagem
    r = 256 #dando um valor para preservar o brilho e contraste durante a conversão
    sketch = cv2.divide(imagem_cv, blur, scale=r) #dividindo pixel a pixel os valores até 256 afim de preservar a imagem 

    #convertendo um array para uma imagem
    pil_sketch = Image.fromarray(sketch)

    # Ajustar intensidade
    if intensidade != 0:
        pil_sketch = pil_sketch.point(lambda p: min(255, p * intensidade / 100))
        #garantindo que não passe de 255 o brilho e fazendo o percentual de quanto mudar com base no que o usuário passar (p=pixels)

    # Ajustar brilho(método padrão da biblioteca pillow)
    enhancer_brilho = ImageEnhance.Brightness(pil_sketch)
    pil_sketch = enhancer_brilho.enhance(brilho)

    # Ajustar contraste(método padrão da biblioteca pillow)
    enhancer_contraste = ImageEnhance.Contrast(pil_sketch)
    pil_sketch = enhancer_contraste.enhance(contraste)

    # Ajustar tonalidade
    if pil_sketch.mode != "RGB":  # Converter para RGB se necessário
        pil_sketch = pil_sketch.convert("RGB")
    cor = combo_cor.get()  # Aqui você pode ajustar a cor (vermelho, azul, verde) ou criar um controle para o usuário
    pil_sketch = aplicar_tonalidade(pil_sketch, s_tonalidade.get(), cor)

    # Ajustar desfoque(método padrão da biblioteca pillow)
    pil_sketch = pil_sketch.filter(ImageFilter.GaussianBlur(radius=desfoque))

    # Chamar o efeito vintage com base no valor do slider
    if vintage >= 0:
        pil_sketch = aplicar_vintage(pil_sketch, vintage)

    # Redimensionar para exibição
    imagem_convertida = pil_sketch #coletando a imagem em preto e branco e armazenando
    imagem_preview = imagem_convertida.resize((200, 200)) #adptando o tamanho
    imagem_preview = ImageTk.PhotoImage(imagem_preview) #transformando no formato certo para o tkinter
    l_preview_convertida.configure(image=imagem_preview) #atribuindo a imagem preview na variavel preview_convertida
    l_preview_convertida.image = imagem_preview #mostrando a preview pro usuário 


# Aplicar efeito vintage
def aplicar_vintage(imagem, intensidade_vintage):
    # Converter para RGB para não dar erros
    if imagem.mode != "RGB":
        imagem = imagem.convert("RGB")
    
    # Dividir as cores para manipular
    r, g, b = imagem.split()
    
    # Ajustar os canais para simular o efeito vintage (amarelado)
    r = r.point(lambda i: min(255, i + intensidade_vintage * 2 ))  # Incrementa o vermelho
    g = g.point(lambda i: min(255, i + intensidade_vintage))      # Incrementa o verde
    b = b.point(lambda i: max(0, i - intensidade_vintage))        # Reduz o azul
    
    # Combinar os canais novamente
    return Image.merge("RGB", (r, g, b))

#função para salvar a imagem convertida
def salvar_imagem_convertida():
    if imagem_convertida: #salvando a imagem em qualquer diretorio sendo o arquivo gerado uma .png
        caminho = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", ".png"), ("all files", ".*")]) 
        if caminho:
            imagem_convertida.save(caminho) #salvando o png no caminho definido pelo usuário

# Função para aplicar tonalidade
def aplicar_tonalidade(imagem, intensidade, cor):
    r, g, b = imagem.convert("RGB").split() #manipulando o red green e blue separadamente
    if cor == "vermelho":
        r = r.point(lambda i: min(255, i + intensidade))  # Incrementa o vermelho
    elif cor == "azul":
        b = b.point(lambda i: min(255, i + intensidade))  # Incrementa o azul
    elif cor == "verde":
        g = g.point(lambda i: min(255, i + intensidade))  # Incrementa o verde
    return Image.merge("RGB", (r, g, b))

#Daqui para baixo é mais estetica e posicionamento!

#dividindo o contéúdo da janela em três partes esse seria o header por exemplo
frame_top = Frame(janela, width=450, height=50, background=co1)
frame_top.grid(row=0, column=0, padx=10, pady=5)

frame_preview = Frame(janela, width=450, height=220, background=co1)
frame_preview.grid(row=1, column=0, padx=10, pady=5)

frame_controls = Frame(janela, width=450, height=200, background=co1)
frame_controls.grid(row=2, column=0, padx=10, pady=5)

#logo e titulo
logo = Label(frame_top, text='Conversor para Desenho a Lapis', font=("Arial", 16, 'bold'), bg=co1, fg=co4)
logo.pack()

# Previews é o texto que fica em cima das imagens
l_preview_original = Label(frame_preview, text='Previa Original', font=("Arial", 12), bg=co1, fg=co4)
l_preview_original.place(x=30, y=10)

l_preview_convertida = Label(frame_preview, text='Previa Convertida', font=("Arial", 12), bg=co1, fg=co4)
l_preview_convertida.place(x=240, y=10)

#Controles (botões para serem arrastados)
ttk.Label(frame_controls, text='Intensidade', background=co1).grid(row=0, column=0, padx=10, pady=5, sticky='w')
s_intensidade = Scale(frame_controls, command=converter_imagem, from_=50, to=300, orient=HORIZONTAL, length=180, bg=co1, fg=co4)
s_intensidade.set(120)
s_intensidade.grid(row=1, column=0, padx=10, pady=5)

ttk.Label(frame_controls, text='Brilho', background=co1).grid(row=2, column=0, padx=10, pady=5, sticky='w')
s_brilho = Scale(frame_controls, command=converter_imagem, from_=50, to=200, orient=HORIZONTAL, length=180, bg=co1, fg=co4)
s_brilho.set(120)
s_brilho.grid(row=3, column=0, padx=10, pady=5)

ttk.Label(frame_controls, text='Contraste', background=co1).grid(row=4, column=0, padx=10, pady=5, sticky='w')
s_contraste = Scale(frame_controls, command=converter_imagem, from_=50, to=200, orient=HORIZONTAL, length=180, bg=co1, fg=co4)
s_contraste.set(120)
s_contraste.grid(row=5, column=0, padx=10, pady=5)

ttk.Label(frame_controls, text='Tonalidade', background=co1).grid(row=0, column=1, padx=10, pady=5, sticky='w')
s_tonalidade = Scale(frame_controls, command=converter_imagem, from_=50, to=300, orient=HORIZONTAL, length=180, bg=co1, fg=co4)
s_tonalidade.set(120)
s_tonalidade.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(frame_controls, text='Desfoque', background=co1).grid(row=2, column=1, padx=10, pady=5, sticky='w')
s_desfoque = Scale(frame_controls, command=converter_imagem, from_=0, to=10, orient=HORIZONTAL, length=180, bg=co1, fg=co4)
s_desfoque.set(3)
s_desfoque.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(frame_controls, text='Vintage', background=co1).grid(row=4, column=1, padx=10, pady=5, sticky='w')
s_vintage = Scale(frame_controls, command=converter_imagem, from_=0, to=10, orient=HORIZONTAL, length=180, bg=co1, fg=co4)
s_vintage.set(5)
s_vintage.grid(row=5, column=1, padx=10, pady=5)

ttk.Label(frame_controls, text='Selecionar Cor', background=co1).grid(row=6, column=0, padx=10, pady=5, sticky='w')
combo_cor = Combobox(frame_controls, values=["vermelho", "azul", "verde"], state="readonly")
combo_cor.set("vermelho")  # Valor padrão
combo_cor.grid(row=7, column=0, padx=10, pady=5)

#botões
b_escolher = Button(janela, command=escolher_imagem, text='Escolher Imagem', bg=co6, fg=co1, font=('Arial', 10), width=15)
b_escolher.place(x=20, y=600)

b_converter = Button(janela, text='Converter', background=co2, fg=co1, font=('Arial', 10), width=15, command=converter_imagem)
b_converter.place(x=160, y=600)

b_salvar = Button(janela, command=salvar_imagem_convertida, text='Salvar Imagem', background=co5, fg=co1, font=('Arial', 10), width=15)
b_salvar.place(x=300, y=600)

janela.mainloop()  # serve para abrir a tela e mantê-la ativa