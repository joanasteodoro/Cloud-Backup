#Computers' Networks Project
#Group 17
#ps aux para obter a lista de processos
#kill -9 PID para acabar o processo
#CENTRAL SERVER

#Otherwise, the CS exchanges LSF-LFD messages with the BS, to
#receive the list of missing or changed files in the backup.

import socket
import sys
import os
import signal
from multiprocessing import Process, Pipe


scktTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
scktUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
luser = -1
lpassword = -1

def signal_handler(sig, frame):
    scktTCP.close()
    scktUDP.close()
    sys.exit(0)

def child(CSport, BSport, childPipe):
    UDP_IP = 'localhost'
    signal.signal(signal.SIGINT, signal_handler)
    scktUDP.bind((UDP_IP, CSport))
    dataUDP, addrUDP = scktUDP.recvfrom(1024)
    dataUDP = dataUDP.decode()
    dataUDP = dataUDP.split()
    BSmsg = "+BS: " + dataUDP[1]  + " " + dataUDP[2]
    print (BSmsg)
    msg = "RGR OK\n"
    scktUDP.sendto(msg.encode(), (UDP_IP, BSport))
    luser = childPipe.recv()
    lpassword = childPipe.recv()
    while True:
        flagUDP = childPipe.recv()
        if flagUDP == 1:
            BSmsg = "LSU " + str(luser) + ' ' + str(lpassword)
            scktUDP.sendto(BSmsg.encode(), (UDP_IP, BSport))
            dataUDP, addr = scktUDP.recvfrom(1024)
            if(dataUDP.decode() == "LUR OK\n" or dataUDP.decode() == "LUR NOK\n"):
                childPipe.send(2)
        if(flagUDP == 3):
            BSmsg = 'LSF ' + luser + ' ' + childPipe.recv() + '\n'
            scktUDP.sendto(BSmsg.encode(), (UDP_IP, BSport))
            dataUDP, addr = scktUDP.recvfrom(1024)
            dataUDP = dataUDP.decode()
            dataUDP = dataUDP.split()
            if(dataUDP[0] == "LFD"):
                childPipe.send(4)
                dataUDP.insert(0, addr)
                childPipe.send(dataUDP)
        if (flagUDP == 5):
            BSmsg = "DLB " + luser + ' ' + childPipe.recv()
            scktUDP.sendto(BSmsg.encode(), (UDP_IP, BSport))
            dataUDP, addr = scktUDP.recvfrom(1024)
            dataUDP = dataUDP.decode()
            if(dataUDP == "DBR NOK\n"):
                childPipe.send(6)
            else:
                childPipe.send(7)

    os._exit(0)

def main():
    users = {}
    global luser
    global lpassword
    if(len(sys.argv) > 1):
    	CSport = 59000
    else:
        CSport = 58017
        BSport = 59000
    parentPipe, childPipe = Pipe()
    newpid = os.fork()
    if newpid == 0:
        p = Process(target=child, args=(CSport, BSport, childPipe))
        p.start()
    else:
        signal.signal(signal.SIGINT, signal_handler)
        tcp_server_address = ('localhost', CSport)
        scktTCP.bind(tcp_server_address)
        scktTCP.listen(1)
        while True:
            connection, client_address = scktTCP.accept()
            try:
                while True:
                    data = connection.recv(1024)
                    data = data.decode()
                    data = data.split()
                    if data:
                        if (data[0] == "DLU"):
                            if(luser != -1):
                                del users[luser]
                                luser = -1
                                message = "DLU OK\n"
                                #Falta condição para os novos users
                        elif(data[0] == "AUT"):
                            usersfile = open("userslist.txt", 'r')
                            userslist = usersfile.readlines()
                            message = ''
                            for i in range(len(userslist)):
                                log = userslist[i].split()
                                if(log[0] == data[1]):
                                    if(log[1] == data[2]):
                                        print("User: " + data[1])
                                        message = "AUR OK\n"
                                        break
                                    else:
                                        message = "AUR NOK\n"
                                        break
                            usersfile.close()
                            if(luser == -1 and lpassword == -1):
                                parentPipe.send(data[1])
                                parentPipe.send(data[2])
                                luser = data[1]
                            if(message != "AUR OK\n" and message != "AUR NOK\n"):
                                usersfile = open("userslist.txt", 'a')
                                usersfile.write(data[1] + ' ' + data[2] + '\n')
                                usersfile.close()
                                users[data[1]] = data[2]
                                parentPipe.send(data[1])
                                parentPipe.send(data[2])
                                message = "AUR NEW\n"
                                print("New user: " + data[1])
                        elif(data[0] == "BCK"):
                            print(data[0] +  ' ' + luser + ' ' + data[1] + ' ' + str(socket.gethostbyname(socket.gethostname())) + ' ' + str(BSport))
                            num = data[2]
                            CSusersfiles = open("backup_list.txt", 'r')
                            userslist = CSusersfiles.readlines()
                            found_user = 0
                            for i in range(len(userslist)):
                                if(userslist[i] == luser + ' ' + data[1] + 'localhost' + str(BSport) + '\n'):
                                    found_user = 1
                            CSusersfiles.close()
                            if not found_user:
                                CSusersfiles = open("backup_list.txt", 'a')
                                IPBS = 'localhost' #This has to be changed if we want to try it out with another machine
                                CSusersfiles.write(luser + ' ' + data[1] + ' ' + IPBS + ' ' + str(BSport) + '\n')
                                CSusersfiles.close()

                            parentPipe.send(1)
                            data = connection.recv(1024)
                            while True:
                                if parentPipe.recv() == 2:
                                    message = "BKR " + ' ' + str(socket.gethostbyname(socket.gethostname())) + ' ' + str(BSport) + ' ' + str(num)
                                    connection.sendall(message.encode())
                                    message = data.decode()
                                    break
                        elif data[0] == "LSD":
                            print("List request")
                            CSusersfiles = open("backup_list.txt", 'r')
                            n_dir = CSusersfiles.readlines()
                            fnum = 0
                            message = ''
                            for i in range(len(n_dir)):
                                n_dir[i] = n_dir[i].split()
                                if (luser == n_dir[i][0]):
                                    fnum += 1
                                    message += ' ' + n_dir[i][1]
                            message = "LDR " + str(fnum) + message + '\n'
                            connection.sendall(message.encode())
                        elif data[0] == "LSF":
                            print("Filelist request")
                            parentPipe.send(3)
                            parentPipe.send(data[1])
                            while True:
                                if parentPipe.recv() == 4:
                                    data = parentPipe.recv()
                                    message = 'LFD ' + data[0][0] + ' ' + str(data[0][1]) + ' ' + str(data[2]) + '\n'
                                    for i in range(3,len(data)):
                                        message += data[i] + ' '
                                    message += '\n'
                                    connection.sendall(message.encode())
                                    break
                        elif(data[0] == "DEL"):
                            parentPipe.send(5)
                            parentPipe.send(data[1])
                            while True:
                                result = parentPipe.recv()
                                if result == 6:
                                    message = "DDR NOK\n"
                                else:
                                    message = "DDR OK\n"
                                break
                        elif(data[0] == "RST"):
                            print("Restore " + data[1])
                            CSusersfiles = open("backup_list.txt", 'r')
                            n_dir = CSusersfiles.readlines()
                            for i in range(len(n_dir)):
                                n_dir[i] = n_dir[i].split()
                                if (luser == n_dir[i][0] and data[1] == n_dir[i][1]):
                                    IPBS = n_dir[i][2]
                                    portBS = n_dir[i][3]
                            message = "RSR " + IPBS + ' ' + portBS
                        connection.sendall(message.encode())
                    else:
                        break
            finally:
                connection.close()

    return 0


main()
