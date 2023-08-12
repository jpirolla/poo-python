import argparse 

class Image:
    def __init__(self,numero_magico, maxval,dim,pixels):
        self._magic_number = numero_magico
        self._dim = dim
        self._num_linhas = int(dim[1])
        self._num_colunas =int(dim[0])
        self._maxval = maxval
        self._pixel_matrix = pixels
        self._hist = None
        #self._dt = args.dt
        

    #----------------------
    # Métodos de acesso 
    #-----------------------

    def get_info(self):
      return (self._magic_number, self._dim, self._maxval, self._pixel_matrix, self._hist)
    
    @property
    def shape(self):    
        return (self._width, self._height)
    
    @property
    def maxval(self): 
        return self._maxval

    @property
    def threshold_optimal(self):
        return self._threshold_optimal
    
    @property
    def numero_magico(self):
        return self._magic_number
    
    @property
    def media(self):
        return self._mean
    
    @property
    def mediana(self):
        return self._median

    #----------------------
    # Construção histograma
    #-----------------------

    def _histograma(self):
        lista_aux=[]   # Lista auxiliar para armazenar todos os pixels da imagem

        for i in range(self._num_linhas):
            for j in range(self._num_colunas):
                lista_aux.append(self._pixel_matrix[i][j])

        p = list(set(lista_aux))  # Remove duplicatas para obter a lista de valores únicos
        self._hist = [0 for i in range(256)]

        for i in p:
            a = 0  # Contador para o valor atual de pixel

            for k in lista_aux:
                if i == k:
                    a += 1 # Incrementa o contador se o pixel atual for igual ao valor atual

            self._hist.insert(i,a)  # Insere a contagem na posição correspondente ao valor de pixel
        return self._hist # retorna o histograma


    #------------------------------
    #
    # Implementação do thresholding
    #
    #-------------------------------

    def thresholding(self, t=127):
        """
        Aplica a técnica de thresholding na imagem atual, transformando os pixels em preto ou branco
        com base em um valor de limiar.

        Args:
            t (int): O valor de limiar para a técnica de thresholding. Pixels maiores que o limiar serão
                    definidos como branco (255), e pixels menores ou iguais ao limiar serão definidos como
                    preto (0). O valor padrão é 127.

        Returns:
            Image: Uma nova instância da classe Image contendo a imagem resultante após a aplicação do thresholding.
                A nova imagem possui o mesmo número mágico, valor máximo, dimensões e matriz de pixels da imagem original.

        """

        self._pixel_matrix = [[255 if pixel > t else 0 for pixel in row] for row in self._pixel_matrix]
        self._maxval = 255 if self._maxval == 255 else 0

        return Image(self._magic_number, self._maxval,self._dim, self._pixel_matrix)

    #------------------------------
    #
    # Implementação do sgt
    #
    #-------------------------------

    def sgt(self, dt=1):
        """
        Aplica o algoritmo SGT na imagem atual, dividindo-a em regiões
        com base na diferença média entre os valores de intensidade dos pixels.

        Args:
            dt (int): O valor de diferença média máxima permitida para a parada do algoritmo. Se a diferença média
                    entre iterações consecutivas for menor ou igual a dt, o algoritmo para. O valor padrão é 1.

        Returns:
            Image: Uma nova instância da classe Image contendo a imagem resultante após a aplicação do algoritmo SGT.
                A nova imagem possui o mesmo número mágico, valor máximo, dimensões e matriz de pixels da imagem original.

        """
        dt = int(dt)
        t_0 = self._average(self._pixel_matrix)
        new_t = 0

        while abs(t_0 - new_t) > dt: 
            
            G1, G2 = self._segment_image(t_0, self._pixel_matrix)

            m1 = self._average(G1)
            m2 = self._average(G2)

            t_0 = new_t 

            new_t = int((m1 + m2) / 2)  

        output_matrix = self.thresholding(t=new_t)
        self._maxval = self._calculate_max_value(self._output_matrix)
        self._median = self._median_value(self._output_matrix)
        self._mean = self._average(self._output_matrix)
    

        return Image(self._magic_number, self._maxval, self._dim, output_matrix.get_info()[3])

    

    def _segment_image(self, T, matriz):

        G1 = [[pixel for pixel in linha if pixel > T] for linha in matriz]
        G2 = [[pixel for pixel in linha if pixel <= T] for linha in matriz]

        return G1, G2
    
    def _average(self, matriz): 
        soma_pixels = 0
        qtd_pixels = 0

        for linha in matriz:
            for valor in linha:
                soma_pixels += valor
                qtd_pixels += 1

        if qtd_pixels > 0:
            media = int(soma_pixels / qtd_pixels)
        else:
            media = 0 

        return media
         
    def _median_value(self, matriz): 
        elements = []

        for row in range(self._height): 
            for col in range(self._width):
                elements.append(matriz[row][col])

        sorted_elements = sorted(elements)
        num_elements = len(elements)

        median = 0 

        if num_elements % 2 == 0: 
            idx1 = num_elements // 2
            idx2 = idx1 - 1
            median = (sorted_elements[idx1] + sorted_elements[idx2]) / 2
        else: 
            median = sorted_elements[num_elements // 2]

        return int(median)

    def _calculate_max_value(self, matriz):
        max_val=0
        for i in matriz:
            if i>max_val:
                max_val=i
        return max_val
    
    #---------------------------------
    #
    # Implementação do Filtro da Média
    #
    #----------------------------------

    def mean(self, k=3): 
        """
        Calcula a média dos pixels em uma vizinhança de tamanho k e retorna uma nova imagem com os valores médios.

        Args:
            k (int): Tamanho da vizinhança.

        Returns:
            Image: Nova imagem com os valores médios dos pixels.
        """

        # Completando as bordas com 0
        pixels_viz = self._adiciona_zeros(self._pixel_matrix, k)

        # Separando a vizinhança de cada pixel
        meus_vizinhos = self._vizinhanca(pixels_viz, k)

        media_pixels = []  # Matriz com os valores médios dos pixels

        for matriz in meus_vizinhos:
            soma = 0
            tamanho = 0
            for linha in matriz:
                soma += sum(linha)
                tamanho += len(linha)
            valor_medio = int(soma / tamanho)
            media_pixels.append(valor_medio)

        print(self._calculate_max_value(media_pixels))

        self._maxval = self._calculate_max_value(media_pixels)

        matriz_pixels = []
        a = 0
        b = self._num_colunas
        for i in range(self._num_linhas):
            matriz_pixels.append(media_pixels[a:b])
            a += self._num_colunas
            b += self._num_colunas

        return Image(self._magic_number, self._maxval, self._dim, matriz_pixels)


    def _adiciona_zeros(self, matriz_pixels, k):
        # modificações que fiz
            # coloquei nomes que são mais intuitivos de ver o que ta acontecendo 
            # fiz com que retornasse uma nova matriz com os zeros ao invés de mudar a matriz original
            # coloquei uma docstring pra ajudar na documentação do código  
        """
        Adiciona zeros nas bordas da matriz P.

        Args:
            matriz_pixels (list): Matriz original com os valores de pixels
            k (int): Número de zeros a serem adicionados nas bordas.

        Returns:
            matriz_preenchida (list): Matriz cópia da original   com zeros adicionados nas bordas.
        """
      
        num_col_add = k//2  # num de linhas e colunas adicionais
        matriz_preenchida = matriz_pixels.copy()

        # preenchendo col laterais
        for i in range(self._num_linhas):
            for j in range(num_col_add):
                matriz_preenchida[i].insert(0,0)
                matriz_preenchida[i].append(0)

        # preenchendo linhas superiores e inferiores
        for i in range(num_col_add):
            lista_aux =[]
            for j in range(self._num_colunas+2):
                lista_aux.append(0)

                matriz_preenchida.insert(0, lista_aux)
                matriz_preenchida.append(lista_aux)

        return matriz_preenchida 



    def _vizinhanca(self, matriz_extendida, k):
        """
        Retorna a vizinhança de cada elemento da matriz P.

        Args:
            matriz_extendida (list): Matriz com as bordas preenchidas.
            k (int): Tamanho da vizinhança.

        Yields:
            list: Vizinhança de um elemento de P por vez.
        """
        for linha in range(self._num_linhas):
            for coluna in range(self._num_colunas):
                vizinhanca = [
                    matriz_extendida[linha + i][coluna:coluna + k]
                    for i in range(k)]
                yield vizinhanca


    #-----------------------------------
    #
    # Implementação do Filtro da Mediana
    #
    #------------------------------------


    def median(self, k=3):
        """
        Calcula a mediana dos pixels em uma vizinhança de tamanho k e retorna uma nova instância de Image
        com os valores medianos dos pixels.

        Args:
            k (int): Tamanho da vizinhança.

        Returns:
            Image: Nova instância de Image com os valores medianos dos pixels.
        """

        # Completando as bordas com 0
        pixels_viz = self._adiciona_zeros(self._pixel_matrix, k)

        # Separando a vizinhança de cada pixel
        meus_vizinhos = self._vizinhanca(pixels_viz, k)

        mediana_pixels = []  # Lista para armazenar os valores medianos dos pixels

        for matriz in meus_vizinhos:
            lista_aux = []
            for linha in matriz:
                for valor in linha:
                    lista_aux.append(valor)

            sorted_lista = sorted(lista_aux)
            tamanho = len(sorted_lista)
            mediana = 0

            if tamanho % 2 == 0:
                n1 = tamanho // 2
                n2 = n1 - 1
                mediana = (sorted_lista[n1] + sorted_lista[n2]) / 2
            else:
                mediana = sorted_lista[tamanho // 2]

            mediana_pixels.append(mediana)

        matriz_pixels_mediana = []  # Matriz para armazenar os valores medianos dos pixels organizados em linhas
        
        a = 0
        b = self._num_colunas

        for i in range(self._num_linhas):
            matriz_pixels_mediana.append(mediana_pixels[a:b])
            a += self._num_colunas
            b += self._num_colunas

        self._maxval = self._calculate_max_value(mediana_pixels)

        return Image(self._magic_number, self._maxval, self._dim, matriz_pixels_mediana)

    #-----------------------------------
    #
    # Implementação do Filtro da Mediana
    #
    #------------------------------------

    def sobel(self, k, image): 

        k = int(k)

        kernel_x = [[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]]

        kernel_y = [[-1, -2, -1],
                    [0, 0, 0],
                    [1, 2, 1]]


         # Completa as bordas com 0
        pixels_viz_x = self._adiciona_zeros(image._pixel_matrix, k)
        pixels_viz_y = self._adiciona_zeros(image._pixel_matrix, k)


        # Aplica a convolução com os kernels de Sobel
        gradient_x = self._convolucao(pixels_viz_x, kernel_x)
        gradient_y = self._convolucao(pixels_viz_y, kernel_y)

        # Calcula o gradiente de intensidade
        gradient_intensity = self._calcular_gradiente_intensidade(gradient_x, gradient_y)

        return gradient_intensity
    

    def _convolucao(self, image, k):
        k = int(k)

        # Define a matriz resultante da convolução
        conv_result = [[0] * (self._num_colunas - k + 1) for _ in range(self._num_linhas - k + 1)]

        # Aplica a convolução
        for i in range(self._num_linhas - k + 1):
            for j in range(self._num_colunas - k + 1):
                for m in range(k):
                    for n in range(k):
                        conv_result[i][j] += image[i + m][j + n] * k[m][n]

        return conv_result


    def _calcular_gradiente_intensidade(self, gradient_x, gradient_y):


        gradient_intensity = [[0] * self._num_colunas for _ in range(self._num_linhas)]

        for i in range(self._num_linhas):
            for j in range(self._num_colunas):
                intensity = (gradient_x[i][j] ** 2 + gradient_y[i][j] ** 2) ** 0.5
                gradient_intensity[i][j] = int(intensity)

        return gradient_intensity
           




def obter_dados():
    #----------------------
    # Implementação do parse
    #-----------------------
    parser=argparse.ArgumentParser(description="Entradas")
    parser.add_argument('--imgpath',action='store',dest='imgpath',required=True)
    parser.add_argument('--op',action='store',dest='op',required=True)
    parser.add_argument('--dt',action='store',dest='dt',required=False,default=1)
    parser.add_argument('--t',action='store',dest='t',required=False,default=127)
    parser.add_argument('--k',action='store',dest='k',required=False,default=3)
    parser.add_argument('--outputpath',action='store',dest='outputpath',required=False)

    args = parser.parse_args()


    return (args.imgpath, args.op, args.t, args.dt, args.k,args.outputpath)



def ler_arquivo(caminho):
    """
    Lê um arquivo no formato PGM e retorna informações sobre a imagem.

    Args:
        caminho (str): O caminho do arquivo a ser lido.

    Returns:
        tuple: Uma tupla contendo informações sobre a imagem lida.
               A tupla é composta pelos seguintes elementos:
               - numero_magico (str): O número mágico do arquivo PGM.
               - max_val (str): O valor máximo permitido para os pixels da imagem.
               - dim (list): As dimensões da imagem [num_colunas, num_linhas].
               - pixels_int (list): Uma lista de listas representando os pixels da imagem,
                                    onde cada valor é um pixel da imagem em formato inteiro.

    """

    with open(caminho,'r') as f:
        linhas_arquivo = f.readlines()
        numero_magico = linhas_arquivo[0] #numero magico
        max_val = linhas_arquivo[2] #maximo valor
        dim = linhas_arquivo[1].split()

        colunas = int(dim[0]) #num_colunas
        linhas = int(dim[1]) #num_linhas

        #Transformando os pixels em int
        pixels_int = [] #Lista de pixels em formato int

        for linha in linhas_arquivo[3:linhas+3]:
            pixels_linha = linha.split()
            linha_int = [int(pixel) for pixel in pixels_linha]
            pixels_int.append(linha_int)


    return (numero_magico,max_val,dim,pixels_int)



def nome_do_arquivo(nome_arquivo, op, param, valor):
  """
    Cria o nome do arquivo de saída com base nos parâmetros fornecidos.

    Args:
        nome_arquivo (str): O nome do arquivo original.
        op (str): A operação realizada no arquivo.
        param (str): O parâmetro utilizado na operação.
        valor (str): O valor do parâmetro.

    Returns:
        str: O nome do arquivo de saída no formato "nome_original_op_paramvalor.pgm".

    """
  dados_arquivo = obter_dados()
  partes_nome = nome_arquivo.split(".")
  nome = f'{partes_nome[0]}_{op}_{param}{valor}.pgm'

  try:
    output = dados_arquivo[5] + "/" + nome
    return output
  except:
    return nome


def escrever_arquivo(nome_arquivo, lista_dados):
    """
    Escreve os dados fornecidos em um arquivo de saída.

    Args:
        nome_arquivo (str): O nome do arquivo de saída.
        lista_dados (tuple): Uma tupla contendo os dados a serem escritos no arquivo.
                             A tupla deve estar na seguinte ordem:
                             - numero_magico (str): O número mágico do arquivo PGM.
                             - dim (list): As dimensões da imagem [num_colunas, num_linhas].
                             - max_val (str): O valor máximo permitido para os pixels da imagem.
                             - pixels_int (list): Uma lista de listas representando os pixels da imagem,
                                                  onde cada valor é um pixel da imagem em formato inteiro.

    Returns:
        arquivo: O arquivo de saída aberto no modo de escrita.

    """
    with open(nome_arquivo, 'w') as arquivo:
        arquivo.writelines([lista_dados[0], str(lista_dados[1][0]), " ", str(lista_dados[1][1]), "\n", str(lista_dados[2])])
        colunas, linhas = lista_dados[1]
        colunas, linhas = int(colunas), int(linhas)
        for i in range(linhas):
            arquivo.write("\n")
            for j in range(colunas):
                arquivo.write(str(lista_dados[3][i][j]))
                arquivo.write(" ")

    return arquivo

def main():
    imgpath, op, t, dt, k, outputpath = obter_dados()
    parametros = ler_arquivo(imgpath)
    imagem = Image(parametros[0], parametros[1], parametros[2], parametros[3])

    try:
        if op == "thresholding":
            resultado = imagem.thresholding(int(t))
            nome = nome_do_arquivo(imgpath, op, "t", outputpath)
            escrever_arquivo(nome, resultado.get_info())

        elif op == "sgt":
            resultado = imagem.sgt(int(dt))
            nome = nome_do_arquivo(imgpath, op, "dt", outputpath)
            escrever_arquivo(nome, resultado.get_info())

        elif op == "mean":
            resultado = imagem.mean(int(k))
            nome = nome_do_arquivo(imgpath, op, "k", outputpath)
            escrever_arquivo(nome, resultado.get_info())

        elif op == "median":
            resultado = imagem.median(int(k))
            nome = nome_do_arquivo(imgpath, op, "k", outputpath)
            escrever_arquivo(nome, resultado.get_info())

        else:
            raise Exception("Invalid parameters")

    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
