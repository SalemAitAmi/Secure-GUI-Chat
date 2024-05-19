#!/usr/bin/python3
import socket
import threading
from dhe import DHE
from customtkinter import *
from PIL import Image
import logging

logging.basicConfig(level=logging.DEBUG, filename='client.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'
PORT = 9090
# Constants for response status
BAD = 'BAD'
OK = 'OK'
DONE = 'DONE'
MAX_MESSAGE_LENGTH = 1024
REQUEST_DELIM = '|||'
DATA_DELIM = '<!>'
 
class Client:
    def __init__(self, host, port):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Try connecting to server; Exit otherwise
            self.server.connect((host, port))
        except:
            print("Failed to connect to server!")
            self.server.close()
            exit(1)
        
        self.dhe = self.encryptTraffic()  # DHE object manages encryption and decryption 
        if self.dhe is not None:
            self.GUI()

    def sendMessage(self):
        message = self.input_box.get().rstrip()
        self.input_box.delete(0, 'end')
        if len(message) > 0:
            self.sendEncrypted('append', message)

    def receive(self):
        print('Start receiving...')
        self.server.settimeout(1)
        while self.receiving:
            try:
                message = self.receiveDecrypted()
                print(message)

                if message:
                    self.message_history.configure(state='normal')
                    self.message_history.insert('end', f'{message}\n')
                    self.message_history.yview('end')
                    self.message_history.configure('disabled')
            except TimeoutError:
                continue
            except Exception as e:
                print("Error in chat receive!", e)
                break
        self.server.setblocking(1)
        print('Stopped receiving...')
        
    def recipientVerify(self):
        recipient = self.recipient_entry.get().rstrip()
        self.sendEncrypted('new', recipient)
        status = self.receiveDecrypted()
        if status == OK:
            self.recipient = recipient
            self.recipient_frame.forget()
            self.chatGUI()
        else:
            #TODO: Add error message to GUI 
            print(f"{recipient} does not exists!")

    def registerVerify(self):
        username = self.username_entry.get().rstrip()
        password = self.password_entry.get().rstrip()
        # Send to server
        message = username + DATA_DELIM + password
        self.sendEncrypted('register', message)

        status = self.receiveDecrypted()
        if status == OK:
            print("Registration Successfull!")
            self.username = username
            self.swapFrame('register-selection')
        else:
            print("User already exists!")

    def loginVerify(self):
        """
        This function verifies the user's login credentials.

        Args:
            self: An instance of the Client class.

        Returns:
            None.

        Raises:
            None.

        Example Usage:
            >>> client = Client(HOST, PORT)
            >>> client.loginVerify()
        """
        # Retrieve creds from GUI
        username = self.username_entry.get().rstrip()
        password = self.password_entry.get().rstrip()
        # Send to server
        message = username + DATA_DELIM + password
        self.sendEncrypted('login', message)
        
        status = self.receiveDecrypted()
        if status == OK:
            print("Login Successfull!")
            self.username = username
            self.swapFrame('login-selection')
        else:
            print("Incorrect username or password!")


    def loadHistory(self, recipient):
        self.sendEncrypted('history', recipient)
        print('Request history')

        self.recipient = recipient
        self.history = []
        while True:
            line = self.receiveDecrypted()
            self.sendEncrypted('control', OK)
            if line == DONE:
                break
            elif line:
                line = line.split(':')
                sender = line[0]
                message = line[1]
                self.history.append((sender, message))

        self.swapFrame('selection-chat')

    def chat2Selection(self):
        self.receiving = False
        self.receive_thread.join()
        self.swapFrame('chat-selection')


    def GUI(self):
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")
        self.root = CTk()
        self.root.geometry("500x550")
        self.root.title("Secure Messaging Chat")
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.large_font = CTkFont(family='Roboto', size=24, weight='bold')
        self.small_font = CTkFont(family='Roboto', size=12, weight='normal')
        self.loginGUI()
        self.root.mainloop()

    def swapFrame(self, swap_string : str):
        print(f"Called swapFrame: {swap_string}")
        match swap_string:
            case 'login-register':
                self.login_frame.forget()
                self.registerGUI()
            case 'login-selection':
                self.login_frame.forget()
                self.selectionGUI()
            case 'register-selection':
                self.register_frame.forget()
                self.selectionGUI()
            case 'selection-chat':
                self.receiving = True
                self.selection_frame.forget()
                self.chatGUI()
            case 'selection-newChat':
                self.receiving = True
                self.selection_frame.forget()
                self.recipientGUI()
            case 'chat-selection':
                self.chat_frame.forget()
                self.selectionGUI()
                #self.selection_frame.pack()

    def chatGUI(self):
        # Load images
        back_arrow_img = CTkImage(Image.open("assets/icon/back_arrow.png"), size=(15, 15))
        # Widget definitions
        self.chat_frame = CTkFrame(master=self.root)
        recipient_label = CTkLabel(master=self.chat_frame, text=self.recipient, font=self.large_font)
        self.message_history = CTkTextbox(master=self.chat_frame, width=350, font=self.small_font, state='disabled')
        input_label = CTkLabel(master=self.chat_frame, text=self.username, font=self.large_font)
        self.input_box = CTkEntry(master=self.chat_frame, placeholder_text='message', font=self.small_font)
        send_button = CTkButton(master=self.chat_frame, text="Send", font=self.small_font, command=self.sendMessage)
        back_button = CTkButton(width=50,master=self.chat_frame, text='', image=back_arrow_img, command=self.chat2Selection)
        # Packing
        back_button.pack(side='top', anchor=NW)
        recipient_label.pack(side='top', pady=20)
        self.message_history.pack(side='top')
        input_label.pack(side='top', pady=15)
        self.input_box.pack(side='top')
        send_button.pack(side='top', pady=30)
        self.chat_frame.pack(fill='both', expand=True)

        if hasattr(self, 'history'):
            self.message_history.configure(state='normal')
            for message in self.history:
                self.message_history.insert('end', f'{message[0]}: {message[1]}\n')
            self.message_history.yview('end')
            self.message_history.configure('disabled')
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def recipientGUI(self):
        # Widget definitions
        self.recipient_frame = CTkFrame(master=self.root, width=400, height=500)
        recipient_label = CTkLabel(master=self.recipient_frame, text="Who would you like to chat with?", font=self.large_font)
        self.recipient_entry = CTkEntry(master=self.recipient_frame, placeholder_text='recipient', font=self.small_font, width=150, height=20)
        submit_button = CTkButton(master=self.recipient_frame, text="Start Chatting", font=self.small_font, command=self.recipientVerify)
        # Packing
        recipient_label.pack(side='top', pady=50)
        self.recipient_entry.pack(side='top', pady=10)
        submit_button.pack(side='top', pady=10)
        self.recipient_frame.pack(fill="both", expand=True)

    def registerGUI(self):
        # Widget definitions
        self.login_frame.forget()
        self.register_frame = CTkFrame(master=self.root, width=400, height=500)
        register_label = CTkLabel(master=self.register_frame, text="Register", font=self.large_font)
        self.username_entry = CTkEntry(master=self.register_frame, placeholder_text='username', font=self.small_font, width=150, height=20)
        self.password_entry = CTkEntry(master=self.register_frame, placeholder_text='password', show='*', font=self.small_font, width=150, height=20)
        register_button = CTkButton(master=self.register_frame, text="Register", font=self.small_font, command=self.registerVerify)
        # Packing
        register_label.pack(side='top', pady=50)
        self.username_entry.pack(side='top', pady=10)
        self.password_entry.pack(side='top', pady=10)
        register_button.pack(side = 'top', pady=20)
        self.register_frame.pack(fill="both", expand=True)

    def loginGUI(self):
        # Widget Definitions
        self.login_frame = CTkFrame(master=self.root, width=400, height=500)
        login_label = CTkLabel(master=self.login_frame, text="Login", font=self.large_font)
        self.username_entry = CTkEntry(master=self.login_frame, placeholder_text='username', font=self.small_font, width=150, height=20)
        self.password_entry = CTkEntry(master=self.login_frame, placeholder_text='password', show='*', font=self.small_font, width=150, height=20)
        login_button = CTkButton(master=self.login_frame, text="Login", font=self.small_font, command=self.loginVerify)
        register_button = CTkButton(master=self.login_frame, text="Register", font=self.small_font, command=lambda: self.swapFrame('login-register'))
        # Packing
        login_label.pack(side='top', pady=50)
        self.username_entry.pack(side='top', pady=10)
        self.password_entry.pack(side='top', pady=10)
        login_button.pack(side = 'top', pady=20)
        register_button.pack(side='top')
        self.login_frame.pack(fill="both", expand=True)

    def selectionGUI(self):
        # Load image
        new_chat_img = CTkImage(Image.open("assets/icon/new_chat_icon.png"), size=(20, 20))
        # Widget Definitions
        self.selection_frame = CTkFrame(master=self.root, width=400, height=500)
        self.selection_frame.pack(padx=20, pady=20)
        selection_label = CTkLabel(master=self.selection_frame, text=self.username, font=self.large_font)
        selection_label.pack(side='top', anchor=NW)
        create_new_chat_button = CTkButton(width=50,master=self.selection_frame, text='New Chat', image=new_chat_img, command=lambda: self.swapFrame('selection-newChat'))
        create_new_chat_button.pack(side='bottom', anchor=S, pady=20)

        selection_list = []
        self.sendEncrypted('selection-list')

        while True:
            response = self.receiveDecrypted()
            self.sendEncrypted('control', OK)
            if response == DONE:
                break
            else:
                selection_list.append(response)

        # Create a button for each existing conversation
        for user in selection_list:
            button_name = CTkButton(master=self.selection_frame, width=400, height=40, text=user, font=self.small_font, command=lambda user=user: self.loadHistory(user))
            button_name.pack(side='top', pady=8)

    def encryptTraffic(self):
        # Initialize DHE instance
        dhe = DHE()
        # Key Exchange Protocol
        try:
            pk1 = int(self.server.recv(1024).decode('utf-8'))
            pk2 = int(self.server.recv(1024).decode('utf-8'))
            dhe.setPublickKey1(pk1)
            print("Public Key 1 (success)")
            dhe.setPublickKey2(pk2)
            print("Public Key 2 (success)")
            dhe.setPrivateKey()
            self.server.send(str(dhe.generatePartialKey()).encode('utf-8'))
            print("Client Partial Key (success)")
            partial_key = int(self.server.recv(1024).decode('utf-8'))
            print("Server Partial Key (success)")
        except Exception as e:
            print("Error Encrypting Traffic!", e)
            return None
        
        # Generate session key from server's partial key
        dhe.generateSessionKey(partial_key)
        print("Traffic Successfully Encrypted!")
        return dhe
    
    def sendEncrypted(self, request, data=None):
        try:
            if data:
                message = request + REQUEST_DELIM + data + REQUEST_DELIM
            else:
                message = request
            logging.debug('Sent: '+message)
            encrypted_message = self.dhe.encryptMessage(message)
            self.server.send((encrypted_message).encode('utf-8'))
        except BlockingIOError:
            pass
        except Exception as e:
            print("Error sending message!", e)

    def receiveDecrypted(self):
        try:
            decrypted_message = self.dhe.decryptMessage(self.server.recv(MAX_MESSAGE_LENGTH).decode('utf-8'))
            if decrypted_message:
                logging.debug('Received: '+decrypted_message)
                return decrypted_message
        except Exception as e:
            raise e
        
    def stop(self):
        print('Shutting down...')
        self.receiving = False
        if hasattr(self, 'receive_thread'):
            self.receive_thread.join()
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        self.root.destroy()
        exit(0)
            

    
if __name__ == '__main__':
    client = Client(HOST, PORT)