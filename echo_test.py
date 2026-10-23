import socket

def start_echo_server():
    
    my_pc_name = socket.gethostname() # Bilgisayarımdan hostname çekiyorum.

    Ip_address = socket.gethostbyname(my_pc_name) # Bilgisayarımdan hostname ile ip adresimi çekiyorum.
    a=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4 ve TCP protokolünü kullanacağımı belirtiyorum.
    a.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Portu hemen bana açabilmesi için ayarı yapıyorum.

    a.bind((Ip_address, 1903)) # Oluşturduğum soketi ıp adresime ve belirlediğim porta bağlıyorum.
    a.listen() # Gelen bağlantı isteklerini dinlemeye başlıyorum.

    conn, addr = a.accept() # İstemciden gelen bağlantıyı kabul ediyorum.

    data=conn.recv(1024) # Bağlanan istemciden gelen veriyi alıyorum.


    if not data: # Bağlantı koparsa ya da veri gelmezse diye kontrol ediyorum.
        print("Warning: The client has not sent data or the connection has been lost!")
    else:
        conn.sendall(data)# Yankı testi mantığına göre gelen veriyi değiştirmeden geri yolluyorum.
        print("The echo was successfully sent.")  
        
    conn.close()
    a.close()