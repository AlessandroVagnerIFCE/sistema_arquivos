#Classe arquivo
#Essa classe guarda os atributos de um arquivo
#TODO: Adaptar para funcionar com inodes e lista encadeada (para ficar de acordo com o que o professor pediu)

class FFile:
    def __init__(self, name: str, type: str, data=None):
        self.name = name
        self.type = type
        self.data = data

    #def rename(self, newName):
        #self.name = newName

    def read(self):
        if (self.type == "DIR"):
            for i in self.data:
                print(i.type + " - " + i.name)
            print("Fim do diretório")
        elif (self.type == "TEXT"):
            print(self.data)
        elif (self.type == "EXEC"): #Apenas para simulação
            print("Executando " + self.name + "...")
            print(self.name + " executado!")