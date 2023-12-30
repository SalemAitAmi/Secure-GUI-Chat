#!/usr/bin/python3
import random
# Implements encryption by using the Diffie-Hellman Key Exchange  
# Do not need to check if keys are co-prime to each other, as the property is inherent between any pair of primes
class DHE:
    # List of primes is declared as a class attribute so the server only needs to maintain one list which avoid collisions of server side private keys. 
    primes = []
    def __init__(self):
        if DHE.primes == []:
            try:
                with open("primes.txt", "r") as file:
                    for line in file:
                        split = line.split(",")
                DHE.primes = [eval(i) for i in split]
            except:
                print("Failed to retrieve list of primes from primes.txt!")
        
        # Instance attributes
        self.public_key_1 = None
        self.public_key_2 = None
        self.__private_key = None
        self.session_key = None

    def setPublickKey1(self, pk1=None):
        # Server is responsible for generating public keys so clients only need to set them
        if pk1 == None:
            self.public_key_1 = random.choice(self.primes)
        else:
            self.public_key_1 = pk1 
    
    def setPublickKey2(self, pk2=None):
        # Server is responsible for generating public keys so clients only need to set them
        # Enforce no collisions between public keys; Ensure pk_2 is large enough by only sampling the top half of primes
        if pk2 == None:
            self.public_key_2 = random.choice(self.primes[int(len(self.primes)/2):])
            while self.public_key_2 == self.public_key_1:
                self.public_key_2 = random.choice(self.primes[int(len(self.primes)/2):])
        else:
            self.public_key_2 = pk2

    def setPrivateKey(self):
        # Private key shouldn't and doesn't need to be visible outside of the class.
        # Enforce no collisions with public keys; private keys should be strictly less than the modulous
        self.__private_key = random.choice(self.primes)
        while self.__private_key ==  self.public_key_1 or self.__private_key >= self.public_key_2-1:
            self.__private_key = random.choice(self.primes)
        # Remove private keys from the class-wide pool to avoid duplicate session keys 
        self.primes.remove(self.__private_key)

    def generatePartialKey(self):
        """Uses the generator, modulous, and secret key to generate a partial key."""
        # If a is prime, then phi(a) = a - 1 (Euler's phi function)
        phi = self.public_key_2 - 1
        # If gcd(a, N) = 1 (i.e. a and N are co-prime), then [a^k mod N] = [a^(k mod phi(N)) mod N]
        reduced_exponent = self.__private_key%phi
        partial_key = (self.public_key_1**reduced_exponent)%self.public_key_2
        return partial_key

    def generateSessionKey(self, partial_key):
        """Uses the modulous, partial key, and secret keyt to generate the session key."""
        # If a is prime, then phi(a) = a - 1 (Euler's phi function)
        phi = self.public_key_2 - 1
        reduced_exponent = self.__private_key%phi
        session_key = (partial_key**reduced_exponent)%self.public_key_2
        self.session_key = session_key
        return session_key

    def encryptMessage(self, message):
        encrypted_message = ""
        key = self.session_key
        for c in message:
            encrypted_message += chr(ord(c)+key)
        return encrypted_message

    def decryptMessage(self, encryptedMessage):
        encrypted_message = ""
        key = self.session_key
        for c in encryptedMessage:
            encrypted_message += chr(ord(c)-key)
        return encrypted_message


if __name__ == '__main__':
    """USAGE EXAMPLE"""
    # Assign keys by randomly selecting a prime number from the list and removing it from the available pool
    # NOTE It doesn't matter if client side private keys collide, as long as the server's private keys don't (i.e. Duplicate session keys impossible)
    server = DHE()
    client = DHE()
    
    server.setPublickKey1()
    server.setPublickKey2()
    server.setPrivateKey()
    client.setPublickKey1(server.public_key_1)
    client.setPublickKey2(server.public_key_2)
    client.setPrivateKey()

    server.generateSessionKey(client.generatePartialKey())
    client.generateSessionKey(server.generatePartialKey())

    print(f"If Session Key 1 == Session Key 2 then all is well! ({server.session_key} == {client.session_key})")
    message = "This is a super-hyper-giga-duper secret message. Don't tell anyone!"
    encryptedMessage = server.encryptMessage(message)
    print("Encrypted: "+encryptedMessage)
    decryptedMessage = client.decryptMessage(encryptedMessage)
    print("Decrypted: "+ decryptedMessage)