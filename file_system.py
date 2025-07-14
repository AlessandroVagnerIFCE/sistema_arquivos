#Classe do sistema de arquivos
#Encapsula todo o funcionamento interno do sistema de arquivos e suas funções básicas
#TODO: Adaptar para funcionar com inodes e lista encadeada (para ficar de acordo com o que o professor pediu)
#IMPORTANTE: Falta adaptar para ficar de acordo com o que o professor pediu, esse é só o funcionamento base do sistema
#IMPORTANTE: Para navegar pelo sistema de arquivos, é necessário entrar manualmente nos diretórios, já que um comando "cd" depende dessas adaptações
#IMPORTANTE: Também não adicionei data de criação/modificação de arquivos

from file_class import FFile, Inode
import math

# parâmetros do FS simulado
BLOCK_SIZE = 4       # caracteres por bloco
TOTAL_BLOCKS = 100
INODE_SIZE = 2 #Cada inode pode referenciar dois blocos
TOTAL_INODES = 20

class Block:
    def __init__(self, index):
        self.index = index
        self.data = ''

class FileSystem:
    def __init__(self, name="FileSystem"):
        self.name = name
        self.free_blocks = []
        self.blocks = []
        self.inodes = []
        for i in range(TOTAL_BLOCKS):
            bloco = Block(i)
            self.free_blocks.append(i)
            self.blocks.append(bloco)
        for j in range(TOTAL_INODES):
            novo_inode = Inode("INODE LIVRE", "INODE LIVRE")
            self.inodes.append(novo_inode)
        #self.root = Inode("root", "DIR")
        self.cwd = None
        self.root = self.newFile("root", "DIR")
        self.cwd = self.root
        self.root.path = "/root"
        self.root.parent = None
        self.copyBuffer = None
        print("Sistema de arquivos " + self.name + " inicializado com sucesso")
        self.pwd()

    #Aloca um inode para um arquivo
    def __alocar_inode__(self, filename: str, ftype: str):
        for i in self.inodes:
            if (i.name == "INODE LIVRE"):
                i.name = filename
                i.type = ftype
                return i
        return None
    
    #Aloca blocos para um inode
    def __alocar_blocos__(self, inode: Inode, quantidade: int):
        #Encadear Inodes
        if (quantidade > INODE_SIZE):
            novo_inode = self.__alocar_inode__(inode.name, inode.type)
            if (novo_inode == None):
                return False
            inode.next = novo_inode
            self.__alocar_blocos__(novo_inode, quantidade - INODE_SIZE)
        #Alocar blocos
        if (quantidade > len(self.free_blocks)):
            print("Não há blocos disponíveis")
            return False
        for i in range(quantidade):
            indice = self.free_blocks.pop()
            inode.block_indices.append(indice)
        inode.size = len(inode.block_indices)*BLOCK_SIZE
        return True
    
    #Escreve um texto nos blocos associados a um inode
    def __escrever_dados__(self, inode: Inode, data: str):
        if (data == ""):
            return False
        tamanho = len(data)
        quantidade_blocos = math.ceil(tamanho/BLOCK_SIZE)
        if (self.__alocar_blocos__(inode, quantidade_blocos)):
            start = 0
            end = BLOCK_SIZE
            if (end > tamanho):
                end = tamanho
            for i in inode.block_indices:
                dados = []
                for j in range(start, end):
                    dados.append(data[j])
                start = start + BLOCK_SIZE
                end = end + BLOCK_SIZE
                if (end > tamanho):
                    end = tamanho
                #if (i is Block):
                    #i = i.index
                self.blocks[i].data = dados
            if (inode.next != None):
                self.__escrever_dados__(inode.next, data[end:])
            return True
        return False
    
    #Libera um inode e todos os blocos associados a ele
    def __free_inode__(self, inode: Inode):
        if (inode.type == "DIR"):
            if (len(inode.block_indices) > 0):     
                for j in self.blocks[inode.block_indices[0]].data: #Alterar isso para considerar um diretório com tamanho limitado
                    self.__free_inode__(j)
        for i in inode.block_indices:
            self.__free_block__(self.blocks[i])
        inode.block_indices = []
        inode.name = "INODE LIVRE"
        inode.type = "INODE LIVRE"
        if (inode.next != None):
            self.__free_inode__(inode.next)
            inode.next = None
        inode.size = 0
        inode.parent = None
        self.printInodelist()
        #for k in self.inodes:
            #print(k.name)

    def __free_block__(self, block: Block):
        block.data = ''
        self.free_blocks.append(block.index)

    
    def __read_blocks__(self, inode: Inode):
        if (inode.type == "DIR"):
            for j in self.blocks[inode.block_indices[0]].data:
                print(j.type + " - " + j.name)
            print("Fim do diretório")
            return True
        for i in inode.block_indices:
            print((self.blocks[i]).data)
        return True
    
    def printInodelist(self):
        for k in self.inodes:
            print(k.name)
    
    def printFreeBlocksList(self):
        for k in self.free_blocks:
            print(k)

    #Adiciona um novo arquivo e retorna o mesmo se a operação for concluída com sucesso
    #Retorna False se a operação falhar
    def newFile(self, fileName: str, type: str, data=None):
        if (self.cwd == None):
            file = self.__alocar_inode__(fileName, type)
            if (file == None):
                print("Não foi possível criar o diretório root")
                return False
            file.type = type
            bloco = self.__alocar_blocos__(file, 1)
            if (bloco):
                self.blocks[file.block_indices[0]].data = []
                return file
            return False
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == fileName):
                print("Já existe um arquivo com o mesmo nome nesse diretório")
                return False

        try:
            #file = FFile(fileName, type)
            file = self.__alocar_inode__(fileName, type)
            if (file == None):
                print("Não foi possível alocar um inode para o arquivo")
                return False
            file.type = type
            if (type == "DIR"): #Alocar um bloco para armazenar um diretório
                bloco = self.__alocar_blocos__(file, 1)
                if (bloco):
                    self.blocks[file.block_indices[0]].data = []
                else:
                    print("Falha ao criar o arquivo, não foi possível alocar um bloco")
                    return False
            elif (data != None):
                self.__escrever_dados__(file, data)
                #file.data = data

            #OBS: Falta limitar o tamanho do diretório, alocando mais blocos quando necessário
            self.blocks[self.cwd.block_indices[0]].data.append(file) #Adicionar o novo arquivo ao diretório atual
            file.parent = self.cwd
            file.path = self.cwd.path + "/" + fileName #Caminho do arquivo

            return file
        except:
            print("Ocorreu um erro desconhecido")
            return False

    #Remove um arquivo
    #Se o arquivo for do tipo DIR, então todos os arquivos dentro dele serão deletados pelo coletor de lixo    
    def removeFile(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == fileName):
                self.__free_inode__(i)
                self.blocks[self.cwd.block_indices[0]].data.remove(i) #Remover do diretório atual
                print(fileName + " removido com sucesso")
                return True
        print("Arquivo não encontrado")
        return False
            
    #Lista todos os arquivos no diretório atual
    #Análogo ao comando ls no terminal
    def ls(self):
        self.__read_blocks__(self.cwd)
        #self.cwd.read()

    #Abre um arquivo
    #Se for um diretório, entra nele
    def openFile(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == fileName):
                if (i.type == "DIR"):
                    self.cwd = i
                    self.pwd()
                self.__read_blocks__(i)
                #i.read()
                return True
        print("Arquivo não encontrado")
        return False

    #Muda o diretório atual para o diretório pai
    #Retorna False se não for possível        
    def goUpwards(self):
        if (self.cwd.parent != None):
            self.cwd = self.cwd.parent
            self.pwd()
            return True
        print("Não existe diretório acima do diretório atual")
        return False
    
    #Imprime o caminho do diretório atual
    #Análogo ao comando cwd no terminal
    def pwd(self):
        print(self.cwd.path)

    #Altera o nome de um arquivo e atualiza o caminho do mesmo
    #Retorna False se a operação falhar
    def renameFile(self, fileName: str, newName: str):
        #Verificar se o novo nome já está sendo usado
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == newName):
                print("Já existe um arquivo com o mesmo nome nesse diretório")
                return False

        #Procurar o arquivo alvo e renomear    
        for j in self.blocks[self.cwd.block_indices[0]].data:
            if (j.name == fileName):
                j.name = newName
                j.path = self.cwd.path + "/" + newName #Caminho do arquivo
                if (j.type == "DIR"):
                    for v in self.blocks[j.block_indices[0]].data:
                        self.__updateCopyPath__(v, j)
                print(fileName + " renomeado para " + newName)
                return True
            
        print("Arquivo não encontrado")
        return False

    #Cria uma cópia de um arquivo e armazena essa cópia em um buffer
    #Retorna False se a operação falhar
    def copyFile(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == fileName):
                cp = FFile(fileName, i.type)
                if (i.type == "DIR"):
                    cp.data = []
                    for j in i.data:
                        cp.data.append(self.__copyAux__(j, cp))
                else:
                    cp.data = i.data
                
                self.copyBuffer = cp
                return cp
            
        print("Arquivo não encontrado")
        return False
    
    def __copyAux__(self, file: FFile, parent: FFile):
        cp = FFile(file.name, file.type)
        if (file.type == "DIR"):
            cp.data = []
            for i in file.data:
                cp.data.append(self.__copyAux__(i, cp))
        else:
            cp.data = file.data

        cp.parent = parent
        return cp
    
    #Adiciona o arquivo armazenado no buffer de cópia ao diretório atual
    #Retorna False se a operação falhar
    def pasteFile(self):
        if (self.copyBuffer == None):
            print("Nenhum arquivo foi copiado para a área de transferência")
            return False
        cp = self.copyBuffer
        
        #Verificar se o nome do arquivo já está sendo usado
        dupeCounter = 0
        pasteFlag = self.__checkDuplicateNames__(cp.name)

        while(pasteFlag == True):
            dupeCounter += 1
            pasteFlag = self.__checkDuplicateNames__(cp.name + "(" + str(dupeCounter) + ")")

        if (dupeCounter > 0):
            cp.name = cp.name + "(" + str(dupeCounter) + ")"
        
        #Adicionar a cópia ao diretório atual
        file = self.__alocar_inode__(cp.name, cp.type)
        if (file == None):
            return False
        if (file.type == "DIR"):
            bloco = self.__alocar_blocos__(file, 1)
            if (bloco):
                for i in cp.data:
                    self.blocks[file.blocks_indices[0]].data.append(i)
        self.__escrever_dados__(file, cp.data)
        file.parent = self.cwd
        file.path = self.cwd.path + "/" + file.name
        self.blocks[self.cwd.block_indices[0]].data.append(file)
        cp.parent = self.cwd
        cp.path = self.cwd.path + "/" + cp.name #Caminho do arquivo

        #Caso seja um diretório, atualizar o caminho de todos os sub-arquivos da cópia
        if (file.type == "DIR"):
            for i in self.blocks[file.blocks_indices[0]].data:
                self.__updateCopyPath__(i, file)
        
        self.copyBuffer = None

    def __checkDuplicateNames__(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == fileName):
                return True
        return False
    
    def __updateCopyPath__(self, file: Inode, parent: Inode):
        file.path = parent.path + "/" + file.name
        if (file.type == "DIR"):
            for i in self.blocks[file.block_indices[0]].data:
                self.__updateCopyPath__(i, file)

    #Imprime o caminho de um arquivo
    def printFilePath(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if (i.name == fileName):
                print(i.path)
                return True
            
        print("Não existe arquivo com o nome " + fileName + " no diretório atual")
        return False
    
    def readFile(self, fileName: str):
        """
        Alias para openFile, mantendo a interface de comparar_desempenho().
        """
        return self.openFile(fileName)

    def writeFile(self, fileName: str, content: str):
        """
        Atualiza o conteúdo de um arquivo texto existente.
        """
        for entry in self.blocks[self.cwd.block_indices[0]].data:
            if entry.name == fileName and entry.type != "DIR":
                self.__escrever_dados__(entry, content)
                #entry.data = content
                print(f"Escrito em {fileName}: {len(content)} bytes")
                return True
        print("Arquivo não encontrado ou não é arquivo")
        return False    


    #Move um arquivo do diretório atual para o diretório alvo
    #Recebe o diretório alvo na forma de caminho
    #Retorna False se a operação falhar
    def moveFile(self, fileName: str, targetDir: str):
            for i in self.blocks[self.cwd.block_indices[0]].data:
                if (i.name == fileName):
                    caminho = targetDir.split("/")
                    current = self.root
                    caminho.pop(0)
                    for j in range(len(caminho)):
                        if (current.type != "DIR"):
                            print("Caminho inválido")
                            return False
                        for k in self.blocks[current.block_indices[0]].data:
                            if (k.name == caminho[j]):
                                current = k
                    if (current.path == targetDir):
                        #Verificar se há conflito de nomes
                        for l in self.blocks[current.block_indices[0]].data:
                            if (l.name == i.name):
                                print("==============")
                                print("Já existe arquivo com o nome " + i.name + " nesse diretório")
                                op_success = False
                                while(op_success == False):
                                    print("Escolha uma das opções abaixo (digite um número):")
                                    print("1- Substituir")
                                    print("2- Renomear")
                                    print("3- Cancelar a operação")
                                    try:
                                        op = int(input("Escolha uma operação valída: "))
                                        if (op == 1):
                                            self.blocks[current.block_indices[0]].data.remove(l)
                                            op_success = True
                                        elif (op == 2):
                                            newName = input("Insira o novo nome do arquivo: ")
                                            auxFlag = True
                                            for n in self.blocks[current.block_indices[0]].data:
                                                if (n.name == newName):
                                                    print("O nome escolhido já está em uso")
                                                    auxFlag = False
                                            if (auxFlag):
                                                i.name = newName
                                                op_success = True
                                        elif (op == 3):
                                            print("Operação cancelada")
                                            op_success = True
                                            return False
                                        else:
                                            print("Operação inválida")
                                    except:
                                        print("Você precisa escolher uma das operações válidas")
                                        print("==============")
                                        #return False
                        self.blocks[current.block_indices[0]].data.append(i)
                        i.parent = current
                        i.path = i.parent.path + "/" + i.name
                        self.blocks[self.cwd.block_indices[0]].data.remove(i)

                        #Se o arquivo movido for um diretório, atualizar o caminho de todos os sub-arquivos
                        if (i.type == "DIR"):
                            for v in self.blocks[i.block_indices[0]].data:
                                self.__updateCopyPath__(v, i)
                        print("Arquivo movido com sucesso")
                        return True
                    
            print("Arquivo não encontrado")
            return False