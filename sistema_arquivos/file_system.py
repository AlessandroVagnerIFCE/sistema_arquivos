#Classe do sistema de arquivos
#Encapsula todo o funcionamento interno do sistema de arquivos e suas funções básicas
#TODO: Adaptar para funcionar com inodes e lista encadeada (para ficar de acordo com o que o professor pediu)
#IMPORTANTE: Falta adaptar para ficar de acordo com o que o professor pediu, esse é só o funcionamento base do sistema
#IMPORTANTE: Para navegar pelo sistema de arquivos, é necessário entrar manualmente nos diretórios, já que um comando "cd" depende dessas adaptações
#IMPORTANTE: Também não adicionei data de criação/modificação de arquivos

from file_class import FFile

class FileSystem:
    def __init__(self, name="FileSystem"):
        self.name = name
        self.root = FFile("root", "DIR", [])
        self.cwd = self.root
        self.root.path = "/root"
        self.root.parent = None
        self.copyBuffer = None
        print("Sistema de arquivos " + self.name + " inicializado com sucesso")
        self.pwd()

    #Adiciona um novo arquivo e retorna o mesmo se a operação for concluída com sucesso
    #Retorna False se a operação falhar
    def newFile(self, fileName: str, type: str, data=None):
        for i in self.cwd.data:
            if (i.name == fileName):
                print("Já existe um arquivo com o mesmo nome nesse diretório")
                return False

        try:
            file = FFile(fileName, type)
            if (type == "DIR"):
                file.data = []
            elif (data != None):
                file.data = data

            self.cwd.data.append(file) #Adicionar o novo arquivo ao diretório atual
            file.parent = self.cwd
            file.path = self.cwd.path + "/" + fileName #Caminho do arquivo

            return file
        except:
            print("Ocorreu um erro desconhecido")
            return False

    #Remove um arquivo
    #Se o arquivo for do tipo DIR, então todos os arquivos dentro dele serão deletados pelo coletor de lixo    
    def removeFile(self, fileName: str):
        for i in self.cwd.data:
            if (i.name == fileName):
                self.cwd.data.remove(i) #Remover do diretório atual
                print(fileName + " removido com sucesso")
                return True
            
    #Lista todos os arquivos no diretório atual
    #Análogo ao comando ls no terminal
    def ls(self):
        self.cwd.read()

    #Abre um arquivo
    #Se for um diretório, entra nele
    def openFile(self, fileName: str):
        for i in self.cwd.data:
            if (i.name == fileName):
                if (i.type == "DIR"):
                    self.cwd = i
                    self.pwd()
                i.read()
                return True

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
        for i in self.cwd.data:
            if (i.name == newName):
                print("Já existe um arquivo com o mesmo nome nesse diretório")
                return False

        #Procurar o arquivo alvo e renomear    
        for j in self.cwd.data:
            if (j.name == fileName):
                j.name = newName
                j.path = self.cwd.path + "/" + newName #Caminho do arquivo
                if (j.type == "DIR"):
                    for v in j.data:
                        self.__updateCopyPath__(v, j)
                print(fileName + " renomeado para " + newName)
                return True
            
        print("Arquivo não encontrado")
        return False

    #Cria uma cópia de um arquivo e armazena essa cópia em um buffer
    #Retorna False se a operação falhar
    def copyFile(self, fileName: str):
        for i in self.cwd.data:
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
        self.cwd.data.append(cp)
        cp.parent = self.cwd
        cp.path = self.cwd.path + "/" + cp.name #Caminho do arquivo

        #Caso seja um diretório, atualizar o caminho de todos os sub-arquivos da cópia
        if (cp.type == "DIR"):
            for i in cp.data:
                self.__updateCopyPath__(i, cp)
        
        self.copyBuffer = None

    def __checkDuplicateNames__(self, fileName: str):
        for i in self.cwd.data:
            if (i.name == fileName):
                return True
        return False
    
    def __updateCopyPath__(self, file: FFile, parent: FFile):
        file.path = parent.path + "/" + file.name
        if (file.type == "DIR"):
            for i in file.data:
                self.__updateCopyPath__(i, file)

    #Imprime o caminho de um arquivo
    def printFilePath(self, fileName: str):
        for i in self.cwd.data:
            if (i.name == fileName):
                print(i.path)
                return True
            
        print("Não existe arquivo com o nome " + fileName + " no diretório atual")
        return False
    
    #Move um arquivo do diretório atual para o diretório alvo
    #Recebe o diretório alvo na forma de caminho
    #Retorna False se a operação falhar
    def moveFile(self, fileName: str, targetDir: str):
            for i in self.cwd.data:
                if (i.name == fileName):
                    caminho = targetDir.split("/")
                    current = self.root
                    caminho.pop(0)
                    for j in range(len(caminho)):
                        if (current.type != "DIR"):
                            print("Caminho inválido")
                            return False
                        for k in current.data:
                            if (k.name == caminho[j]):
                                current = k
                    if (current.path == targetDir):
                        #Verificar se há conflito de nomes
                        for l in current.data:
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
                                            current.data.remove(l)
                                            op_success = True
                                        elif (op == 2):
                                            newName = input("Insira o novo nome do arquivo: ")
                                            auxFlag = True
                                            for n in current.data:
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
                        current.data.append(i)
                        i.parent = current
                        i.path = i.parent.path + "/" + i.name
                        self.cwd.data.remove(i)

                        #Se o arquivo movido for um diretório, atualizar o caminho de todos os sub-arquivos
                        if (i.type == "DIR"):
                            for v in i.data:
                                self.__updateCopyPath__(v, i)
                        print("Arquivo movido com sucesso")
                        return True
                    
            print("Arquivo não encontrado")
            return False