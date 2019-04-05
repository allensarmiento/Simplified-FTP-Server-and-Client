import commands
import codecs
import socket
import sys
import os

SERVER_NAME = '127.0.0.1'
BUFFER_SIZE = 4096

# ***
# getTempSocket
# Create a TCP socket and returns it
# ***
def getTempSocket(client):
    welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        welcome_socket.bind(('', 0))
    except socket.error as err:
        print "[ERROR " + str(err) + " ] Socket was unable to bind"
        return None
    port = welcome_socket.getsockname()[1]
    print "[ACCEPTED] The ephemeral port is", port
    client.send(str(port).encode("UTF-8"))
    welcome_socket.listen(1)
    print "[ACCEPTED] The server is ready to receive"
    client_socket, ip = welcome_socket.accept()
    welcome_socket.close()
    return client_socket

# ***
# getInstruction
# ***
def getInstruction(client, filename):
    temp_socket = getTempSocket(client)
    download = downloadFile(filename, temp_socket)
    if download:
        print "[ACCEPTED]", filename, "has begun downloading"
        complete = client.recv(1).decode("UTF-8")
        if complete == '1':
            print "[SUCCESS]", filename, "download complete"
        else:
            print "[FAILURE]", filename, "was unable to download"
    else:
        print "[ERROR] Could not receive", filename

    temp_socket.close()

def downloadFile(filename, welcome_socket):
    try:
        read_file = codecs.open("server/"+filename, 'rb', encoding="UTF-8")
    except OSError:
        print "[ERROR] Could not open", filename
        welcome_socket.close()
    
    print "[ACCEPTED] Sending", filename
    
    data = read_file.read(1024)
    while data:
        welcome_socket.send(data.encode("UTF-8"))
        data = read_file.read(1024)
    
    print "[SUCCESS] Finished sending", os.path.getsize("server/"+filename)+10
    read_file.close()

    welcome_socket.close()
    return True

# ***
# putInstruction
# ***
def putInstruction(client, filename):
    temp_socket = getTempSocket(client)
    upload = uploadFile(filename, temp_socket)
    if upload == 0:
        print "[FAILURE] Could not upload", filename
        client.send('0'.encode("UTF-8"))
    else:
        print "[SUCCESS]", filename, "upload complete"
        client.send('1'.encode("UTF-8"))

def uploadFile(filename, welcome_socket):
    path_to_file = "server/" + filename
    with codecs.open(path_to_file, "wb", encoding="UTF-8") as f:
        print "[ACCEPTED] File opened"
        while True:
            print("[STATUS] Receiving data...")
            data = welcome_socket.recv(1024).decode("UTF-8")
            if not data:
                break 
            f.write(data)

    f.close()

    print "[SUCCESS] Received", os.path.getsize(filename)
    print "[SUCCESS] Uploading finished"
    welcome_socket.close()
    return True

def lsInstruction(client, instruction):
    for line in commands.getstatusoutput('ls server'):
        file_name = line

def main():
    if len(sys.argv) < 2:
        print "[USAGE] python " + sys.argv[0] + "<port number>"
    port_num = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("[SUCCESS] The socket is ready")
    try:
        server_socket.bind((SERVER_NAME, port_num))
    except socket.error as err:
        print "[ERROR " + str(err) + "] Socket binding failed"
        server_socket.close()
        return
    print "[SUCCESS] Socket was binded successfully"
    server_socket.listen(1)
    print "[STATUS] Currently listening for a client..."
    while True:
        print "[STATUS] The server is waiting for a connection..."
        client, ip = server_socket.accept()
        print "[SUCCESS] A client connected on port", port_num, "with IP address", ip
        while True:
            user_input = client.recv(BUFFER_SIZE).decode("UTF-8")
            if not user_input:
                print "[ERROR] Wrong instruction given from the client"
                break
            num_words = len(user_input.split())
            if num_words == 2:
                instruction, filename = user_input.split()
                if instruction == "get":
                    getInstruction(client, filename)
                elif instruction == "put":
                    putInstruction(client, filename)
                else:
                    print "[ERROR] Invalid instruction was received"
            elif num_words == 1:
                instruction = user_input
                if instruction == "ls":
                    lsInstruction(client, instruction)
                elif instruction == "quit":
                    print "[FINISH] The connection will now close"
                    client.close()
                    server_socket.close()
                    exit(1)
                else:
                    print "[ERROR] Invalid instruction was received"

if __name__ == "__main__":
    main()