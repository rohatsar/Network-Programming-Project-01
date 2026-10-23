import socket

def hata_yonetimi():
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Soket oluşturuyoruz.
    r.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1903) # Soket üzerinden veri gönderirken kullanılacak boyutu ayarlıyoruz.
    r.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1903) # Soket üzerinden veri alırken kullanılacak boyutu ayarlıyoruz.
    print(f"Buffer -> Send: {r.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)}, "
          f"Recv: {r.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)}") # Az önce değiştirdiğimiz boyutları kontrol ettirip ekrana yazdırıyoruz.
    r.close() # Soketi kapatıyoruz.

    
    for blocking_mod in [True, False]: # For döngüsünde true gelirse timeout testi yapıyoruz false gelirsede non-blocking mod testi yapıyoruz.
         r_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Soket açıyoruz.
         try:
             if blocking_mod:
                 r_test.settimeout(1.903) # Karşıdan eğer yanıt gelmezse 1.903 saniye sonra fırlat.
                 print("\n")
                 print("Connecting")
             else:
                 r_test.setblocking(False) # Beklemeden direkt fırlatır.
                 print("\n")
                 print("Connecting")

             r_test.connect(("10.255.255.1", 1903)) # Hata tespiti yapmak için bilerek bilinmeyen bir IP adresine bağlanmaya çalışıyoruz.
             
         except socket.timeout: #  Döngü true iken  1.903 saniye sonra hatayı yakalarız.
             print("Error: The connection has expired.") 
         except BlockingIOError: # Döngü false iken anında fırlatır ve hatayı yakalarız.
             print("Error: The operation could not be completed immediately.") 
         except OSError as e: # Tüm işlemlerin  hataları yakalayan güvenlik ağıdır.
             print(f"Socket error: {e}")
         finally:
             r_test.close() # Hangi hata olursa olsun soketi kapatıyoruz.

if __name__ == "__main__":
    hata_yonetimi()