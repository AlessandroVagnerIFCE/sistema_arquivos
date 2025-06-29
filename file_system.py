#Classe do sistema de arquivos
#Encapsula todo o funcionamento interno do sistema de arquivos e suas funções básicas
#TODO: Adicionar funções copiar, mover, renomear
#IMPORTANTE: Falta adaptar para ficar de acordo com o que o professor pediu, esse é só o funcionamento base do sistema

from file_class import FFile

class FileSystem:
    def __init__(self, name="FileSystem"):
        self.name = name
        self.root = FFile("root", "DIR", [])
        self.cwd = self.root
        self.root.path = "/root"
        self.root.parent = None
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