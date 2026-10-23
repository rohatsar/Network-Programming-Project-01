import socket
import struct
import time

def sntp_zaman_kontrol():
    NTP_SERVER = "pool.ntp.org" # Zaman bilgisini çekeceğimiz genel NTP sunucusunu belirliyoruz.
    TIME1970 = 2208988800 # 1900 ile 1970 yılları arasındaki saniye farkını tutuyoruz.
    
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SNTP'de UDP protokolü kullanıldığı için UDP soketi oluşturuyoruz.
    client.settimeout(1.903) # Sunucudan yanıt gelmezse 1.903 saniye bekleyip zaman aşımına düşmesini sağlıyoruz.
    
    
    data = b'\x1b' + 47 * b'\0' # Sunucudan saati istemek için 48 baytlık standart SNTP paketini hazırlıyoruz.
    
    try:
        print(f"\n[SNTP Modülü] {NTP_SERVER} adresine zaman isteği yollanıyor...")
        client.sendto(data, (NTP_SERVER, 1903)) # Hazırladığımız paketi belirlediğimiz port üzerinden sunucuya yolluyoruz.
        
        data, address = client.recvfrom(1024) # Sunucudan gelen yanıtı 1024 byte olarak alıyoruz.
        if data: # Eğer sunucudan veri geldiyse işlemlere başlıyoruz.
            t = struct.unpack('!12I', data)[10] # Gelen bayt verisini çözüp içinden 10. sıradaki zaman bilgisini çekiyoruz.
            gercek_zaman = t - TIME1970 # Çektiğimiz zamandan 1970 farkını çıkararak güncel zamana ulaşıyoruz.
            
            print("Zaman bilgisi başarıyla alındı:")
            print("Sistem Zamanı:", time.ctime()) # Bilgisayarımızın kendi saatini ekrana yazdırıyoruz.
            print("SNTP Sunucu Zamanı:", time.ctime(gercek_zaman)) # Sunucudan aldığımız gerçek saati okunabilir formata çevirip yazdırıyoruz.
            
    except socket.timeout: # 1.903 saniye içinde yanıt gelmezse zaman aşımı hatasını yakalıyoruz.
        print("Hata: SNTP sunucusuna bağlanırken zaman aşımı oluştu.")
    except socket.error as e: # Bağlantıda veya sokette başka bir sorun çıkarsa hatayı burada yakalıyoruz.
        print(f"Soket hatası oluştu: {e}")
    finally:
        client.close() # İşlem bitince her durumda soketi kapatıyoruz.
        print("SNTP soketi kapatıldı.\n")

if __name__ == "__main__":
    sntp_zaman_kontrol()