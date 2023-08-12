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


    def _read_img(self):

        with open(self._imgpath, 'r', encoding='utf-8') as f:

            complete_file = [line for line in f.readlines() if not line.startswith('#')]
            self._magic_number = complete_file[0]
            self._width, self._height  = map(int, complete_file[1].split())
            self._maxval = (complete_file[2])
            self._pixel_matrix = [[int(pixel) for pixel in line.split()] for line in complete_file[3:]]
            
        return self._magic_number, self._width, self._height, self._maxval, self._pixel_matrix



    def sobel_filter(self, k, matriz): 

        k = int(k)

        # Define the Sobel kernels
        kernel_x = [[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]]

        kernel_y = [[-1, -2, -1],
                    [0, 0, 0],
                    [1, 2, 1]]


        output_image = [[0] * self._width for _ in range(self._height)]

        
        padded_image = [[0] * (self._width + 2) for _ in range(self._height + 2)]
        for i in range(self._height):
            for j in range(self._width):
                padded_image[i+1][j+1] = matriz[i][j]


        for i in range(1, self._height + 1):
            for j in range(1, self._width + 1):

                gradient_x = 0
                for m in range(3):
                    for n in range(3):
                        gradient_x += kernel_x[m][n] * padded_image[i-1+m][j-1+n]


                gradient_y = 0
                for m in range(3):
                    for n in range(3):
                        gradient_y += kernel_y[m][n] * padded_image[i-1+m][j-1+n]

            
                output_image[i-1][j-1] = gradient_x, gradient_y

        return output_image


    def _normalizar_matriz(self, matriz):
        max_valor = self._calculate_max_value(matriz)

        matriz_normalizada = []
        for linha in matriz:
            linha_normalizada = []
            for elemento in linha:
                elemento_normalizado = round((elemento * 255) / (max_valor))
                linha_normalizada.append(elemento_normalizado)
            matriz_normalizada.append(linha_normalizada)

        return matriz_normalizada
    

    def _calculate_max_value(self, matriz):
        max_value = 0
        for linha in matriz: 
            for valor in linha: 
                if valor > max_value:
                        max_value = valor

        return max_value 

    def _padded_matrix(self, matriz): 
        pass



def check_arguments(args):

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
    parser.add_argument('--outputpath', action='store', dest='outputpath', type=str, help='Diretório para salvar as imagens resultantes')

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
