#Aqui é onde faço os testes para verificar se tudo está funcionando corretamente

from file_system import FileSystem

#TESTES    
sistema = FileSystem()
sistema.newFile("teste.txt", "TEXT", "Isso é um teste")
sistema.newFile("dirteste", "DIR")
sistema.ls()
print("\n")
sistema.openFile("teste.txt")
sistema.openFile("dirteste")
sistema.newFile("outro_teste.txt", "TEXT", "Isso é outro teste")
sistema.ls()
print("\n")
sistema.goUpwards()
sistema.removeFile("dirteste")
sistema.ls()
sistema.goUpwards()