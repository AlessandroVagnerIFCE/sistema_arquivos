#Aqui é onde faço os testes para verificar se tudo está funcionando corretamente

from file_system import FileSystem

#TESTES    
sistema = FileSystem()

#Criar arquivos
sistema.newFile("teste.txt", "TEXT", "Isso é um teste")
sistema.newFile("dirteste", "DIR")
sistema.ls()
print("\n")

#Abrir arquivos
sistema.openFile("teste.txt")
sistema.openFile("dirteste")
sistema.newFile("outro_teste.txt", "TEXT", "Isso é outro teste")
sistema.ls()
print("\n")
sistema.goUpwards()
#sistema.removeFile("dirteste")

#Copiar e colar arquivos
sistema.copyFile("dirteste")
sistema.pasteFile()
sistema.ls()
sistema.openFile("dirteste(1)")
sistema.goUpwards()
sistema.ls()
print("\n")
#sistema.copyFile("teste.txt")
#sistema.pasteFile()
#sistema.copyFile("dirteste")
#sistema.pasteFile()
#sistema.copyFile("dirteste")
#sistema.pasteFile()
#sistema.removeFile("dirteste(1)")
#sistema.openFile("teste.txt(1)")
#sistema.openFile("dirteste")

#Mover arquivos
sistema.moveFile("dirteste(1)", "/root/dirteste")
sistema.ls()
sistema.openFile("dirteste")
sistema.goUpwards()
sistema.copyFile("dirteste")
sistema.pasteFile()
sistema.ls()
sistema.moveFile("dirteste(1)", "/root/dirteste")
sistema.openFile("dirteste")
sistema.goUpwards()
sistema.ls()

