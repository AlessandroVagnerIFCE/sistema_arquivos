import shlex
from file_class import Inode, FFileEnc

# parâmetros do FS simulado
BLOCK_SIZE = 4       # caracteres por bloco
TOTAL_BLOCKS = 100

class Block:
    def __init__(self, index):
        self.index = index
        self.data = ''
        self.next = None

class LinkedFileSystem:
    def __init__(self):
        self.blocks = [Block(i) for i in range(TOTAL_BLOCKS)]
        # cria inode raiz
        root_inode = Inode('root', 'DIR')
        root_inode.dir_entries = []  # para diretório, lista de FFILE
        self.root = FFileEnc(root_inode)
        self.root.path = '/root'
        self.root.parent = None
        self.cwd = self.root
        print('LinkedFS iniciado com sucesso')

    def _allocate_chain(self, content: str, inode: Inode):
        # libera blocos anteriores
        for idx in inode.block_indices:
            blk = self.blocks[idx]
            blk.data = ''
            blk.next = None
        inode.block_indices.clear()
        inode.head = None
        # aloca nova cadeia
        prev = None
        pos = 0
        while pos < len(content):
            # encontra bloco livre
            for blk in self.blocks:
                if blk.data == '': break
            pedaco = content[pos:pos+BLOCK_SIZE]
            blk.data = pedaco
            inode.block_indices.append(blk.index)
            if prev:
                prev.next = blk
            else:
                inode.head = blk
            prev = blk
            pos += BLOCK_SIZE
        inode.size = len(content)

    @staticmethod
    def _read_chain(head: Block) -> str:
        data = ''
        blk = head
        while blk:
            data += blk.data
            blk = blk.next
        return data

    def newFile(self, name: str, ftype: str, content: str = None):
        # checa duplicados
        for entry in self.cwd.inode.dir_entries:
            if entry.name == name:
                print('Já existe arquivo/diretório com esse nome')
                return False
        # cria inode e FFile
        inode = Inode(name, ftype)
        if ftype == 'DIR':
            inode.dir_entries = []
        file = FFileEnc(inode)
        # monta conteúdo
        if ftype in ('TEXT', 'EXEC'):
            self._allocate_chain(content or '', inode)
        # link pai e path
        file.parent = self.cwd
        file.path = self.cwd.path + '/' + name
        self.cwd.inode.dir_entries.append(file)
        return file

    def ls(self):
        # listar entradas do cwd
        self.cwd.read()

    def cd(self, name: str):
        # navegação: '.', '..' ou subdiretório
        if name == '.':
            print(self.cwd.path)
            return True
        if name == '..':
            if self.cwd.parent:
                self.cwd = self.cwd.parent
            print(self.cwd.path)
            return True
        # busca subdir
        for entry in self.cwd.inode.dir_entries:
            if entry.name == name and entry.type == 'DIR':
                self.cwd = entry
                print(self.cwd.path)
                return True
        print('Diretório não encontrado')
        return False

    def moveFile(self, name: str, target_path: str):
        # encontra arquivo no cwd
        item = next((e for e in self.cwd.inode.dir_entries if e.name == name), None)
        if not item:
            print('Arquivo não encontrado')
            return False
        # resolve target_path
        parts = target_path.strip('/').split('/')
        cur = self.root
        for p in parts[1:]:
            cur = next((e for e in cur.inode.dir_entries if e.name==p and e.type=='DIR'), None)
            if not cur:
                print('Caminho inválido')
                return False
        # remove do cwd e anexa ao destino
        self.cwd.inode.dir_entries.remove(item)
        cur.inode.dir_entries.append(item)
        item.parent = cur
        # atualiza paths
        def upd(f, base):
            f.path = base + '/' + f.name
            if f.type == 'DIR':
                for sub in f.inode.dir_entries:
                    upd(sub, f.path)
        upd(item, cur.path)
        print(f"{name} movido para {cur.path}")
        return True

    def writeFile(self, name: str, content: str):
        # simula escrita
        item = next((e for e in self.cwd.inode.dir_entries if e.name==name and e.type!='DIR'), None)
        if not item:
            print('Arquivo não encontrado ou não é arquivo')
            return False
        self._allocate_chain(content, item.inode)
        print(f"Escrito em {name}: {len(content)} bytes")
        return True

    def readFile(self, name: str):
        # simula leitura
        item = next((e for e in self.cwd.inode.dir_entries if e.name==name and e.type!='DIR'), None)
        if not item:
            print('Arquivo não encontrado ou não é arquivo')
            return False
        text = self._read_chain(item.inode.head)
        print(text)
        return True

    def removeFile(self, name: str):
        # remoção de arquivo ou diretório
        item = next((e for e in self.cwd.inode.dir_entries if e.name==name), None)
        if not item:
            print('Arquivo/Diretório não encontrado')
            return False
        # libera blocos se arquivo
        if item.type != 'DIR':
            for idx in item.inode.block_indices:
                blk = self.blocks[idx]
                blk.data = ''
                blk.next = None
        # se diretório, recursivamente removemos entradas (garbage collector simulado)
        self.cwd.inode.dir_entries.remove(item)
        print(f"{name} excluído com sucesso")
        return True

def imprimir_ajuda():
    print("""
Comandos disponíveis:
  ls
  cd <diretório|. |..>
  mkdir <nome_do_diretório>
  touch <nome_do_arquivo> [conteúdo inicial]
  mv <nome> <caminho/destino>
  write <nome_do_arquivo> <novo_conteúdo>
  read <nome_do_arquivo>
  rm <nome>
  help
  exit
""")

def main():
    fs = LinkedFileSystem()
    imprimir_ajuda()

    while True:
        try:
            linha = input(f"{fs.cwd.path}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not linha:
            continue

        # divide respeitando aspas
        partes = shlex.split(linha)
        cmd, *args = partes

        if cmd == 'ls':
            fs.ls()

        elif cmd == 'cd':
            if len(args) != 1:
                print("Uso: cd <diretório|. |..>")
            else:
                fs.cd(args[0])

        elif cmd == 'mkdir':
            if len(args) != 1:
                print("Uso: mkdir <nome_do_diretório>")
            else:
                result = fs.newFile(args[0], 'DIR')
                if result:
                    print(f"Diretório '{args[0]}' criado.")

        elif cmd == 'touch':
            if len(args) == 0:
                print("Uso: touch <nome_do_arquivo> [conteúdo]")
            else:
                name = args[0]
                content = args[1] if len(args) > 1 else ''
                result = fs.newFile(name, 'TEXT', content)
                if result:
                    print(f"Arquivo '{name}' criado.")

        elif cmd == 'mv':
            if len(args) != 2:
                print("Uso: mv <nome> <caminho/destino>")
            else:
                fs.moveFile(args[0], args[1])

        elif cmd == 'write':
            if len(args) < 2:
                print("Uso: write <nome_do_arquivo> <novo_conteúdo>")
            else:
                name = args[0]
                content = " ".join(args[1:])
                fs.writeFile(name, content)

        elif cmd == 'read':
            if len(args) != 1:
                print("Uso: read <nome_do_arquivo>")
            else:
                fs.readFile(args[0])

        elif cmd == 'rm':
            if len(args) != 1:
                print("Uso: rm <nome>")
            else:
                fs.removeFile(args[0])

        elif cmd in ('help', '?'):
            imprimir_ajuda()

        elif cmd in ('exit', 'quit'):
            print("Encerrando LinkedFS.")
            break

        else:
            print(f"Comando desconhecido: {cmd}. Digite 'help' para ver a lista.")

if __name__ == '__main__':
    main()