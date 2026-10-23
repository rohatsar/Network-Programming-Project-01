import makine_bilgisi
import echo_test
import sohbet_modulu
import sntp_module
import hata_yonetimi

def ana_menu():
    while True: # Kullanıcı çıkış yapana kadar menüyü sürekli ekrana getiriyoruz.
        print("\n--- Network Diagnostic Menu ---")
        print("1. Machine Information")
        print("2. Echo Test")
        print("3. Chat Module")
        print("4. SNTP Time Check")
        print("5. Error Management")
        print("0. Exit")
        
        secim = input("Make your choice: ").strip() # Kullanıcıdan yapmak istediği işlemi alıyoruz.
        
        if secim == '1':
            makine_bilgisi.enter_machine_information() # Makine bilgisi modülündeki fonksiyonu çağırıyoruz.
        elif secim == '2':
            echo_test.start_echo_server() # Echo testi sunucusunu başlatıyoruz.
        elif secim == '3':
            sohbet_modulu.sohbet_modulu() # Sohbet modülünü başlatıyoruz.
        elif secim == '4':
            sntp_module.sntp_zaman_kontrol() # SNTP zaman kontrolü modülünü çalıştırıyoruz.
        elif secim == '5':
            hata_yonetimi.hata_yonetimi() # Hata yönetimi testlerini çalıştırıyoruz.
        elif secim == '0':
            print("Exiting...")
            break # 0 seçilirse döngüyü kırıp programdan çıkıyoruz.
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    ana_menu()

    