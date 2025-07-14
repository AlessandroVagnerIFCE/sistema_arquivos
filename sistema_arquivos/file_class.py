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

class Inode:
    """
    Representa o i-node de um arquivo ou diretório, armazenando metadados.
    """
    def __init__(self, name: str, ftype: str):
        self.name = name
        self.type = ftype        # 'DIR' ou 'TEXT' ou 'EXEC'
        self.size = 0            # em bytes (ou caracteres simulados)
        self.block_indices = []  # lista de índices de blocos alocados
        self.head = None         # head do Block (lista encadeada)

class FFileEnc:
    def __init__(self, inode: Inode):
        self.inode = inode      # objeto Inode associado
        self.parent = None      # diretório pai
        self.path = None        # caminho completo

        # Copia os atributos do inode para manter sincronização inicial
        self.name = inode.name
        self.type = inode.type

    def read(self):
        # leitura de diretório ou conteúdo encadeado
        if self.type == 'DIR':
            for entry in self.inode.dir_entries:
                print(f"{entry.type} - {entry.name}")
            print("Fim do diretório")
        else:
            # chamamos o método de instância _read_chain
            text = self.parent.fs._read_chain(self.inode.head)
            if self.type == 'TEXT':
                print(text)
            elif self.type == 'EXEC':
                print(f"Executando {self.name}...")
                print(f"{self.name} executado!")