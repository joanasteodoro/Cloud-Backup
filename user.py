#Computers' Networks Project
#Group 17

#port=58011 user=99999 pass=zzzzzzzz '192.168.1.1'

import socket
import sys
import os
import signal
import time
import shutil

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
luser = -1
lpassword = -1

def login(user, password, server_address):
    lusername = user
    lpass = password
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Resolve o bad file descriptor
    sckt.connect(server_address)
    logged = 1
    try:
        message = "AUT "+ lusername + " " + lpass
        sckt.sendall(message.encode())
        amount_received = 0
        amount_expected = 1024
        while amount_received == 0:
            data = sckt.recv(1024)
            amount_received += len(data.decode())
            if("AUR NEW\n" == data.decode()):
                result = "User " + lusername + " created\n"
            elif("AUR OK\n" == data.decode()):
                result = "Successful login\n"
            elif("AUR NOK\n" == data.decode()):
                result = "Wrong Password\n"
                logged = 0
            print(result)
    finally:
        sckt.close()
    if (logged == 0):
        return 1
    return 0

def deluser(lusername, lpass, server_address):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Resolve o bad file descriptor
    sckt.connect(server_address)
    global luser
    try:
        message = "AUT "+ lusername + " " + str(lpass)
        sckt.sendall(message.encode())
        amount_received = 0
        amount_expected = 1024
        data = sckt.recv(1024)
        if("AUR OK\n" == data.decode()):
            message = "DLU\n"
            sckt.sendall(message.encode())
        result = sckt.recv(1024)
        result = result.decode()
        if(result == "DLU OK\n"):
        	luser = -1
    finally:
        sckt.close()
    return 0

def send_file(folder, filename, sckt_aux):
    path = os.path.join(folder, filename)
    f = open(path, 'rb')
    bytesToSend = f.read(1024)
    while(bytesToSend):
        sckt_aux.send(bytesToSend)
        time.sleep(0.1)
        bytesToSend = f.read(1024)
    f.close()

def receive_file(user, sckt_aux, n_files, path):
    for i in range(int(n_files)):
        data = sckt_aux.recv(1024)
        data = data.decode().split()
        name = data[0]
        size = data[1]
        bytesReceived = 0
        size = int(size)
        f = open(name, 'wb')
        data = sckt_aux.recv(1024)
        f.write(data)
        bytesReceived += len(data)
        while (bytesReceived < size):
            data = sckt_aux.recv(1024)
            f.write(data)
            bytesReceived += len(data)
        f.close()
        path2 = os.path.join(path, name)
        os.rename(name, path2)

def backupBS(user, password, server_address, directory):
    socket_aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_aux.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        socket_aux.sendall(message.encode())
        data = socket_aux.recv(1024)
        files = os.listdir(directory)
        num = len(files)
        result = 'completed – ' + directory + ': '
        if ("AUR OK\n" == data.decode()):
            Message = "UPL " + directory + ' ' + str(num)
            socket_aux.sendall(Message.encode())
            for i in range(num):
                result += files[i] + ' '
                path = os.path.join(directory, files[i])
                stat = time.gmtime(os.path.getmtime(path))
                date = time.strftime('%d.%m.%y', stat)
                file_time = time.strftime('%H:%M:%S', stat)
                size = os.path.getsize(path)
                Message = '\t' + files[i] + ' ' + date + ' ' + file_time + ' ' + str(size) + '\n'
                socket_aux.sendall(Message.encode())
                time.sleep(0.1)
                send_file(directory, files[i], socket_aux)
            data = socket_aux.recv(1024)
        if("UPR OK\n" == data.decode()):
            print(result + '\n')
    finally:
        socket_aux.close()

def backupDir(user, password, server_address, directory):
    sckt.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        sckt.sendall(message.encode())
        data = sckt.recv(1024)
        if ("AUR OK\n" == data.decode()):
            files = os.listdir(directory)
            num = len(files)
            Message = "BCK " + directory + ' ' + str(num)
            sckt.sendall(Message.encode())
            #Part where he receives the ip address and port
            #Envia os ficheiros e os seus detalhes
            Message = ''
            for i in range(num):
                path = os.path.join(directory, files[i])
                stat = time.gmtime(os.path.getmtime(path))
                date = time.strftime('%d.%m.%y', stat)
                file_time = time.strftime('%H:%M:%S', stat)
                size = os.path.getsize(path)
                Message += '\t' + files[i] + ' ' + date + ' ' + file_time + ' ' + str(size) + '\n'
            sckt.sendall(Message.encode())
            result = sckt.recv(1024)
            result = result.decode()
            result = result.split()
            print("backup to: " + result[1] + ' ' + result[2])
            server_address = ('localhost', int(result[2])) #If we working on the same computer = 'localhost', else = result[1]
    finally:
        sckt.close()
        backupBS(user, password, server_address, directory)
    return 0

def dirList(user, password, server_address):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        sckt.sendall(message.encode())
        data = sckt.recv(1024)
        if ("AUR OK\n" == data.decode()):
            message = 'LSD\n'
        sckt.sendall(message.encode())
        result = sckt.recv(1024)
        result = result.decode()
        print(result)
    finally:
        sckt.close()
    return 0

def filelistDir(user, password, server_address, directory):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        sckt.sendall(message.encode())
        data = sckt.recv(1024)
        if ("AUR OK\n" == data.decode()):
            message = 'LSF ' + directory + '\n'
        sckt.sendall(message.encode())
        result = sckt.recv(1024)
        result = result.decode()
        print(result)
    finally:
        sckt.close()
    return 0

def restoreBS(user, password, server_address, directory):
    socket_aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_aux.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        socket_aux.sendall(message.encode())
        data = socket_aux.recv(1024)
        if ("AUR OK\n" == data.decode()):
            Message = "RSB " + directory
            socket_aux.sendall(Message.encode())
            data = socket_aux.recv(1024)
            data = data.decode()
            data = data.split()
            if (os.path.isdir(directory)):
                shutil.rmtree(directory)
            os.makedirs(directory)
            receive_file(luser, socket_aux, data[1], directory)
            data = socket_aux.recv(1024)
        result = "success – " + directory + ': '
        n_files = os.listdir(directory)
        for i in range(len(n_files)):
            if(i != len(n_files)-1 ):
                result += n_files[i] + ', '
            else:
                result += n_files[i] + '\n'
        print(result)
    finally:
        socket_aux.close()

def restoreDir(user, password, server_address, directory):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        sckt.sendall(message.encode())
        data = sckt.recv(1024)
        if ("AUR OK\n" == data.decode()):
            files = os.listdir(directory)
            num = len(files)
            Message = "RST " + directory + '\n'
            sckt.sendall(Message.encode())
            #Part where he receives the ip address and port
            data = sckt.recv(1024)
            data = data.decode()
            data = data.split()
            print('from : ' + data[1] + ' ' + data[2])
            server_address = (data[1], int(data[2])) #If we working on the same computer = 'localhost', else = result[1]
    finally:
        sckt.close()
        restoreBS(user, password, server_address, directory)
    return 0

def deleteDir(user, password, server_address, directory):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect(server_address)
    try:
        message = "AUT " + user + " " + password
        sckt.sendall(message.encode())
        data = sckt.recv(1024)
        if ("AUR OK\n" == data.decode()):
            Message = "DEL " + directory + '\n'
            sckt.sendall(Message.encode())
            #Part where he receives the ip address and port
            data = sckt.recv(1024)
            data = data.decode()
            if(data == 'DDR OK\n'):
                print('deleted ' + directory + '\n')
            else:
                print('directory does not exist')
    finally:
        sckt.close()
    return 0

def logout(user, password):
    luser = -1
    lpassword = -1
    return 0

def main():
    if(len(sys.argv) == 4):
        CSname = input("CS name: ")
        CSport = input("Port: ")
    elif(len(sys.argv) == 3 and isinstance(sys.argv[2], str)):
        CSname = input("CS name: ")
    elif(len(sys.argv) == 3 and isinstance(sys.argv[2], int)):
        CSport = input("Port: ")
    elif(len(sys.argv) == 3):
        raise TypeError('Error: invalid input.')
    else:
        CSport = 58017
    server_address = ('localhost', CSport)
    global luser
    logged = 0
    while True:
        menu_input = input()
        if (isinstance(menu_input, str)):
        #FAZER CHECK NA PASSWORD
            instruction = menu_input.split()
            if(instruction[0] == "login" and isinstance(instruction[1], str) and isinstance(instruction[2], str) and not logged):
                luser = instruction[1]
                lpassword = instruction[2]
                logged = 1
                if (login(luser, lpassword, server_address) == 1):
                    logged = 0
            elif(instruction[0] == "deluser" and logged):
            		if(luser == -1):
            			print("Login required.")
            		else:
                		deluser(luser, lpassword, server_address)
            elif(instruction[0] == "backup" and len(instruction) == 2 and logged):
                directory = instruction[1]
                backupDir(luser, lpassword, server_address, directory)
            elif(instruction[0] == "dirlist" and logged):
                dirList(luser, lpassword, server_address)
            elif(instruction[0]=="filelist" and len(instruction) == 2 and logged):
                directory = instruction[1]
                filelistDir(luser, lpassword, server_address, directory)
            elif(instruction[0] == "restore" and len(instruction) == 2 and logged):
                directory = instruction[1]
                restoreDir(luser, lpassword, server_address, directory)
            elif(instruction[0] == "delete" and len(instruction) == 2 and logged):
                directory = instruction[1]
                deleteDir(luser, lpassword, server_address, directory)
            elif(instruction[0] == "logout" and logged):
                logout(luser, lpassword)
                logged = 0
                print('Successful logout\n')
            elif(instruction[0] == "exit"):
                return 0
            elif (instruction[0] == "login" and logged):
                print("Logout required.\n")
            elif instruction[0] != "exit" and not logged:
                print("Login required.\n")
            else:
                print("Error: Menu instruction invalid.\n")

    return 0

main()
