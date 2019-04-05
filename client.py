import commands
import codecs
import socket 
import sys
import os

SERVER_NAME = '127.0.0.1'
BUFFER_SIZE = 4096

# ***
# getEmphemeralSocket
# Creates a socket utilizing a provided port number and server
# ***
def getEphemeralSocket(port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_NAME, int(port)))
    print "[SUCCESS] Connected to the server port ", port
    return client_socket

# ***
# getInstruction
# ***
def getInstruction(socket, input, filename):
    socket.send(input.encode("UTF-8"))
    temp_port = socket.recv(BUFFER_SIZE).decode("UTF-8")
    print "[ACCEPTED] The ephemeral port is", temp_port
    download = downloadFile(filename, temp_port)
    if download:
        print "[SUCCESS] The server has downloaded", filename 
        socket.send('1'.encode("UTF-8"))
    else:
        print "[FAILURE] The server was unable to download", filename
        socket.send('0'.encode("UTF-8"))

def downloadFile(filename, port):
    temp_socket = getEphemeralSocket(port)

    path_to_file = filename
    with codecs.open(path_to_file, "wb", encoding="UTF-8") as f:
        print "[ACCEPTED] File opened to write to"
        while True:
            print "[STATUS] Receiving data..."
            data = temp_socket.recv(1024).decode("UTF-8")
            if not data:
                break 
            f.write(data)

    print "[SUCCESS] Received", os.path.getsize(filename)
    f.close()
    temp_socket.close()
    print "[SUCCESS] File was received successfully"
    return True

# ***
# putInstruction
# ***
def putInstruction(socket, input, filename):
    socket.send(input.encode("UTF-8"))
    temp_port = socket.recv(BUFFER_SIZE).decode("UTF-8")
    print "[ACCEPTED] The ephemeraal port is", temp_port
    upload = uploadFile(filename, temp_port)
    if upload:
        print "[SUCCESS]", filename, "upload is processing"
        confirmation = socket.recv(1).decode("UTF-8")
        if confirmation == '1':
            print "[SUCCESS] The server has received", filename
        else:
            print "[ERROR] The server has not received", filename
    else:
        print "[FAILURE]", filename, "was not able to upload"

def uploadFile(filename, port):
    temp_socket = getEphemeralSocket(port)
    
    try:
        read_file = codecs.open(filename, "rb", encoding="UTF-8")
    except OSError:
        print "[ERROR] Could not open", filename
        temp_socket.close()
        return False
    
    print "[ACCEPTED]", filename, "is now uploading to the server"

    send_buffer = 0
    file_data = read_file.read(1024)
    while file_data:
        temp_socket.send(file_data.encode("UTF-8"))
        file_data = read_file.read(1024)
    
    print "[SUCCESS] Sent", os.path.getsize(filename)+10
    read_file.close()
    temp_socket.close()
    return True

def lsInstruction(socket, input):
    print "[ls -l] Contents of the server:"
    for line in commands.getstatusoutput('ls -l server'):
        print line

def main():
    if len(sys.argv) < 2:
        print "[USAGE] python" + sys.argv[0] + "<port number>"
    SERVER_NAME = "ecs.fullerton.edu"
    port_num = int(sys.argv[1])
    socket = getEphemeralSocket(port_num)

    while True:
        # Get user input. If not valid, keep asking for input
        while True:
            user_input = raw_input('ftp> ')
            num_words = len(user_input.split())
            if num_words == 2:
                instruction, filename = user_input.split()
                if instruction == "get":
                    getInstruction(socket, user_input, filename)
                    break
                elif instruction == "put":
                    putInstruction(socket, user_input, filename)
                    break
                else:
                    print "[ERROR] That is not a valid instruction."
                    print "Instructions available: get | put"
            elif num_words == 1:
                instruction = user_input 
                if instruction == "ls":
                    lsInstruction(socket, user_input)
                elif instruction == "quit":
                    print "[FINISH] The session will now close"
                    socket.send(user_input.encode("UTF-8"))
                    socket.close()
                    exit(1)
                else:
                    print "[ERROR] That is not a valid instruction."
                    print "Instructions available: ls | quit"
            else:
                print "[ERROR] That is not a valid input."
                print "Input must be: <instruction> <filename> or <instruction>"
                print "Instructions available: get | put | ls | quit"

if __name__ == "__main__":
    main()