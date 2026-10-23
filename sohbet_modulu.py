import socket

def sohbet_kaydet(metin): # Hem server hemde client tarafından her mesajları tek bir dosyaya yazdırmak için fonksiyon tanımlıyoruz.
    with open("sohbet_kayitlari.txt", "a") as f: # Txtimizi oluşturuyoruz.
        f.write(metin) # Gelen mesajı dosyaya yazdırıyoruz.
        f.write("\n")

def sohbet_modulu():
    secim = input("Please select the mode for Server (s), for Client (c): ").strip().lower() # Kullanıcıya Server mı yoksa Client mı olacağını soruyoruz.
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket oluşturuyoruz.

    if secim == 's': # Eğer server modunu seçersek
        my_pc_name = socket.gethostname() # Bilgisayarımdan hostname çekiyorum.
        Ip_address = socket.gethostbyname(my_pc_name) # Hostname ile ip adresimi çekiyorum.
        
        r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Port takılı kalmasın, hemen tekrar açabilsin diye ayar yapıyorum.
        r.bind((Ip_address, 1903)) # Oluşturduğum soketi ip adresime ve 1903 portuna bağlıyorum.
        r.listen(1) # Gelen bağlantı isteklerini dinlemeye başlıyorum.
        
        print(f"Server started on {Ip_address}:1903. Waiting for client...") # Client'tan bağlanırken görebilmek için IP'yi ekrana yazdırıyorum.
        conn, addr = r.accept() # İstemciden gelen bağlantıyı kabul ediyorum.
        print(f"Connected by {addr}. (Çıkmak için 'cikis' yazın)")

        while True:
            gelen = conn.recv(1024).decode('utf-8') # Karşıdan gelen veriyi 1024 byte olarak alıp çözüyorum.
            if not gelen or gelen.lower() == 'cikis': # Eğer 'cikis' yazdıysa veya bağlantı koptuysa döngüyü kırıyoruz.
                print("Client left the chat.")
                break
            
            print(f"Client: {gelen}") 
            print("\n")
            sohbet_kaydet(f"Client: {gelen}") # Gelen mesajı dosyaya kaydediyorum.
            
            cevap = input("Server: ") # Server olarak cevabımı yazıyorum.
            conn.sendall(cevap.encode('utf-8')) # Cevabı encode edip karşı tarafa gönderiyorum.
            sohbet_kaydet(f"Server: {cevap}")
            
            if cevap.lower() == 'cikis': # Ben 'cikis' yazdıysam sohbeti bitiriyorum.
                break

        conn.close() # İstemci bağlantısını kapatıyorum.

    elif secim == 'c': # Eğer client modunu seçersek
        hedef_ip = input("Enter server IP address: ").strip() # Bağlanacağımız sunucunun IP adresini alıyorum.
        v = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket oluşturuyoruz.
        v.connect((hedef_ip, 1903)) # Sunucunun 1903 portuna bağlanıyorum.
        print("Connected to server!") # Çıkmak için 'cikis' yazın

        while True: 
            # Telsiz mantığına göre mesaj gönderip sonra cevap bekliyoruz.
            # Burada conn kullanmıyoruz onun yerine kendi oluşturduğumuz soketimizi kullanıyoruz.
            mesaj = input("Client: ") # Göndereceğim mesajı alıyorum.
            v.sendall(mesaj.encode('utf-8')) # Mesajı sunucuya yolluyorum.
            sohbet_kaydet(f"Client: {mesaj}") # Kendi mesajımı da dosyaya yazdırıyorum.

            if mesaj.lower() == 'cikis':
                break

            gelen = v.recv(1024).decode('utf-8') # Sunucudan gelecek cevabı bekliyorum.
            if not gelen or gelen.lower() == 'cikis':
                print("Server ended the chat.")
                break

            print(f"Server: {gelen}")
            sohbet_kaydet(f"Server: {gelen}") # Sunucunun cevabını dosyaya kaydediyorum.

    else:
        print("Invalid selection!")

    v.close() # İşlem bitince ana soketi kapatıyorum.

if __name__ == "__main__":
    sohbet_modulu()