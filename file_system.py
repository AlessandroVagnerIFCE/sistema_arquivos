from file_class import FFile, Inode
import math

# parâmetros do FS simulado
BLOCK_SIZE = 4  # caracteres por bloco
TOTAL_BLOCKS = 100
INODE_SIZE = 2  # Cada inode pode referenciar dois blocos
TOTAL_INODES = 20


class Block:
    def __init__(self, index):
        self.index = index
        self.data = ''


class FileSystem:
    def __init__(self, name="FileSystem"):
        self.name = name
        self.blocks = []
        self.block_bitmap = [0] * TOTAL_BLOCKS  # 0 = livre, 1 = ocupado
        self.inodes = []

        for i in range(TOTAL_BLOCKS):
            self.blocks.append(Block(i))

        for j in range(TOTAL_INODES):
            self.inodes.append(Inode("INODE LIVRE", "INODE LIVRE"))

        self.cwd = None
        self.root = self.newFile("root", "DIR")
        self.cwd = self.root
        self.root.path = "/root"
        self.root.parent = None
        self.copyBuffer = None
        print(f"Sistema de arquivos '{self.name}' inicializado com sucesso")
        self.pwd()

    # Busca o primeiro bloco livre no bitmap
    def __find_free_block__(self):
        for idx, bit in enumerate(self.block_bitmap):
            if bit == 0:
                return idx
        return -1

    # Marca um bloco como usado no bitmap
    def __mark_block_used__(self, block_index):
        self.block_bitmap[block_index] = 1
        print(f"[DEBUG] Bloco {block_index} marcado como USADO")

    # Marca um bloco como livre no bitmap
    def __mark_block_free__(self, block_index):
        self.block_bitmap[block_index] = 0
        print(f"[DEBUG] Bloco {block_index} marcado como LIVRE")

    # Aloca um inode para um arquivo
    def __alocar_inode__(self, filename: str, ftype: str):
        for i in self.inodes:
            if i.name == "INODE LIVRE":
                i.name = filename
                i.type = ftype
                print(f"[DEBUG] Inode alocado para '{filename}' do tipo '{ftype}'")
                return i
        print("[DEBUG] Falha: nenhum inode livre disponível")
        return None

    # Aloca blocos para um inode usando o bitmap
    def __alocar_blocos__(self, inode: Inode, quantidade: int):
        if quantidade > INODE_SIZE:
            novo_inode = self.__alocar_inode__(inode.name, inode.type)
            if novo_inode is None:
                print("[DEBUG] Falha ao alocar inode encadeado")
                return False
            inode.next = novo_inode
            print(f"[DEBUG] Criado inode encadeado: {novo_inode.name}")
            # Recursivamente aloca blocos para o novo inode
            if not self.__alocar_blocos__(novo_inode, quantidade - INODE_SIZE):
                return False

        blocos_livres = self.block_bitmap.count(0)
        if quantidade > blocos_livres:
            print("[DEBUG] Não há blocos livres suficientes")
            return False

        for _ in range(quantidade):
            indice = self.__find_free_block__()
            if indice == -1:
                print("[DEBUG] Erro inesperado: bitmap inconsistente")
                return False
            self.__mark_block_used__(indice)
            inode.block_indices.append(indice)

        inode.size = len(inode.block_indices) * BLOCK_SIZE
        print(f"[DEBUG] {quantidade} blocos alocados para inode '{inode.name}' (total size: {inode.size} bytes)")
        return True

    # Escreve dados em blocos associados a um inode
    def __escrever_dados__(self, inode: Inode, data: str):
        print(f"[DEBUG] Escrevendo dados no arquivo '{inode.name}': '{data}'")
        if not data:
            print("[DEBUG] Nenhum dado para escrever")
            return False

        tamanho = len(data)
        quantidade_blocos = math.ceil(tamanho / BLOCK_SIZE)

        # Alocar blocos conforme necessário
        if not self.__alocar_blocos__(inode, quantidade_blocos):
            print("[DEBUG] Falha na alocação de blocos para escrita")
            return False

        data_cursor = 0
        inode_cursor = inode

        while inode_cursor and data_cursor < tamanho:
            for blk_idx in inode_cursor.block_indices:
                trecho = data[data_cursor:data_cursor + BLOCK_SIZE]
                # Armazena lista de caracteres
                self.blocks[blk_idx].data = list(trecho)
                print(f"[DEBUG] Bloco {blk_idx} recebe dados: '{trecho}'")
                data_cursor += BLOCK_SIZE
                if data_cursor >= tamanho:
                    break
            if inode_cursor.next:
                print(f"[DEBUG] Passando para inode encadeado: '{inode_cursor.next.name}'")
            inode_cursor = inode_cursor.next

        print(f"[DEBUG] Escrita concluída no arquivo '{inode.name}'")
        return True

    # Lê dados de um inode, seguindo encadeamento
    def __ler_dados__(self, inode: Inode) -> str:
        dados_lidos = ''
        inode_cursor = inode

        while inode_cursor is not None:
            for blk_idx in inode_cursor.block_indices:
                bloco = self.blocks[blk_idx]
                trecho = ''.join(bloco.data) if isinstance(bloco.data, list) else str(bloco.data)
                dados_lidos += trecho
                print(f"[DEBUG] Lendo bloco {blk_idx}: '{trecho}'")
            if inode_cursor.next:
                print(f"[DEBUG] Indo para próximo inode: '{inode_cursor.next.name}'")
            inode_cursor = inode_cursor.next

        print(f"[DEBUG] Dados totais lidos do arquivo '{inode.name}': '{dados_lidos}'")
        return dados_lidos

    # Libera um inode e seus blocos
    def __free_inode__(self, inode: Inode):
        if inode.type == "DIR":
            if inode.block_indices:
                # Supondo que diretórios armazenam referências a arquivos (Inodes)
                for file_inode in self.blocks[inode.block_indices[0]].data:
                    self.__free_inode__(file_inode)

        for i in inode.block_indices:
            self.__free_block__(self.blocks[i])

        inode.block_indices = []
        inode.name = "INODE LIVRE"
        inode.type = "INODE LIVRE"
        inode.next = None
        inode.size = 0
        print(f"[DEBUG] Inode '{inode.name}' liberado")

    # Libera um bloco
    def __free_block__(self, block: Block):
        block.data = ''
        self.__mark_block_free__(block.index)

    # Lê o conteúdo do diretório ou arquivo
    def __read_blocks__(self, inode: Inode):
        if inode.type == "DIR":
            print(f"Conteúdo do diretório '{inode.name}':")
            if inode.block_indices:
                for j in self.blocks[inode.block_indices[0]].data:
                    print(f"  {j.type} - {j.name}")
            print("Fim do diretório")
            return True

        print(f"Conteúdo do arquivo '{inode.name}':")
        for i in inode.block_indices:
            dados = self.blocks[i].data
            texto = ''.join(dados) if isinstance(dados, list) else str(dados)
            print(texto)
        return True

    # Cria um novo arquivo ou diretório
    def newFile(self, fileName: str, type: str, data=None):
        # Validação de nome inválido
        if not fileName or fileName in [".", ".."]:
            print(f"[ERRO] Nome inválido para arquivo/diretório: '{fileName}'")
            return False
        # Caso especial: criando root quando cwd é None
        if self.cwd is None:
            inode = self.__alocar_inode__(fileName, type)
            if inode is None:
                print("[ERRO] Não foi possível alocar inode para root")
                return False
            inode.type = type
            # Aloca pelo menos 1 bloco
            if not self.__alocar_blocos__(inode, 1):
                print("[ERRO] Não foi possível alocar bloco para root")
                return False
            self.blocks[inode.block_indices[0]].data = []
            return inode

        # Também vale verificar se já existe um arquivo/diretório com esse nome no cwd
        for f in self.blocks[self.cwd.block_indices[0]].data:
            if f.name == fileName:
                print(f"[ERRO] Arquivo ou diretório com nome '{fileName}' já existe no diretório atual")
                return False

        if self.cwd is None:
            file = self.__alocar_inode__(fileName, type)
            if file is None:
                return False
            if not self.__alocar_blocos__(file, 1):
                return False
            self.blocks[file.block_indices[0]].data = []
            return file

        # Verifica se já existe arquivo com mesmo nome no diretório atual
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == fileName:
                print(f"[DEBUG] Já existe arquivo ou diretório chamado '{fileName}' aqui")
                return False

        try:
            file = self.__alocar_inode__(fileName, type)
            if file is None:
                return False
            if type == "DIR":
                if not self.__alocar_blocos__(file, 1):
                    print("[DEBUG] Falha ao alocar bloco para diretório")
                    return False
                self.blocks[file.block_indices[0]].data = []
            elif data is not None:
                if not self.__escrever_dados__(file, data):
                    print("[DEBUG] Falha ao escrever dados no arquivo")
                    return False

            self.blocks[self.cwd.block_indices[0]].data.append(file)
            file.parent = self.cwd
            file.path = self.cwd.path + "/" + fileName

            print(f"[DEBUG] '{fileName}' criado com sucesso no diretório '{self.cwd.name}'")
            return file

        except Exception as e:
            print(f"[DEBUG] Erro desconhecido ao criar arquivo: {e}")
            return False

    # Remove um arquivo/diretório pelo nome
    def removeFile(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == fileName:
                self.blocks[self.cwd.block_indices[0]].data.remove(i)
                self.__free_inode__(i)
                print(f"[DEBUG] '{fileName}' removido com sucesso")
                return True
        print(f"[DEBUG] Arquivo '{fileName}' não encontrado para remoção")
        return False

    # Lista arquivos do diretório atual
    def ls(self):
        self.__read_blocks__(self.cwd)

    # Abre arquivo ou entra no diretório
    def openFile(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == fileName:
                if i.type == "DIR":
                    self.cwd = i
                    self.pwd()
                self.__read_blocks__(i)
                return True
        print(f"[DEBUG] Arquivo '{fileName}' não encontrado")
        return False

    # Vai para o diretório pai
    def goUpwards(self):
        if self.cwd.parent is not None:
            self.cwd = self.cwd.parent
            self.pwd()
            return True
        print("[DEBUG] Não existe diretório acima do atual")
        return False

    # Imprime o caminho do diretório atual
    def pwd(self):
        print(f"Caminho atual: {self.cwd.path}")

    # Renomeia arquivo/diretório
    def renameFile(self, fileName: str, newName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == newName:
                print("[DEBUG] Já existe arquivo com o novo nome")
                return False
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == fileName:
                i.name = newName
                i.path = self.cwd.path + "/" + newName
                print(f"[DEBUG] Arquivo '{fileName}' renomeado para '{newName}'")
                return True
        print(f"[DEBUG] Arquivo '{fileName}' não encontrado para renomear")
        return False

    # Copia arquivo para buffer temporário
    def copyFile(self, fileName: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == fileName:
                self.copyBuffer = i
                print(f"[DEBUG] '{fileName}' copiado para buffer")
                return True
        print(f"[DEBUG] Arquivo '{fileName}' não encontrado para copiar")
        return False

    def pasteFile(self):
        print("[DEBUG] Iniciando operação de colar arquivo do buffer")
        if self.copyBuffer is None:
            print("[ERRO] Buffer vazio - nada para colar")
            return False

        print(f"[DEBUG] Arquivo no buffer: '{self.copyBuffer.name}'")

        # Verifica se já existe arquivo/diretório com mesmo nome no diretório atual
        print("[DEBUG] Verificando existência de arquivo/diretório com mesmo nome no diretório atual")
        nomes_cwd = [f.name for f in self.blocks[self.cwd.block_indices[0]].data]
        print(f"[DEBUG] Arquivos no diretório atual: {nomes_cwd}")

        if self.copyBuffer.name in nomes_cwd:
            print(f"[ERRO] Já existe um arquivo/diretório com o nome '{self.copyBuffer.name}' aqui")
            return False

        # Adiciona uma cópia para evitar referência ao mesmo objeto
        import copy
        novo_arquivo = copy.deepcopy(self.copyBuffer)
        novo_arquivo.parent = self.cwd
        novo_arquivo.path = self.cwd.path + "/" + novo_arquivo.name

        print(f"[DEBUG] Criando cópia do arquivo '{novo_arquivo.name}' para colar em '{self.cwd.path}'")
        self.blocks[self.cwd.block_indices[0]].data.append(novo_arquivo)
        print(f"[DEBUG] '{novo_arquivo.name}' colado com sucesso no diretório atual: '{self.cwd.path}'")

        return True

    # Modifica dados de um arquivo
    def modifyFile(self, fileName: str, newData: str):
        for i in self.blocks[self.cwd.block_indices[0]].data:
            if i.name == fileName:
                self.__free_inode__(i)
                if not self.__escrever_dados__(i, newData):
                    print("[DEBUG] Falha ao modificar dados do arquivo")
                    return False
                print(f"[DEBUG] Arquivo '{fileName}' modificado com sucesso")
                return True
        print(f"[DEBUG] Arquivo '{fileName}' não encontrado para modificação")
        return False

    def run_debug_tests(self):
        print("[DEBUG] Iniciando testes robustos de debug...")

        # 1 - Criar arquivo com nome inválido
        nomes_invalidos = ["", ".", ".."]
        for nome in nomes_invalidos:
            res = self.newFile(nome, "FILE")
            print(f"[TEST 1] Criar arquivo com nome '{nome}': {'Sucesso' if res else 'Falha esperada'}")
            assert res is False, f"[ERRO CRÍTICO] Aceitou nome inválido '{nome}'"

        # 2 - Mover arquivo para local com mesmo nome (simulando com rename e copy+paste)
        # Criar um arquivo no root
        arq1 = self.newFile("arquivo1.txt", "FILE", "Teste")
        assert arq1, "[ERRO CRÍTICO] Falha ao criar arquivo1"

        # Criar diretório para mover
        dir1 = self.newFile("dir1", "DIR")
        assert dir1, "[ERRO CRÍTICO] Falha ao criar diretório dir1"

        # Simular copiar arquivo1 para dir1
        self.copyFile("arquivo1.txt")
        self.cwd = dir1
        res_paste = self.pasteFile()

        print(f"[TEST 2] Colar arquivo com mesmo nome em dir1: {'Sucesso' if res_paste else 'Falha esperada'}")
        assert res_paste is False, "[ERRO CRÍTICO] Permitido arquivo duplicado no mesmo diretório"

        # Reset cwd para root
        self.cwd = self.root

        # 3 - Verificar atualização do caminho ao mover arquivo/diretório
        # Criar subdir e arquivo dentro dele
        subdir = self.newFile("subdir", "DIR")
        assert subdir, "[ERRO CRÍTICO] Falha ao criar subdir"
        self.cwd = subdir
        subfile = self.newFile("subfile.txt", "FILE", "conteúdo")
        assert subfile, "[ERRO CRÍTICO] Falha ao criar subfile"

        self.cwd = self.root
        # Mover subdir para dir1 (simulando removendo e adicionando)
        if subdir in self.blocks[self.cwd.block_indices[0]].data:
            self.blocks[self.cwd.block_indices[0]].data.remove(subdir)
        self.cwd = dir1
        # Antes de adicionar, checar nome duplicado
        nomes_dir1 = [f.name for f in self.blocks[self.cwd.block_indices[0]].data]
        assert subdir.name not in nomes_dir1, "[ERRO CRÍTICO] Nome já existe no destino"

        self.blocks[self.cwd.block_indices[0]].data.append(subdir)
        subdir.parent = self.cwd

        # Atualizar caminhos recursivamente
        def atualizar_path(inode, novo_path):
            inode.path = novo_path
            if inode.type == "DIR" and inode.block_indices:
                for f in self.blocks[inode.block_indices[0]].data:
                    atualizar_path(f, novo_path + "/" + f.name)

        atualizar_path(subdir, self.cwd.path + "/" + subdir.name)
        print(f"[TEST 3] Caminho do subdir atualizado: {subdir.path}")
        print(f"[TEST 3] Caminho do subfile atualizado: {subfile.path}")
        assert subfile.path.startswith(
            subdir.path), "[ERRO CRÍTICO] Caminho do arquivo filho não atualizado corretamente"

        # 4 - Deletar diretório e garantir liberação recursiva de blocos e inodes
        self.cwd = dir1
        qtd_blocos_antes = sum(self.block_bitmap)
        qtd_inodes_antes = sum(1 for i in self.inodes if i.name != "INODE LIVRE")
        self.removeFile("subdir")
        qtd_blocos_depois = sum(self.block_bitmap)
        qtd_inodes_depois = sum(1 for i in self.inodes if i.name != "INODE LIVRE")

        print(f"[TEST 4] Blocos ocupados antes: {qtd_blocos_antes}, depois: {qtd_blocos_depois}")
        print(f"[TEST 4] Inodes ocupados antes: {qtd_inodes_antes}, depois: {qtd_inodes_depois}")
        assert qtd_blocos_depois < qtd_blocos_antes, "[ERRO CRÍTICO] Blocos não liberados após deleção"
        assert qtd_inodes_depois < qtd_inodes_antes, "[ERRO CRÍTICO] Inodes não liberados após deleção"

        # 5 - Tamanho infinito: testar com dados enormes (maior que INODE_SIZE * BLOCK_SIZE)
        self.cwd = self.root
        arquivo_grande = self.newFile("grande.txt", "FILE")
        assert arquivo_grande, "[ERRO CRÍTICO] Falha ao criar arquivo grande"
        dados_grandes = "X" * (INODE_SIZE * BLOCK_SIZE * 3)  # Forçar mais de um inode encadeado
        sucesso_escrita = self.__escrever_dados__(arquivo_grande, dados_grandes)
        print(f"[TEST 5] Escrita de arquivo grande com encadeamento: {'Sucesso' if sucesso_escrita else 'Falha'}")
        assert sucesso_escrita, "[ERRO CRÍTICO] Falha ao escrever arquivo grande com inode encadeado"
        dados_lidos_grande = self.__ler_dados__(arquivo_grande)
        assert dados_lidos_grande.startswith("X"), "[ERRO CRÍTICO] Dados lidos incorretos no arquivo grande"
        assert len(dados_lidos_grande) == len(dados_grandes), "[ERRO CRÍTICO] Tamanho do arquivo lido incorreto"

        # 6 - Verificar se inode foi encadeado
        assert arquivo_grande.next is not None, "[ERRO CRÍTICO] Inode não foi encadeado para arquivo grande"

        # 7,8 - Testar reutilização de blocos e bitmap
        # Liberar arquivo_grande
        self.__free_inode__(arquivo_grande)
        blocos_livres_apos_free = self.block_bitmap.count(0)
        print(f"[TEST 7-8] Blocos livres após liberar arquivo grande: {blocos_livres_apos_free}")
        assert blocos_livres_apos_free >= INODE_SIZE * 3, "[ERRO CRÍTICO] Blocos não foram liberados no bitmap"

        # Criar novo arquivo que deve reutilizar blocos livres
        novo_arquivo = self.newFile("novo.txt", "FILE")
        assert novo_arquivo, "[ERRO CRÍTICO] Falha ao criar novo arquivo após liberação"
        dados_novo = "Y" * (BLOCK_SIZE * 2)
        self.__escrever_dados__(novo_arquivo, dados_novo)
        blocos_livres_apos_novo = self.block_bitmap.count(0)
        print(f"[TEST 7-8] Blocos livres após criar novo arquivo: {blocos_livres_apos_novo}")
        assert blocos_livres_apos_novo < blocos_livres_apos_free, "[ERRO CRÍTICO] Blocos não reutilizados"

        # 9 - Verificar reutilização de inodes
        inodes_livres_antes = sum(1 for i in self.inodes if i.name == "INODE LIVRE")
        self.__free_inode__(novo_arquivo)
        inodes_livres_depois = sum(1 for i in self.inodes if i.name == "INODE LIVRE")
        print(f"[TEST 9] Inodes livres antes: {inodes_livres_antes}, depois: {inodes_livres_depois}")
        assert inodes_livres_depois > inodes_livres_antes, "[ERRO CRÍTICO] Inodes não foram liberados e reutilizados"

        # 10 - Verificação simples de limite de inodes e blocos (não infinito)
        print(f"[TEST 10] Total blocos: {TOTAL_BLOCKS}, Total inodes: {TOTAL_INODES}")
        assert TOTAL_BLOCKS < 1_000_000, "[ERRO CRÍTICO] Total de blocos exagerado (infinito)"
        assert TOTAL_INODES < 10_000, "[ERRO CRÍTICO] Total de inodes exagerado (infinito)"

        print("[DEBUG] Todos os testes robustos passaram com sucesso!")
