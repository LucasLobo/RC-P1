# RC-P1

Projecto realizado no âmbito da cadeira de Redes e Computadores do curso de Engenharia Informática e de Computadores pelo grupo 54 constituido pelos seguintes elementos:

-João Gonçalo da Luz Rodrigues nº76154

-Lucas Lobo Fell nº86464

-Marcos Pedrosa Pêgo nº86472


O objectivo deste projecto era criar uma rede simples que permitia aos utilizadores guardar documentos de um dado repositório para um serviço de nuvem(Cloud Service).

Este projecto contém 3 aplicações:

-user.py(Aplicação do Utilizador)

-CS.py(Aplicação do Servidor Central)

-BS.py(Aplicação do Servidor de Backup)


# Compilar e Correr o Projecto


Para correr este projecto é necessário executar os seguintes comandos no directório do projecto:

-make clean

-make all


Após realizar estas operações podemos correr os scripts de python:

-./CS.py [-p CSport]

(Sendo CSport um argumento opcional)

-./BS.py [-b BSport] [-n CSname] [-p CSport]

(Sendo BSport, CSname e CSport argumentos opcionais)

-./user.py [-n CSname] [-p CSport]

(Sendo CSname e CSport argumentos opcionais)


O utilizador dispõe dos seguintes comandos:

-login user pass

-deluser

-backup dir

-restore dir

-dirlist

-filelist dir

-delete dir

-logout

-exit
