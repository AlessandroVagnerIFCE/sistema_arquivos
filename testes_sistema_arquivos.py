import shlex
from file_system import FileSystem        # seu módulo original
from file_system_linked import LinkedFileSystem

def imprimir_ajuda():
    print("""
Escolha o FS para testar:
  1 - FileSystem (inode-based)
  2 - LinkedFileSystem (chain-based)
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
    tamanho_arquivo = 1000  # tamanho do conteúdo em caracteres
    conteudo = 'A' * tamanho_arquivo

    print(f"\nComparando desempenho com arquivos de {tamanho_arquivo} caracteres...\n")

    # TESTE: criação
    print("1. Criação de arquivo:")
    
    fs = FileSystem()
    inicio = time.time()
    fs.newFile('teste.txt', 'TEXT', conteudo)
    duracao_inode = time.time() - inicio
    print(f"- FileSystem (inode): {duracao_inode:.6f}s")

    lfs = LinkedFileSystem()
    inicio = time.time()
    lfs.newFile('teste.txt', 'TEXT', conteudo)
    duracao_linked = time.time() - inicio
    print(f"- LinkedFileSystem (cadeia): {duracao_linked:.6f}s")

    # TESTE: leitura
    print("\n2. Leitura de arquivo:")

    inicio = time.time()
    fs.readFile('teste.txt')
    duracao_inode = time.time() - inicio
    print(f"- FileSystem (inode): {duracao_inode:.6f}s")

    inicio = time.time()
    lfs.readFile('teste.txt')
    duracao_linked = time.time() - inicio
    print(f"- LinkedFileSystem (cadeia): {duracao_linked:.6f}s")

    # TESTE: escrita
    print("\n3. Escrita em arquivo:")
    novo_conteudo = 'B' * tamanho_arquivo

    inicio = time.time()
    fs.writeFile('teste.txt', novo_conteudo)
    duracao_inode = time.time() - inicio
    print(f"- FileSystem (inode): {duracao_inode:.6f}s")

    inicio = time.time()
    lfs.writeFile('teste.txt', novo_conteudo)
    duracao_linked = time.time() - inicio
    print(f"- LinkedFileSystem (cadeia): {duracao_linked:.6f}s")

    # TESTE: remoção
    print("\n4. Remoção de arquivo:")

    inicio = time.time()
    fs.removeFile('teste.txt')
    duracao_inode = time.time() - inicio
    print(f"- FileSystem (inode): {duracao_inode:.6f}s")

    inicio = time.time()
    lfs.removeFile('teste.txt')
    duracao_linked = time.time() - inicio
    print(f"- LinkedFileSystem (cadeia): {duracao_linked:.6f}s")

    print("\n🔚 Comparação concluída.")


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
        #elif opc == '3':
            #comparar_desempenho()
        elif opc in ('help','?'):
            continue
        elif opc in ('exit','quit'):
            print('Encerrando.')
            break
        else:
            print('Opção inválida.')

if __name__ == '__main__':
    main()
