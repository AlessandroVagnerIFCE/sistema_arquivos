import shlex
from file_system import FileSystem, test_filesystem_errors  # Inodes
from file_system_linked import LinkedFileSystem #Lista encadeada

def imprimir_ajuda():
    print("""
Escolha o FS para testar:
  1 - FileSystem (inode-based)
  2 - LinkedFileSystem (chain-based)
  3 - Executar testes 
  4 - Executar comparação 
  help - mostrar ajuda
  exit - sair
""")

def repl_fs(fs):
    while True:
        try:
            linha = input(f"{fs.cwd.path}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo do REPL.")
            break
        if not linha:
            continue
        partes = shlex.split(linha)
        cmd, *args = partes

        if cmd == 'ls':
            fs.ls()
        elif cmd == 'open' and args:
            if (args[0] == ".."):
                fs.goUpwards()
            else:
                fs.openFile(args[0])
        elif cmd == 'mkdir' and args:
            if (args[0] == ".."):
                print("Nome inválido")
            else:
                fs.newFile(args[0], 'DIR')
        elif cmd == 'touch' and args:
            if (args[0] == ".."):
                print("Nome inválido")
            else:
                fs.newFile(args[0], 'TEXT', args[1] if len(args)>1 else '')
        elif cmd == 'mv' and len(args)==2:
            fs.moveFile(args[0], args[1])
        elif cmd == 'write' and len(args)>=2:
            fs.writeFile(args[0], " ".join(args[1:]))
        elif cmd == 'read' and args:
            fs.readFile(args[0])
        elif cmd == 'rm' and args:
            fs.removeFile(args[0])
        elif cmd == 'inodes' and args:
            fs.printInodesList()
        elif cmd == 'freeblocks' and args:
            fs.printFreeBlocksList()
        elif cmd in ('help','?'):
            imprimir_ajuda()
        elif cmd in ('exit','quit'):
            break
        else:
            print(f"Comando desconhecido: {cmd}")

import time
from file_system import FileSystem
from file_system_linked import LinkedFileSystem

def comparar_desempenho():
    tamanho_arquivo = 1000
    conteudo = 'A' * tamanho_arquivo
    novo_conteudo = 'B' * tamanho_arquivo

    print(f"\n📊 Comparando desempenho com arquivos de {tamanho_arquivo} caracteres...\n")

    for sistema_nome, Sistema in [("FileSystem (inode)", FileSystem), ("LinkedFileSystem (cadeia)", LinkedFileSystem)]:
        print(f"🔧 {sistema_nome}")

        fs = Sistema()
        erro_detectado = False

        # Criação
        try:
            inicio = time.time()
            sucesso = fs.newFile('teste.txt', 'TEXT', conteudo)
            duracao = time.time() - inicio
            if not sucesso:
                print("❌ Erro ao criar arquivo.")
                erro_detectado = True
            else:
                print(f"  - Criação: {duracao:.6f}s")
        except Exception as e:
            print(f"❌ Exceção durante criação: {e}")
            erro_detectado = True

        if erro_detectado:
            continue

        # Leitura
        try:
            inicio = time.time()
            conteudo_lido = fs.readFile('teste.txt')
            duracao = time.time() - inicio
            if conteudo_lido is None:
                print("❌ Erro ao ler o arquivo.")
                erro_detectado = True
            else:
                print(f"  - Leitura: {duracao:.6f}s")
        except Exception as e:
            print(f"❌ Exceção durante leitura: {e}")
            erro_detectado = True

        if erro_detectado:
            continue

        # Escrita
        try:
            inicio = time.time()
            sucesso = fs.writeFile('teste.txt', novo_conteudo)
            duracao = time.time() - inicio
            if not sucesso:
                print("❌ Erro ao escrever no arquivo.")
                erro_detectado = True
            else:
                print(f"  - Escrita: {duracao:.6f}s")
        except Exception as e:
            print(f"❌ Exceção durante escrita: {e}")
            erro_detectado = True

        if erro_detectado:
            continue

        # Remoção
        try:
            inicio = time.time()
            sucesso = fs.removeFile('teste.txt')
            duracao = time.time() - inicio
            if not sucesso:
                print("❌ Erro ao remover o arquivo.")
            else:
                print(f"  - Remoção: {duracao:.6f}s")
        except Exception as e:
            print(f"❌ Exceção durante remoção: {e}")

        print("")  # linha em branco para separação

    print("✅ Comparação concluída.")


def main():
    while True:
        imprimir_ajuda()
        opc = input('Escolha opção> ').strip()
        if opc == '1':
            fs = FileSystem()
            repl_fs(fs)
        elif opc == '2':
            lfs = LinkedFileSystem()
            repl_fs(lfs)

        elif opc == '3':
            test_filesystem_errors()
        elif opc == '4':
            comparar_desempenho()
        elif opc in ('help','?'):
            continue
        elif opc in ('exit','quit'):
            print('Encerrando.')
            break
        else:
            print('Opção inválida.')

if __name__ == '__main__':
    main()
