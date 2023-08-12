import argparse 

class Image: 

    def __init__(self, args):

        #----------------------
        # Atributos do parser
        #-----------------------

        self._imgpath = args.imgpath
        self._op = args.op
        self._param = args.param[0]
        self._param_value = args.param[1]
        self._outputpath = args.outputpath

        #----------------------
        # Atributos da imagem
        #-----------------------

        self._magic_number= None    
        self._width = None
        self._height = None
        self._maxval = None
        self._mean = None
        self._median = None
        self._pixel_matrix = None
        self._threshold_value  = None
        self._threshold_optimal = None
        self._output_matrix= None


    #----------------------
    # Métodos de acesso 
    #-----------------------

    @property
    def get_shape(self):    
        return (self._width, self._height)
    
    @property
    def get_maxval(self): 
        return self._maxval
    
    @property
    def get_threshold_optimal(self):
        return self._threshold_optimal
    
    @property
    def get_magic_number(self):
        return self._magic_number
    
    @property
    def get_mean(self):
        return self._mean
    
    @property
    def get_median(self):
        return self._median
    

    #----------------------
    # Leitura imagem 
    #-----------------------
    
    def _read_img(self):

        with open(self._imgpath, 'r', encoding='utf-8') as f:

            complete_file = [line for line in f.readlines() if not line.startswith('#')]
            self._magic_number = complete_file[0]
            self._width, self._height  = map(int, complete_file[1].split())
            self._maxval = (complete_file[2])
            self._pixel_matrix = [[int(pixel) for pixel in line.split()] for line in complete_file[3:]]
            
        return self._magic_number, self._width, self._height, self._maxval, self._pixel_matrix


    #------------------------------
    #
    # Implementação do thresholding
    #
    #-------------------------------

    def thresholding(self, t=127):

        t = int(self._param_value)
        output_thresholding = [[255 if pixel > t else 0 for pixel in linha] for linha in self._pixel_matrix]

        self._output_matrix  = output_thresholding
        self._maxval = self._calculate_max_value(output_thresholding)
        return  self._output_matrix, self._maxval


    #------------------------------
    #
    # Implementação do sgt
    #
    #-------------------------------

    def sgt(self, dt=1):

        dt = int(self._param_value)
        t_0 = self._average(self._pixel_matrix)
        new_t = 0

        while abs(t_0 - new_t) > dt: 
            
            G1, G2 = self._segment_image(t_0, self._pixel_matrix)

            m1 = self._average(G1)
            m2 = self._average(G2)

            t_0 = new_t 

            new_t = int((m1 + m2) / 2)  

        self._output_matrix = self.thresholding(t=new_t)
        self._threshold_optimal = new_t
        self._maxval = self._calculate_max_value(self._output_matrix)
        self._median = self._median_value(self._output_matrix)
        self._mean = self._average(self._output_matrix)
        return self._output_matrix, self._maxval
    
        

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
        max_value = float('-inf')

        for linha in matriz:
            if isinstance(linha, list):
                for valor in linha:
                    if isinstance(valor, list):
                        valor = valor[0]
                    if valor > max_value:
                        max_value = valor
            else:
                if linha > max_value:
                    max_value = linha

        return max_value

    #---------------------------------
    #
    # Implementação do Filtro da Média
    #
    #----------------------------------

    def mean(self, k=3): 
        k = int(k)
        radius= k // 2
        # Create extended matrix with appropriate border size
        output_matrix = [[0] * self._width for _ in range(self._height)]

        # Create extended matrix with appropriate border size
        extended_matrix = [[0] * (self._width + 2 * radius) for _ in range(self._height + 2 * radius)]
        for i in range(self._height):
            for j in range(self._width):
                extended_matrix[i + radius][j + radius] = self._pixel_matrix[i][j]

        # Copy border pixels to extended matrix
        for i in range(radius):
            for j in range(self._width):
                extended_matrix[i][j + radius] = self._pixel_matrix[0][j]
                extended_matrix[self._height + radius+ i][j + radius] = self._pixel_matrix[self._height - 1][j]
        for i in range(self._height + 2 * radius):
            for j in range(radius):
                extended_matrix[i][j] = extended_matrix[i][radius]
                extended_matrix[i][self._width + radius+ j] = extended_matrix[i][self._width + radius- 1]

        for i in range(self._height):
            for j in range(self._width):
                total = 0
                count = 0
                for z in range(k):
                    for m in range(k):
                        total += extended_matrix[i + z][j + m]
                        count += 1
                output_matrix[i][j] = total // count  # Calculate the mean of all values in the window
        self._output_matrix = output_matrix
        self._maxval = self._calculate_max_value(output_matrix)
        return self._output_matrix


    #-----------------------------------
    #
    # Implementação do Filtro da Mediana
    #
    #------------------------------------

    def median(self, k=3):
        k = int(k)
        radius = k // 2
        # matriz inicializada com o mesmo tamanho da imagem original
        output_matrix = [[0] * self._width for _ in range(self._height)]

        # matriz extendida com as bordas 
        extended_matrix = [[0] * (self._width + 2 * radius) for _ in range(self._height + 2 * radius)]
        for i in range(self._height):
            for j in range(self._width):
                extended_matrix[i + radius][j + radius] = self._pixel_matrix[i][j]

        # pixels da borda superior e inferior 
        #itera nas linhas 
        for i in range(radius):
            # itera nas colunas
            for j in range(self._width):
                # adiciona os valores originais nas posições ajustadas na matriz extendida
                extended_matrix[i][j + radius] = self._pixel_matrix[0][j]
                # valores da ultima linha da matriz 
                extended_matrix[self._height + radius + i][j + radius] = self._pixel_matrix[self._height - 1][j]
        
        # pixels da borda esquerda e direita
        for i in range(self._height + 2 * radius):
            for j in range(radius):
                extended_matrix[i][j] = extended_matrix[i][radius]
                extended_matrix[i][self._width + radius + j] = extended_matrix[i][self._width + radius - 1]

        for i in range(self._height):
            for j in range(self._width):
                auxiliar = []
                for z in range(k):
                    for m in range(k):
                        auxiliar.append(extended_matrix[i + z][j + m])
                auxiliar.sort()
                output_matrix[i][j] = auxiliar[(len(auxiliar) - 1) // 2] 
        self._output_matrix = output_matrix
        self._maxval = self._calculate_max_value(output_matrix)
        return self._output_matrix
    


    #----------------------
    # Salvar imagem 
    #-----------------------

    def save_image(self):

        # informações do filename
        point_position = self._imgpath.rfind('.')
        bar_position = self._imgpath.rfind('/')
        img_type = "." + self._imgpath.split(".")[-1]
        img_name = self._imgpath[bar_position + 1: point_position]
        new_img_name = img_name + '_' + self._op + '_' + self._param + str(self._param_value) + img_type

        output_filepath = self._outputpath + '/' + new_img_name

        try:
            with open(output_filepath, "w") as file:
                
                # infos
                file.write(str(self._magic_number))
                file.write(f'{self._width} {self._height}\n')
                file.write(str(self._maxval)+'\n')

                # matrix values
                for linha in self._output_matrix:
                    line_str = " ".join(map(str, linha))
                    file.write(line_str+'\n')
        except:
            print('Erro ao salvar a imagem')



def check_arguments(args):
    """
    Tem como objetivo verificar a passagem de parametros.
    Retorna True ou False.
    """

    state = None 

    if args.op == 'thresholding' and args.param[0] == 't': 
        state = True
    elif args.op == 'sgt' and args.param[0] == 'dt': 
        state = True
    elif args.op == 'mean' and args.param[0] == 'k': 
        state = True
    elif args.op == 'median' and args.param[0] == 'k': 
        state = True

    return state 


def print_infos(args, obj): 
    """
    Tem como objetivo printar as informações necessárias ao solicitar a operação sgt.
    """

    print(f'magic_number {obj.get_magic_number}')
    print(f'dimensions {obj.get_shape}')
    print(f'maxval {obj.get_maxval}')
    #print(f'mean {obj.get_mean}')
    print(f'median {obj.get_median}')
    print(f'T {obj.get_threshold_optimal}')


def main():

    parser=argparse.ArgumentParser()
  

    parser.add_argument('--imgpath', action='store',dest='imgpath', type=str, help='Caminho da imagem de entrada', required=True)
    parser.add_argument('--op', action='store', dest='op', type=str,  choices=['thresholding', 'sgt', 'mean', 'median'], help='Operação a ser executada', required=True)
    parser.add_argument('--param', action='store', nargs='+', help='Parâmetro da operação.')
    parser.add_argument('--outputpath', action='store', dest='outputpath', type=str, help='Diretório para salvar as imagens resultantes', required=True)

    args = parser.parse_args()



    if (not check_arguments(args)):
        print('O parâmetro não corresponde com a operação solicitada.')
        exit()

    if check_arguments(args):
        param = args.param[0]
        param_value = args.param[1]

    image = Image(args)

    if args.op == 'thresholding':
        image._read_img()
        image.thresholding(param_value)
        image.save_image()

    elif args.op == 'sgt':
        image._read_img()
        image.sgt(param_value)
        print_infos(args, image)
        image.save_image()

    elif args.op == 'mean':
        image._read_img() 
        image.mean(param_value)
        image.save_image()

    elif args.op == 'median':
        image._read_img()
        image.median(param_value)
        image.save_image()
    
if __name__ == '__main__':
    main()
