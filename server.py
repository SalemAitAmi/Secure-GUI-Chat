#!/usr/bin/python3
import os
import socket
import threading
import time
from dhe import DHE
from db_management import ChatDatabase
import select
import logging

logging.basicConfig(level=logging.DEBUG, filename='server.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'
PORT = 9090
# Constants for login protocol
BAD = 'BAD'
OK = 'OK'
DONE = 'DONE'
MAX_MESSAGE_LENGTH = 1024
REQUEST_DELIM = '|||'
DATA_DELIM = '<!>'


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initialize server
server_socket.bind((HOST, PORT))                                   # Bind to localhost, port 9090
server_socket.listen()                                             # Listen for clients
print(f'Listening on {(HOST, PORT)}')

mutex = threading.Lock()  # Used for safe writes (avoid corrupting database)
sockets_list = [server_socket]
clients_dict = {}
active_threads = []

clients = list()

def login(notified_socket, db, dict, data):
    """Defines the login protocol."""
    try:
        name, password = data.split(DATA_DELIM)
    except Exception as e:
        print("Error Retreiving Login Credentials!", e)
        return False
    
    result_row = db.getUser(name)  # query the user_table for the given credentials.
    if result_row is None or result_row[1] != password:
        sendEncrypted(notified_socket, dict, BAD)
    else:
        sendEncrypted(notified_socket, dict, OK)
        dict['username'] = name
        dict['logged_in'] = True
    return True

def register(notified_socket, db, dict, data):
        try:
            name, password = data.split(DATA_DELIM)
        except Exception as e:
            print('Error Retreiving Registration Credentials!', e)
            return False
        
        status = db.addUser(name, password)
        if status:
            dict['username'] = name
            sendEncrypted(notified_socket, dict, OK)
        else:
            sendEncrypted(notified_socket, dict, BAD)
    

def sendHistory(notified_socket, db , dict, recipient):
    if not recipient:
        print('Client disconected before receiving history!')
        return
    dict['recipient'] = recipient

    conversation_history = db.getConversation(dict['username'], recipient)
    if conversation_history is None:
        db.createConversation(dict['username'], recipient)
        return
    
    for row in conversation_history:
        message = f"{row[0]}: {row[1]}"  # Construct message
        sendEncrypted(notified_socket, dict, message)   # Send message
        request_data = receiveDecrypted(notified_socket, dict)
        _, status, _ = request_data.split(REQUEST_DELIM)
        if status == OK:
            continue
        else:
            # TODO: add mid-transaction error handling 
            pass
    sendEncrypted(notified_socket, dict, DONE)
    print("History Sent!")

def newChat(notified_socket, db, dict, data):
    status = db.createConversation(dict['username'], data)
    if status:
        dict['recipient'] = data
        sendEncrypted(notified_socket, dict, OK)
    else:
        sendEncrypted(notified_socket, dict, BAD)


def sendRecipientList(notified_socket, db, dict):
    username = dict['username']
    conversation_list = db.getAllTables()
    for conversation in conversation_list[1:]:
        cur = conversation[0].split('_')

        if cur[1] == username:
            sendEncrypted(notified_socket, dict, cur[2])
            request_data = receiveDecrypted(notified_socket, dict)
            _, status, _ = request_data.split(REQUEST_DELIM)
            if status == OK: 
                continue
        elif cur[2] == username:
            sendEncrypted(notified_socket, dict, cur[1])
            request_data = receiveDecrypted(notified_socket, dict)
            _, status, _ = request_data.split(REQUEST_DELIM)
            if status == OK: 
                continue

        

    sendEncrypted(notified_socket, dict, DONE)


def appendConvo(notified_socket, db, dict, data):
    # Whenever an existing conversation is appended:
    # - Update the database 
    # - Resend the message to the sender (maintain consistency between chat renderings)
    # - If the recipient is online, send the message to them 
    sender = dict['username']
    receiver = dict['recipient']

    status = db.appendConversation(sender, receiver, data)
    if not status:
        return # Consider error handling (raise maybe)
    message = sender + ': ' + data
    sendEncrypted(notified_socket, dict, message)

    for client_sock in clients_dict:
        if clients_dict[client_sock]['username'] == receiver:
            sendEncrypted(client_sock, clients_dict[client_sock], message)

def encryptTraffic(client_conn : socket.socket):
    """Encrypt traffic between the client and server by using the Diffie-Hellman Key Exchange protocol."""
    dhe = DHE()           # Initialize Diffie-Hellman Key Exchange instance
    dhe.setPublickKey1()  # Select public key 1, 
    dhe.setPublickKey2()  # public key 2,
    dhe.setPrivateKey()   # and the private key uniformly at random from the pool of primes
    time.sleep(1)         # Sleep to give client enough time to initialize
    
    try:
        client_conn.send(str(dhe.public_key_1).encode('utf-8'))           # Send Public Key 1 (generator)
        print("Public Key 1 (success)")
        client_conn.send(str(dhe.public_key_2).encode('utf-8'))           # Send Public Key 2 (modulous)
        print("Public Key 2 (success)")
        client_partial_key = int(client_conn.recv(1024).decode('utf-8'))  # Wait to receive the client's Partial Key
        print("Client Partial Key (success)")
        client_conn.send(str(dhe.generatePartialKey()).encode('utf-8'))   # Send server's partial key
        print("Server Partial Key (success)")
    except Exception as e:
        print("Error Encrypting Traffic!", e)                             # If any exception occurs, print it, and return None 
        return None
    
    dhe.generateSessionKey(client_partial_key)  # Generate session key and return DHE() instance
    print("Traffic Successfully Encrypted!")
    return dhe

def sendEncrypted(client_socket : socket.socket, client_dict : dict, message : str):
    """Send an encrypted message to the specified client."""
    try:
        logging.debug('Sent: '+message)
        encrypted_message = client_dict['dhe'].encryptMessage(message)
        client_socket.send(encrypted_message.encode('utf-8'))
    except BlockingIOError:
        pass
    except Exception as e:
        print("Error sending message!", e)

def receiveDecrypted(client_socket : socket.socket, client_dict : dict):
    """Receive an ecnrypted message from the specified client and decrypt it."""
    try:
        encrypted_message = client_socket.recv(MAX_MESSAGE_LENGTH).decode('utf-8')
    except BlockingIOError:
        pass
    else:
        if encrypted_message:
            decrypted_message = client_dict['dhe'].decryptMessage(encrypted_message)
            logging.debug('Received: '+decrypted_message)
            return decrypted_message
        else:
            raise RuntimeError("Connection closed!")

    
def service_request(notified_socket, dict, recurse_req=None):
    db = ChatDatabase('chat_database')
    if not recurse_req:
        try: 
            request_data = receiveDecrypted(notified_socket, dict)
            request_data = request_data.split(REQUEST_DELIM)
            req_size = len(request_data)
            if req_size == 3:
                request, data, _ = request_data
            elif req_size == 1:
                request = request_data[0]
            elif req_size > 3:
                request = request_data[0]
                data = request_data[1]
                next_req = request_data[2:]
        except RuntimeError:
            print(f'Client ({client_address}) disconected before sending request!')
            return        
    else:
        pass

    
    match request:
        case 'login':
            logged_in = login(notified_socket, db, dict, data)
            if logged_in:
                dict['logged_in'] = logged_in
                print(f'{dict["username"]} Logged In!')
        case 'register':
            registered = register(notified_socket, db, dict, data)
            if registered:
                dict['logged_in'] = registered
        case 'selection-list':
            print('Sending recipient list...')
            sendRecipientList(notified_socket, db, dict)
        case 'history':
            print('Sending history...')
            sendHistory(notified_socket, db, dict, data)
        case 'new':
            print('Creating new chat...')
            newChat(notified_socket, db, dict, data)
        case 'append':
            print('Appending conversation...')
            appendConvo(notified_socket, db, dict, data)
        case 'disconnect':
            pass

    if 'next_req' not in locals():
        with mutex:
            active_threads.remove(threading.current_thread())
            sockets_list.append(notified_socket)
    else:
        service_request(notified_socket, dict, next_req)


if __name__ == '__main__':
    if not os.path.isfile('chat_database'):
        os.system('python init_database.py')
    while True:
        print(f"listening for {len(sockets_list)} sockets!")
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list, 1)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                # When a new connection is detected:
                # - Accept it 
                # - Encrypt its traffic using DHE
                # - Initialize and store a client dictionary
                # - And append sockets_list with the client socket

                client_socket, client_address = server_socket.accept()

                dhe = encryptTraffic(client_socket)
                if dhe is None:
                    print(f"Error Encrypting Traffic with {client_address}!")
                    continue

                with mutex:
                    clients_dict[client_socket] = {'dhe' : dhe, 'username' : None, 'recipient' : None, 'logged_in' : False, 'addr' : client_address}
                    sockets_list.append(client_socket)
            else:
                # When an accepted socket is notified:
                # - Start a thread to service its request
                # - Remove that socket from the list of sockets to be notified
                # - And store the thread handle
                print(f"Client {clients_dict[notified_socket]['addr']} notified!")
                p = threading.Thread(target=service_request, args=(notified_socket, clients_dict[notified_socket]))
                with mutex:
                    active_threads.append(p)
                    sockets_list.remove(notified_socket)
                p.start()
        for notified_socket in exception_sockets:
            with mutex:
                sockets_list.remove(notified_socket)
                del clients_dict[notified_socket]