import socket

def enter_machine_information():
    
    my_pc_name = socket.gethostname() # Bilgisayarımdan hostname çekiyorum.
    Ip_address = socket.gethostbyname(my_pc_name) # Bilgisayarımdan hostname ile ip adresimi çekiyorum.

    print("Pc name:", my_pc_name)
    print("IP Address:", Ip_address)