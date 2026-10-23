import os
import socket
import struct
import threading
import time
import tkinter as tk
from tkinter import messagebox

# ==============================================================================
# KLASİK NETWORK OPERATIONS CENTER (NOC) - CYBER NAVY & CYAN RENK PALETİ
# ==============================================================================
BG_DARK = "#070D19"         # Ana Arka Plan (Derin Gece / Ağ Mavisi)
BG_SIDEBAR = "#0C1526"      # Sol Menü ve Üst Bar Zemini
BG_CARD = "#111E34"         # Kart ve Panel Yüzeyi (Koyu Lacivert/Slate)
BG_CARD_HOVER = "#182A47"   # Buton / Kart Hover Yüzeyi
BG_TERMINAL = "#050A14"     # Konsol İç Zemini (Terminal Siyah-Lacivert)
BORDER_COLOR = "#1E3354"    # İnce Ağ Çizgisi / Çerçeve Rengi

TEXT_WHITE = "#F0F6FC"      # Parlak Buz Beyazı Başlıklar
TEXT_SILVER = "#94A3B8"     # Açık Slate Gri Alt Metinler
TEXT_MUTED = "#526D8D"      # İkincil Teknik Metinler

NET_CYAN = "#00D2FF"        # Ana Ağ Vurgu Rengi (Siber Camgöbeği / Cyan)
NET_BLUE = "#0284C7"        # Buton Arka Plan Mavisi (Klasik Network Mavisi)
NET_BLUE_HOVER = "#0369A1"  # Buton Hover Mavisi
STATUS_GREEN = "#10B981"    # Aktif Hat / Başarılı İşlem Yeşili
STATUS_AMBER = "#F59E0B"    # Paket Bekleme / Uyarı Sarısı
STATUS_RED = "#EF4444"      # Bağlantı Hatası Kırmızısı


def sohbet_kaydet(metin):
    """Hem Server hem de Client mesajlarını sohbet_kayitlari.txt dosyasına kaydeder."""
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sohbet_kayitlari.txt")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(metin + "\n")


# ==============================================================================
# DOĞRUDAN ARAYÜZ İÇİ CANLI SOHBET (CHAT) PENCERESİ (SERVER & CLIENT)
# ==============================================================================
class NetworkChatWindow:
    def __init__(self, parent_app, force_role=None):
        self.app = parent_app
        self.win = tk.Toplevel(parent_app.root)
        self.win.title("NetCore • TCP Socket Chat Terminal (Port 1903)")
        self.win.geometry("660x620")
        self.win.minsize(580, 500)
        self.win.config(bg=BG_DARK)

        # Soket ve Bağlantı Durumu
        self.role = tk.StringVar(value=force_role or "server")
        self.sender_choice = tk.StringVar(value="Server")
        self.target_ip_var = tk.StringVar(value="127.0.0.1")
        self.msg_var = tk.StringVar()
        self.status_text_var = tk.StringVar(value="Hazır • Doğrudan Mesaj Yazabilirsiniz")

        self.server_sock = None
        self.active_sock = None
        self.is_connected = False
        self.is_running = False

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

        # Pencere açıldığında otomatik olarak:
        # Port 1903 boşsa Server başlatır, doluysa Client olarak bağlanır!
        self.win.after(150, lambda: self._auto_initialize_socket(force_role))
        self.win.after(250, lambda: self.msg_entry.focus_force())

    def _build_ui(self):
        # 1. Üst Siber Ağ Şeridi (TOP)
        stripe = tk.Frame(self.win, bg=BG_DARK, height=3)
        stripe.pack(side=tk.TOP, fill=tk.X)
        tk.Frame(stripe, bg=NET_BLUE, height=3).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Frame(stripe, bg=NET_CYAN, height=3, width=180).pack(side=tk.LEFT, fill=tk.Y)
        tk.Frame(stripe, bg=BORDER_COLOR, height=3).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 2. Başlık Barı (TOP)
        header = tk.Frame(self.win, bg=BG_SIDEBAR, padx=18, pady=12, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(side=tk.TOP, fill=tk.X)

        title_col = tk.Frame(header, bg=BG_SIDEBAR)
        title_col.pack(side=tk.LEFT)
        tk.Label(
            title_col, text="🌐  TCP SOCKET CHAT TERMINAL",
            font=("Segoe UI", 12, "bold"), bg=BG_SIDEBAR, fg=TEXT_WHITE
        ).pack(anchor="w")
        self.status_lbl = tk.Label(
            title_col, textvariable=self.status_text_var,
            font=("Segoe UI", 8, "bold"), bg=BG_SIDEBAR, fg=STATUS_GREEN
        )
        self.status_lbl.pack(anchor="w", pady=(2, 0))

        # Aynı bilgisayarda 2 ayrı pencere ile Server + Client konuşması yapmak için buton
        clone_btn = tk.Button(
            header, text="+ İkinci Sohbet Penceresi Aç (Client)",
            command=lambda: NetworkChatWindow(self.app, force_role="client"),
            bg=BG_CARD, fg=NET_CYAN, activebackground=NET_BLUE, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 8, "bold"), padx=12, pady=6, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER_COLOR
        )
        clone_btn.pack(side=tk.RIGHT)

        # 3. Bağlantı ve Rol Seçim Paneli (TOP)
        conn_panel = tk.Frame(self.win, bg=BG_CARD, padx=16, pady=10, highlightthickness=1, highlightbackground=BORDER_COLOR)
        conn_panel.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(10, 6))

        role_row = tk.Frame(conn_panel, bg=BG_CARD)
        role_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(role_row, text="MOD:", font=("Segoe UI", 8, "bold"), bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=(0, 8))

        self.btn_role_server = tk.Button(
            role_row, text="📡 SERVER (Port 1903)",
            command=lambda: self.switch_mode("server"),
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2"
        )
        self.btn_role_server.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_role_client = tk.Button(
            role_row, text="💻 CLIENT (Sunucuya Bağlan)",
            command=lambda: self.switch_mode("client"),
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2"
        )
        self.btn_role_client.pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(role_row, text="IP:", font=("Segoe UI", 8, "bold"), bg=BG_CARD, fg=TEXT_SILVER).pack(side=tk.LEFT, padx=(0, 6))

        self.ip_entry = tk.Entry(
            role_row, textvariable=self.target_ip_var, width=15,
            bg=BG_TERMINAL, fg=TEXT_WHITE, insertbackground=NET_CYAN,
            relief=tk.FLAT, font=("Consolas", 10),
            highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=NET_CYAN
        )
        self.ip_entry.pack(side=tk.LEFT, ipady=3, padx=(0, 8))

        self.start_btn = tk.Button(
            role_row, text="↻ Yeniden Bağlan", command=self.start_connection,
            bg="#1A2C49", fg=TEXT_WHITE, activebackground=NET_BLUE, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 8, "bold"), padx=10, pady=4, cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT)

        # 4. ALT MESAJ YAZMA ALANI (ÖNCE PACK EDİLİR Kİ ASLA EKRANDAN TAŞMASIN!)
        input_bar = tk.Frame(self.win, bg=BG_CARD, padx=14, pady=12, highlightthickness=2, highlightbackground=NET_CYAN)
        input_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(6, 16))

        sender_btn = tk.Button(
            input_bar, textvariable=self.sender_choice,
            command=self._toggle_sender_label,
            bg="#1A2C49", fg=NET_CYAN, activebackground=BG_CARD_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"), width=7, pady=6, cursor="hand2"
        )
        sender_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.msg_entry = tk.Entry(
            input_bar, textvariable=self.msg_var,
            bg=BG_TERMINAL, fg=TEXT_WHITE, insertbackground=NET_CYAN,
            relief=tk.FLAT, font=("Segoe UI", 11),
            highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=NET_CYAN
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda _: self.send_message())

        self.send_btn = tk.Button(
            input_bar, text="GÖNDER ▸", command=self.send_message,
            bg=NET_BLUE, fg=TEXT_WHITE, activebackground=NET_BLUE_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=20, pady=6, cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT)

        # 5. ORTA MESAJLAŞMA EKRANI (CHAT FEED)
        feed_frame = tk.Frame(self.win, bg=BG_TERMINAL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        feed_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=16, pady=4)

        scrollbar = tk.Scrollbar(feed_frame, bg=BG_SIDEBAR, troughcolor=BG_TERMINAL, relief=tk.FLAT, width=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_view = tk.Text(
            feed_frame, bg=BG_TERMINAL, fg=TEXT_WHITE,
            height=12,
            font=("Segoe UI", 10), relief=tk.FLAT, padx=14, pady=12,
            spacing1=4, spacing3=4, wrap=tk.WORD, state=tk.DISABLED,
            yscrollcommand=scrollbar.set, cursor="arrow"
        )
        self.chat_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_view.yview)

        # Sohbet ekranına tıklanınca imleci otomatik olarak aşağıdaki yazı kutusuna odakla
        self.chat_view.bind("<Button-1>", lambda _: self.msg_entry.focus_set())

        # Mesaj Balonu Renk Etiketleri
        self.chat_view.tag_config("time", foreground=TEXT_MUTED, font=("Consolas", 8))
        self.chat_view.tag_config("system", foreground=STATUS_AMBER, font=("Segoe UI", 9, "italic"))
        self.chat_view.tag_config("error", foreground=STATUS_RED, font=("Segoe UI", 9, "bold"))
        self.chat_view.tag_config("me_tag", foreground=NET_CYAN, font=("Segoe UI", 10, "bold"))
        self.chat_view.tag_config("me_msg", foreground=TEXT_WHITE, font=("Segoe UI", 10))
        self.chat_view.tag_config("peer_tag", foreground=STATUS_GREEN, font=("Segoe UI", 10, "bold"))
        self.chat_view.tag_config("peer_msg", foreground="#E2E8F0", font=("Segoe UI", 10))

        self._update_role_buttons()
        self._append_system_msg("Aşağıdaki mavi çerçeveli kutuya mesajınızı yazıp Enter'a veya 'GÖNDER' butonuna basabilirsiniz.")

    def _toggle_sender_label(self):
        yeni = "Client" if self.sender_choice.get() == "Server" else "Server"
        self.sender_choice.set(yeni)

    def _update_role_buttons(self):
        if self.role.get() == "server":
            self.btn_role_server.config(bg=NET_BLUE, fg=TEXT_WHITE)
            self.btn_role_client.config(bg="#16243B", fg=TEXT_SILVER)
            self.sender_choice.set("Server")
        else:
            self.btn_role_client.config(bg=NET_BLUE, fg=TEXT_WHITE)
            self.btn_role_server.config(bg="#16243B", fg=TEXT_SILVER)
            self.sender_choice.set("Client")

    def switch_mode(self, new_role):
        self.disconnect()
        self.role.set(new_role)
        self._update_role_buttons()
        self.start_connection()
        self.msg_entry.focus_set()

    def _auto_initialize_socket(self, force_role=None):
        """Pencere açılınca 1903 portunu kontrol eder; boşsa Server kurar, doluysa Client olarak bağlanır."""
        if force_role == "client":
            self.role.set("client")
            self._update_role_buttons()
            self.start_connection()
            return

        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(0.25)
        hedef = self.target_ip_var.get().strip() or "127.0.0.1"
        sonuc = test_sock.connect_ex((hedef, 1903))
        test_sock.close()

        if sonuc == 0:
            self.role.set("client")
            self._update_role_buttons()
            self.start_connection()
        else:
            self.role.set("server")
            self._update_role_buttons()
            self.start_connection()

    def _set_chat_status(self, text, color=STATUS_AMBER):
        self.status_text_var.set(text)
        self.status_lbl.config(fg=color)

    def _append_system_msg(self, text, is_error=False):
        if not self.win.winfo_exists():
            return
        self.chat_view.config(state=tk.NORMAL)
        now = time.strftime("%H:%M:%S")
        self.chat_view.insert(tk.END, f"[{now}] ", "time")
        self.chat_view.insert(tk.END, f"{text}\n", "error" if is_error else "system")
        self.chat_view.see(tk.END)
        self.chat_view.config(state=tk.DISABLED)

    def _append_chat_bubble(self, sender_label, message, is_me=True):
        if not self.win.winfo_exists():
            return
        self.chat_view.config(state=tk.NORMAL)
        now = time.strftime("%H:%M:%S")
        self.chat_view.insert(tk.END, f"[{now}] ", "time")
        tag_lbl = "me_tag" if is_me else "peer_tag"
        tag_txt = "me_msg" if is_me else "peer_msg"
        self.chat_view.insert(tk.END, f"{sender_label}: ", tag_lbl)
        self.chat_view.insert(tk.END, f"{message}\n", tag_txt)
        self.chat_view.see(tk.END)
        self.chat_view.config(state=tk.DISABLED)

    # --------------------------------------------------------------------------
    # SOKET BAĞLANTI MANTIĞI (SERVER VE CLIENT THREAD'LERİ)
    # --------------------------------------------------------------------------
    def start_connection(self):
        self.disconnect()
        self.is_running = True

        if self.role.get() == "server":
            threading.Thread(target=self._server_worker, daemon=True).start()
        else:
            threading.Thread(target=self._client_worker, daemon=True).start()

    def _server_worker(self):
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind(("0.0.0.0", 1903))
            self.server_sock.listen(1)

            local_ip = "127.0.0.1"
            self.win.after(0, lambda: self._set_chat_status(
                f"Sunucu Aktif ({local_ip}:1903) • Doğrudan Yazabilir veya İkinci Pencere Açabilirsiniz", STATUS_GREEN
            ))
            self.win.after(0, lambda: self._append_system_msg(
                f"Server {local_ip}:1903 üzerinde dinlemede. Hemen mesaj yazabilir veya '+ İkinci Sohbet Penceresi Aç' ile karşılıklı konuşabilirsiniz."
            ))

            conn, addr = self.server_sock.accept()
            self.active_sock = conn
            self.is_connected = True

            self.win.after(0, lambda: self._set_chat_status(f"Canlı Bağlantı Kuruldu • İstemci: {addr[0]}:{addr[1]}", STATUS_GREEN))
            self.win.after(0, lambda: self._append_system_msg(f"İstemci ({addr[0]}:{addr[1]}) sohbete katıldı!"))
            self.app.root.after(0, lambda: self.app.log(f"[Sohbet Modülü] İstemci bağlandı: {addr[0]}:{addr[1]}", "success"))

            self._receive_loop(peer_name="Client")
        except OSError:
            pass
        except Exception as e:
            self.win.after(0, lambda err=e: self._append_system_msg(f"Sunucu Hatası: {err}", is_error=True))

    def _client_worker(self):
        hedef_ip = self.target_ip_var.get().strip() or "127.0.0.1"
        try:
            self.win.after(0, lambda: self._set_chat_status(f"{hedef_ip}:1903 sunucusuna bağlanılıyor...", STATUS_AMBER))

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((hedef_ip, 1903))
            sock.settimeout(None)

            self.active_sock = sock
            self.is_connected = True

            self.win.after(0, lambda: self._set_chat_status(f"Canlı Bağlantı Kuruldu • Sunucu: {hedef_ip}:1903", STATUS_GREEN))
            self.win.after(0, lambda: self._append_system_msg(f"Sunucuya ({hedef_ip}:1903) başarıyla bağlandınız!"))
            self.app.root.after(0, lambda: self.app.log(f"[Sohbet Modülü] Client olarak {hedef_ip}:1903 sunucusuna bağlanıldı.", "success"))

            self._receive_loop(peer_name="Server")
        except Exception:
            self.win.after(0, lambda: self._set_chat_status("Yerel Sohbet Modu Aktif (Mesajlar Kaydedilir)", STATUS_GREEN))
            self.win.after(0, lambda: self._append_system_msg("Not: Karşı sunucu bulunamadı, yazdığınız mesajlar doğrudan ekrana ve sohbet_kayitlari.txt dosyasına kaydedilecek."))

    def _receive_loop(self, peer_name):
        while self.is_running and self.active_sock:
            try:
                veri = self.active_sock.recv(1024)
                if not veri:
                    self.win.after(0, lambda: self._append_system_msg(f"{peer_name} bağlantıyı kapattı."))
                    break
                mesaj = veri.decode("utf-8", errors="replace").strip()
                if mesaj.lower() == "cikis":
                    self.win.after(0, lambda: self._append_system_msg(f"{peer_name} 'cikis' yazarak sohbetten ayrıldı."))
                    break

                self.win.after(0, lambda m=mesaj: self._append_chat_bubble(peer_name, m, is_me=False))
                self.app.root.after(0, lambda m=mesaj: self.app.log(f"[Sohbet Gelen] {peer_name}: {m}", "info"))
            except OSError:
                break
        self.is_connected = False

    def send_message(self):
        mesaj = self.msg_var.get().strip()
        if not mesaj:
            return

        kim = self.sender_choice.get()

        if self.is_connected and self.active_sock:
            try:
                self.active_sock.sendall(mesaj.encode("utf-8"))
            except Exception as e:
                self._append_system_msg(f"Soket gönderim uyarısı: {e}", is_error=True)

        self.msg_var.set("")
        self._append_chat_bubble(kim, mesaj, is_me=(kim == "Server"))
        sohbet_kaydet(f"{kim}: {mesaj}")
        self.app.log(f"[Sohbet Kaydedildi] {kim}: {mesaj}", "success")

        if mesaj.lower() == "cikis":
            self._append_system_msg("Sohbet 'cikis' komutuyla sonlandırıldı.")
            self.disconnect()

        self.msg_entry.focus_set()

    def disconnect(self):
        self.is_running = False
        self.is_connected = False
        if self.active_sock:
            try:
                self.active_sock.close()
            except Exception:
                pass
            self.active_sock = None
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
            self.server_sock = None

    def on_close(self):
        self.disconnect()
        self.win.destroy()


# ==============================================================================
# ANA AĞ TEŞHİS VE TOPOLOJİ KONTROL MERKEZİ UYGULAMASI
# ==============================================================================
class NetworkDiagnosticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetCore • Network Diagnostic & Topology Suite | CEN322")
        self.root.geometry("1080x730")
        self.root.minsize(980, 660)
        self.root.config(bg=BG_DARK)

        # Dinamik Durum Değişkenleri (GitHub / Gizlilik için varsayılan olarak maskeli)
        self.privacy_mode = tk.BooleanVar(value=True)
        self.privacy_btn_text = tk.StringVar(value="🔒 Host/IP: Gizli")
        self.echo_msg_var = tk.StringVar(value="NETCORE_ECHO_PACKET // SEQ=1 // PROTO=TCP")
        self.quick_chat_var = tk.StringVar()
        self.quick_role_var = tk.StringVar(value="Server")
        self.hostname_var = tk.StringVar(value="LOCAL-NODE [Gizli]")
        self.ip_var = tk.StringVar(value="***.***.***.***")
        self.clock_var = tk.StringVar(value="00:00:00")
        self.state_var = tk.StringVar(value="ONLINE")

        # Arayüz Bileşenlerini Oluştur
        self._build_top_stripe()
        self._build_header()
        self._build_status_bar()
        self._build_main_layout()

        # Başlangıç Görevleri
        self._update_clock()
        self._fetch_initial_host_info()
        self._print_welcome_banner()

    # --------------------------------------------------------------------------
    # ÜST SİBER ŞERİT VE AĞ TOPOLOJİLİ HEADER (CANVAS)
    # --------------------------------------------------------------------------
    def _build_top_stripe(self):
        stripe = tk.Frame(self.root, bg=BG_DARK, height=3)
        stripe.pack(fill=tk.X, side=tk.TOP)
        tk.Frame(stripe, bg=NET_BLUE, height=3).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Frame(stripe, bg=NET_CYAN, height=3, width=240).pack(side=tk.LEFT, fill=tk.Y)
        tk.Frame(stripe, bg=NET_BLUE, height=3).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_SIDEBAR, height=82, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        left_box = tk.Frame(header, bg=BG_SIDEBAR)
        left_box.pack(side=tk.LEFT, padx=22, pady=12)

        # Özel Çizim Küresel Ağ / Düğüm (Node) Rozeti
        badge = tk.Canvas(left_box, width=52, height=52, bg=BG_SIDEBAR, highlightthickness=0)
        badge.pack(side=tk.LEFT, padx=(0, 14))
        # Dış Radar Çemberi ve İç Ağ Bağlantıları
        badge.create_oval(4, 4, 48, 48, fill="#0F1D33", outline=NET_CYAN, width=2)
        badge.create_oval(14, 4, 38, 48, outline=BORDER_COLOR, width=1)
        badge.create_line(4, 26, 48, 26, fill=BORDER_COLOR, width=1)
        # Ağ Düğümleri (Nodes) ve Bağlantı Hatları
        badge.create_line(16, 17, 36, 17, fill=NET_CYAN, width=2)
        badge.create_line(16, 17, 26, 36, fill=NET_CYAN, width=2)
        badge.create_line(36, 17, 26, 36, fill=NET_CYAN, width=2)
        badge.create_oval(12, 13, 20, 21, fill=NET_CYAN, outline=TEXT_WHITE)
        badge.create_oval(32, 13, 40, 21, fill=STATUS_GREEN, outline=TEXT_WHITE)
        badge.create_oval(22, 32, 30, 40, fill=NET_BLUE, outline=TEXT_WHITE)

        title_box = tk.Frame(left_box, bg=BG_SIDEBAR)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="NETCORE  •  NETWORK DIAGNOSTIC & TOPOLOGY SUITE",
            font=("Segoe UI", 14, "bold"),
            bg=BG_SIDEBAR,
            fg=TEXT_WHITE
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="CEN322 Network Programming  |  TCP/IP, UDP, SNTP & Socket Control Center",
            font=("Segoe UI", 9),
            bg=BG_SIDEBAR,
            fg=TEXT_SILVER
        ).pack(anchor="w", pady=(2, 0))

        # Orta-Sağ Dekoratif Ağ Topolojisi (Network Mesh & Nodes Arka Plan Efekti)
        topo_canvas = tk.Canvas(header, width=250, height=76, bg=BG_SIDEBAR, highlightthickness=0)
        topo_canvas.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        nodes = [(20, 22), (75, 55), (130, 20), (185, 50), (230, 25)]
        for i in range(len(nodes) - 1):
            x1, y1 = nodes[i]
            x2, y2 = nodes[i + 1]
            topo_canvas.create_line(x1, y1, x2, y2, fill="#1E3A5F", width=1, dash=(3, 2))
        topo_canvas.create_line(20, 22, 130, 20, fill="#163052", width=1)
        topo_canvas.create_line(75, 55, 185, 50, fill="#163052", width=1)
        for idx, (nx, ny) in enumerate(nodes):
            col = NET_CYAN if idx % 2 == 0 else STATUS_GREEN
            topo_canvas.create_oval(nx - 4, ny - 4, nx + 4, ny + 4, fill=col, outline="")

        right_box = tk.Frame(header, bg=BG_SIDEBAR)
        right_box.pack(side=tk.RIGHT, padx=22)

        clock_card = tk.Frame(right_box, bg=BG_CARD, padx=14, pady=6, highlightthickness=1, highlightbackground=BORDER_COLOR)
        clock_card.pack(side=tk.RIGHT)

        tk.Label(clock_card, text="SYSTEM UTC/LOCAL TIME", font=("Segoe UI", 7, "bold"), bg=BG_CARD, fg=NET_CYAN).pack(anchor="e")
        tk.Label(clock_card, textvariable=self.clock_var, font=("Consolas", 13, "bold"), bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="e")

        self.privacy_btn = tk.Button(
            right_box, textvariable=self.privacy_btn_text, command=self.toggle_privacy_mode,
            bg=BG_CARD, fg=STATUS_GREEN, activebackground=BG_CARD_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 8, "bold"), padx=10, pady=8, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER_COLOR
        )
        self.privacy_btn.pack(side=tk.RIGHT, padx=(0, 12))

    # --------------------------------------------------------------------------
    # ANA GÖVDE (SOL SIDEBAR + SAĞ DASHBOARD & TERMİNAL)
    # --------------------------------------------------------------------------
    def _build_main_layout(self):
        # Arka planda klasik network ızgara hissi veren ana konteyner
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=12)

        # --- SOL MENÜ (SIDEBAR) ---
        sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=290, highlightthickness=1, highlightbackground=BORDER_COLOR)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="AĞ TEŞHİS MODÜLLERİ",
            font=("Segoe UI", 9, "bold"),
            bg=BG_SIDEBAR,
            fg=NET_CYAN
        ).pack(anchor="w", padx=18, pady=(16, 8))

        self._create_nav_card(
            sidebar, "01", "Makine & Arayüz Bilgisi", "Hostname & IPv4 Adres Tespiti",
            self.run_machine_info
        )
        self._create_nav_card(
            sidebar, "02", "SNTP Zaman Senkronu", "UDP 123 • pool.ntp.org (1.903s)",
            self.run_sntp
        )
        self._create_nav_card(
            sidebar, "03", "TCP Echo Simülasyonu", "Loopback Paket & RTT Doğrulama",
            self.run_echo_test
        )
        self._create_nav_card(
            sidebar, "04", "Hata Yönetimi & Buffer", "1903B Buffer • Blocking / Non-Block",
            self.run_error_mgmt
        )
        self._create_nav_card(
            sidebar, "05", "Canlı Sohbet (TCP Chat)", "Arayüz İçi Server & Client (1903)",
            self.open_chat_window
        )

        tk.Frame(sidebar, bg=BORDER_COLOR, height=1).pack(fill=tk.X, padx=18, pady=12)

        self._create_action_button(
            sidebar, "⚡  TÜM AĞ TESTLERİNİ ÇALIŞTIR", NET_BLUE, NET_BLUE_HOVER, TEXT_WHITE,
            self.run_all_diagnostics
        )
        self._create_action_button(
            sidebar, "🧹  TERMİNALİ TEMİZLE", BG_CARD, BG_CARD_HOVER, TEXT_SILVER,
            self.clear_console
        )

        # Sol menünün altında mini Ağ Topolojisi Durum Kutusu
        net_box = tk.Frame(sidebar, bg=BG_CARD, padx=12, pady=8, highlightthickness=1, highlightbackground=BORDER_COLOR)
        net_box.pack(side=tk.BOTTOM, fill=tk.X, padx=14, pady=12)
        tk.Label(net_box, text="AĞ PROTOKOL YIĞINI", font=("Segoe UI", 7, "bold"), bg=BG_CARD, fg=NET_CYAN).pack(anchor="w")
        tk.Label(net_box, text="• Transport : TCP / UDP (AF_INET)\n• Servis Port: 1903 | NTP: 123", font=("Consolas", 8), bg=BG_CARD, fg=TEXT_SILVER, justify="left").pack(anchor="w", pady=(2, 0))

        # --- SAĞ PANEL (METRİK KARTLAR + INTERAKTİF BAR + KONSOL + ALT YAZI BARI) ---
        right_area = tk.Frame(body, bg=BG_DARK)
        right_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 1. Üst Durum Kartları (3 Sütun)
        cards_row = tk.Frame(right_area, bg=BG_DARK)
        cards_row.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        cards_row.columnconfigure((0, 1, 2), weight=1, uniform="stat")

        self._create_stat_card(cards_row, 0, "YEREL DÜĞÜM (HOSTNAME)", self.hostname_var, "Aktif Ağ İstasyonu")
        self._create_stat_card(cards_row, 1, "YEREL IPv4 ADRESİ", self.ip_var, "Port: 1903  •  Buffer: 1903 B")
        self.state_label = self._create_stat_card(cards_row, 2, "HAT & MODÜL DURUMU", self.state_var, "Timeout Limiti: 1.903 sn")

        # 2. Hızlı Echo Paketi Araç Çubuğu
        toolbar = tk.Frame(right_area, bg=BG_CARD, padx=14, pady=8, highlightthickness=1, highlightbackground=BORDER_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        tk.Label(
            toolbar, text="ECHO PAYLOAD:", font=("Segoe UI", 8, "bold"),
            bg=BG_CARD, fg=NET_CYAN
        ).pack(side=tk.LEFT, padx=(0, 8))

        entry = tk.Entry(
            toolbar, textvariable=self.echo_msg_var,
            bg=BG_TERMINAL, fg=TEXT_WHITE, insertbackground=NET_CYAN,
            relief=tk.FLAT, font=("Consolas", 10),
            highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=NET_CYAN
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 10))
        entry.bind("<Return>", lambda _: self.run_echo_test())

        send_btn = tk.Button(
            toolbar, text="Paketi Gönder ▸", command=self.run_echo_test,
            bg=NET_BLUE, fg=TEXT_WHITE, activebackground=NET_BLUE_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2"
        )
        send_btn.pack(side=tk.LEFT, padx=(0, 6))

        log_btn = tk.Button(
            toolbar, text="📄 Sohbet Kayıtları", command=self.show_chat_logs,
            bg="#1A2C49", fg=TEXT_SILVER, activebackground=BG_CARD_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=4, cursor="hand2"
        )
        log_btn.pack(side=tk.LEFT)

        # 3. Ana Ekran Alt Hızlı Sohbet Yazma Barı (BOTTOM - Her Zaman Görünür)
        quick_chat_bar = tk.Frame(right_area, bg=BG_CARD, padx=14, pady=10, highlightthickness=1, highlightbackground=NET_CYAN)
        quick_chat_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        tk.Label(
            quick_chat_bar, text="💬 HIZLI SOHBET MESAJI:", font=("Segoe UI", 8, "bold"),
            bg=BG_CARD, fg=NET_CYAN
        ).pack(side=tk.LEFT, padx=(0, 8))

        role_toggle = tk.Button(
            quick_chat_bar, textvariable=self.quick_role_var,
            command=lambda: self.quick_role_var.set("Client" if self.quick_role_var.get() == "Server" else "Server"),
            bg="#1A2C49", fg=TEXT_WHITE, activebackground=BG_CARD_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 8, "bold"), width=7, pady=4, cursor="hand2"
        )
        role_toggle.pack(side=tk.LEFT, padx=(0, 8))

        self.quick_chat_entry = tk.Entry(
            quick_chat_bar, textvariable=self.quick_chat_var,
            bg=BG_TERMINAL, fg=TEXT_WHITE, insertbackground=NET_CYAN,
            relief=tk.FLAT, font=("Segoe UI", 10),
            highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=NET_CYAN
        )
        self.quick_chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 10))
        self.quick_chat_entry.bind("<Return>", lambda _: self.send_quick_chat())

        quick_send_btn = tk.Button(
            quick_chat_bar, text="Mesaj Gönder ▸", command=self.send_quick_chat,
            bg=NET_BLUE, fg=TEXT_WHITE, activebackground=NET_BLUE_HOVER, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=14, pady=4, cursor="hand2"
        )
        quick_send_btn.pack(side=tk.RIGHT)

        # 4. Terminal Konsol Alanı (Arka Planında Hafif Siber Ağ Izgarası İle)
        term_wrapper = tk.Frame(right_area, bg=BG_TERMINAL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        term_wrapper.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        term_header = tk.Frame(term_wrapper, bg=BG_SIDEBAR, height=34)
        term_header.pack(fill=tk.X, side=tk.TOP)
        term_header.pack_propagate(False)

        dots = tk.Canvas(term_header, width=60, height=20, bg=BG_SIDEBAR, highlightthickness=0)
        dots.pack(side=tk.LEFT, padx=12, pady=7)
        dots.create_oval(4, 4, 14, 14, fill=STATUS_RED, outline="")
        dots.create_oval(22, 4, 32, 14, fill=STATUS_AMBER, outline="")
        dots.create_oval(40, 4, 50, 14, fill=STATUS_GREEN, outline="")

        tk.Label(
            term_header,
            text="admin@netcore-noc: ~/tcp-ip-analyzer",
            font=("Consolas", 9, "bold"),
            bg=BG_SIDEBAR,
            fg=NET_CYAN
        ).pack(side=tk.LEFT)

        tk.Label(
            term_header,
            text="AF_INET  •  SOCK_STREAM / SOCK_DGRAM",
            font=("Consolas", 8),
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED
        ).pack(side=tk.RIGHT, padx=14)

        text_container = tk.Frame(term_wrapper, bg=BG_TERMINAL)
        text_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = tk.Scrollbar(text_container, bg=BG_SIDEBAR, troughcolor=BG_TERMINAL, relief=tk.FLAT, width=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.console = tk.Text(
            text_container,
            bg=BG_TERMINAL,
            fg=TEXT_WHITE,
            height=12,
            insertbackground=NET_CYAN,
            selectbackground=NET_BLUE,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=16,
            pady=12,
            spacing1=2,
            spacing3=2,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD
        )
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.console.yview)

        # Konsola tıklanınca alttaki hızlı sohbet kutusuna odakla
        self.console.bind("<Button-1>", lambda _: self.quick_chat_entry.focus_set())

        self.console.tag_config("banner", foreground=NET_CYAN, font=("Consolas", 10, "bold"))
        self.console.tag_config("section", foreground="#38BDF8", font=("Consolas", 10, "bold"))
        self.console.tag_config("accent", foreground=NET_CYAN, font=("Consolas", 10, "bold"))
        self.console.tag_config("time", foreground=TEXT_MUTED, font=("Consolas", 9))
        self.console.tag_config("info", foreground="#CBD5E1")
        self.console.tag_config("success", foreground=STATUS_GREEN, font=("Consolas", 10, "bold"))
        self.console.tag_config("warning", foreground=STATUS_AMBER)
        self.console.tag_config("error", foreground=STATUS_RED, font=("Consolas", 10, "bold"))

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=BG_SIDEBAR, height=30, highlightthickness=1, highlightbackground=BORDER_COLOR)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.status_dot = tk.Canvas(bar, width=12, height=12, bg=BG_SIDEBAR, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(16, 6), pady=9)
        self.dot_id = self.status_dot.create_oval(2, 2, 10, 10, fill=STATUS_GREEN, outline="")

        self.status_bar = tk.Label(
            bar,
            text="Ağ Durumu: Çevrimiçi (Online)  |  TCP/UDP Soket Motoru Hazır (Port: 1903)",
            font=("Segoe UI", 8),
            bg=BG_SIDEBAR,
            fg=TEXT_SILVER
        )
        self.status_bar.pack(side=tk.LEFT)

        tk.Label(
            bar,
            text="NETCORE NOC v2.4  •  IEEE 802.3 / IPv4",
            font=("Consolas", 8, "bold"),
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED
        ).pack(side=tk.RIGHT, padx=16)

    # --------------------------------------------------------------------------
    # ÖZEL UI BİLEŞEN OLUŞTURUCULAR (KARTLAR & BUTONLAR)
    # --------------------------------------------------------------------------
    def _create_nav_card(self, parent, code, title, subtitle, command):
        card = tk.Frame(parent, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER_COLOR, cursor="hand2")
        card.pack(fill=tk.X, padx=14, pady=5)

        indicator = tk.Frame(card, bg=BORDER_COLOR, width=4)
        indicator.pack(side=tk.LEFT, fill=tk.Y)

        num_lbl = tk.Label(
            card, text=code, font=("Consolas", 11, "bold"),
            bg="#162642", fg=NET_CYAN, width=3, pady=8
        )
        num_lbl.pack(side=tk.LEFT, padx=(10, 10), pady=10)

        text_box = tk.Frame(card, bg=BG_CARD)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=8)

        lbl_title = tk.Label(text_box, text=title, font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=TEXT_WHITE, anchor="w")
        lbl_title.pack(fill=tk.X)

        lbl_sub = tk.Label(text_box, text=subtitle, font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_SILVER, anchor="w")
        lbl_sub.pack(fill=tk.X)

        arrow = tk.Label(card, text="›", font=("Segoe UI", 14, "bold"), bg=BG_CARD, fg=TEXT_MUTED, padx=10)
        arrow.pack(side=tk.RIGHT)

        widgets = [card, text_box, lbl_title, lbl_sub, arrow, num_lbl]

        def on_enter(_):
            card.config(bg=BG_CARD_HOVER, highlightbackground=NET_CYAN)
            text_box.config(bg=BG_CARD_HOVER)
            lbl_title.config(bg=BG_CARD_HOVER)
            lbl_sub.config(bg=BG_CARD_HOVER)
            arrow.config(bg=BG_CARD_HOVER, fg=NET_CYAN)
            indicator.config(bg=NET_CYAN)
            num_lbl.config(bg=NET_BLUE, fg=TEXT_WHITE)

        def on_leave(_):
            card.config(bg=BG_CARD, highlightbackground=BORDER_COLOR)
            text_box.config(bg=BG_CARD)
            lbl_title.config(bg=BG_CARD)
            lbl_sub.config(bg=BG_CARD)
            arrow.config(bg=BG_CARD, fg=TEXT_MUTED)
            indicator.config(bg=BORDER_COLOR)
            num_lbl.config(bg="#162642", fg=NET_CYAN)

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda _: command())

    def _create_action_button(self, parent, text, bg_col, hover_col, fg_col, command):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg_col, fg=fg_col, activebackground=hover_col, activeforeground=TEXT_WHITE,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"), pady=9, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER_COLOR
        )
        btn.pack(fill=tk.X, padx=14, pady=4)
        btn.bind("<Enter>", lambda _: btn.config(bg=hover_col))
        btn.bind("<Leave>", lambda _: btn.config(bg=bg_col))

    def _create_stat_card(self, parent, col, title, value_var, footer_text):
        padx = (0, 8) if col == 0 else ((4, 4) if col == 1 else (8, 0))
        card = tk.Frame(parent, bg=BG_CARD, padx=14, pady=10, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg=BG_CARD, fg=NET_CYAN).pack(anchor="w")
        val_lbl = tk.Label(card, textvariable=value_var, font=("Consolas", 13, "bold"), bg=BG_CARD, fg=TEXT_WHITE)
        val_lbl.pack(anchor="w", pady=(3, 3))
        tk.Label(card, text=footer_text, font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_SILVER).pack(anchor="w")
        return val_lbl

    # --------------------------------------------------------------------------
    # YARDIMCI METOTLAR (LOGLAMA, SAAT, DURUM GÜNCELLEME)
    # --------------------------------------------------------------------------
    def _update_clock(self):
        self.clock_var.set(time.strftime("%H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def _set_status(self, message, state_text="ONLINE", color=STATUS_GREEN):
        self.status_bar.config(text=f"Ağ Durumu: {message}")
        self.state_var.set(state_text)
        self.state_label.config(fg=color)
        self.status_dot.itemconfig(self.dot_id, fill=color)

    def _get_display_host_info(self):
        """Gerçek socket fonksiyonlarıyla host ve IP bilgisini alır; gizlilik modundaysa maskeler."""
        pc_name = socket.gethostname()
        ip_addr = socket.gethostbyname(pc_name)
        if self.privacy_mode.get():
            return "LOCAL-NODE [Gizli]", "***.***.***.***"
        return pc_name, ip_addr

    def toggle_privacy_mode(self):
        yeni_durum = not self.privacy_mode.get()
        self.privacy_mode.set(yeni_durum)
        if yeni_durum:
            self.privacy_btn_text.set("🔒 Host/IP: Gizli")
            self.privacy_btn.config(fg=STATUS_GREEN)
        else:
            self.privacy_btn_text.set("👁 Host/IP: Açık")
            self.privacy_btn.config(fg=STATUS_AMBER)
        self._fetch_initial_host_info()

    def _fetch_initial_host_info(self):
        try:
            disp_host, disp_ip = self._get_display_host_info()
            self.hostname_var.set(disp_host)
            self.ip_var.set(disp_ip)
        except Exception:
            self.hostname_var.set("LOCAL-NODE")
            self.ip_var.set("127.0.0.1")

    def log(self, message, tag="info", show_time=True):
        if show_time:
            now = time.strftime("%H:%M:%S")
            self.console.insert(tk.END, f"[{now}] ", "time")
        self.console.insert(tk.END, message + "\n", tag)
        self.console.see(tk.END)

    def log_divider(self, title=""):
        if title:
            line = f"━━━ {title} " + "━" * max(5, 58 - len(title))
            self.log(line, "section", show_time=True)
        else:
            self.log("─" * 66, "time", show_time=False)

    def clear_console(self):
        self.console.delete(1.0, tk.END)
        self._print_welcome_banner()
        self._set_status("Terminal temizlendi ve yeni paket analizlerine hazır.", "ONLINE", STATUS_GREEN)

    def _print_welcome_banner(self):
        banner = (
            "╔══════════════════════════════════════════════════════════════════╗\n"
            "║     NETCORE NOC  •  NETWORK DIAGNOSTIC & PACKET ANALYZER v2.4    ║\n"
            "╚══════════════════════════════════════════════════════════════════╝"
        )
        self.log(banner, "banner", show_time=False)
        self.log("Sol menüdeki modüllerden birini seçebilir veya en alttaki kutudan doğrudan sohbet mesajı yazabilirsiniz.\n", "info", show_time=False)

    # --------------------------------------------------------------------------
    # ANA EKRAN ALT HIZLI SOHBET GÖNDERİMİ
    # --------------------------------------------------------------------------
    def send_quick_chat(self):
        mesaj = self.quick_chat_var.get().strip()
        if not mesaj:
            return
        rol = self.quick_role_var.get()
        self.quick_chat_var.set("")
        sohbet_kaydet(f"{rol}: {mesaj}")
        tag = "accent" if rol == "Server" else "success"
        self.log(f"💬 [{rol}] {mesaj}", tag)
        self._set_status(f"Sohbet mesajı gönderildi ve kaydedildi ({rol}).", "CHAT AKTİF", STATUS_GREEN)

    # --------------------------------------------------------------------------
    # MODÜL 1: MAKİNE BİLGİSİ
    # --------------------------------------------------------------------------
    def run_machine_info(self):
        self._set_status("Yerel ağ arayüzü ve host bilgileri taranıyor...", "TARANIYOR", STATUS_AMBER)
        self.log_divider("MODÜL 01 • YEREL MAKİNE & AĞ ARAYÜZÜ BİLGİSİ")
        try:
            disp_host, disp_ip = self._get_display_host_info()
            self.hostname_var.set(disp_host)
            self.ip_var.set(disp_ip)

            self.log(f"✔ Bilgisayar Adı (Hostname) : {disp_host}", "success")
            self.log(f"✔ Yerel IPv4 Adresi         : {disp_ip}", "success")
            self.log(f"✔ Aktif Servis Portu        : 1903 (TCP/UDP)\n", "info")
            self._set_status("Makine ve IPv4 bilgileri başarıyla alındı.", "BAŞARILI", STATUS_GREEN)
        except Exception as e:
            self.log(f"✖ Makine bilgisi alınırken hata oluştu: {e}\n", "error")
            self._set_status("Makine bilgisi hatası!", "HATA", STATUS_RED)

    # --------------------------------------------------------------------------
    # MODÜL 2: SNTP ZAMAN KONTROLÜ (Non-blocking Thread)
    # --------------------------------------------------------------------------
    def run_sntp(self):
        threading.Thread(target=self._sntp_worker, daemon=True).start()

    def _sntp_worker(self):
        self.root.after(0, lambda: self._set_status("pool.ntp.org adresine UDP zaman paketi gönderiliyor...", "SNTP AKTİF", STATUS_AMBER))
        self.root.after(0, lambda: self.log_divider("MODÜL 02 • SNTP ZAMAN SENKRONİZASYONU"))
        self.root.after(0, lambda: self.log("Sunucu: pool.ntp.org:123  |  Protokol: UDP  |  Timeout: 1.903 sn", "info"))

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(1.903)
        data = b'\x1b' + 47 * b'\0'

        try:
            baslangic = time.perf_counter()
            client.sendto(data, ("pool.ntp.org", 123))
            resp, addr = client.recvfrom(1024)
            gecikme_ms = (time.perf_counter() - baslangic) * 1000

            if resp:
                t = struct.unpack('!12I', resp)[10]
                gercek_zaman = t - 2208988800
                fark = abs(time.time() - gercek_zaman)

                self.root.after(0, lambda: self.log(f"✔ Yanıt Veren Sunucu IP  : {addr[0]} ({gecikme_ms:.1f} ms)", "info"))
                self.root.after(0, lambda: self.log(f"✔ Yerel Sistem Saati     : {time.ctime()}", "info"))
                self.root.after(0, lambda: self.log(f"✔ SNTP Atomik Sunucu     : {time.ctime(gercek_zaman)}", "success"))
                self.root.after(0, lambda: self.log(f"✔ Sapma / Fark           : {fark:.3f} saniye — Senkronizasyon Tamam!\n", "success"))
                self.root.after(0, lambda: self._set_status("SNTP zaman senkronizasyonu tamamlandı.", "SENKRON", STATUS_GREEN))
        except socket.timeout:
            self.root.after(0, lambda: self.log("✖ Hata: 1.903 saniye içinde yanıt alınamadı (socket.timeout).\n", "error"))
            self.root.after(0, lambda: self._set_status("SNTP zaman aşımı oluştu.", "TIMEOUT", STATUS_RED))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"✖ Soket Hatası: {e}\n", "error"))
            self.root.after(0, lambda: self._set_status("SNTP bağlantı hatası.", "HATA", STATUS_RED))
        finally:
            client.close()

    # --------------------------------------------------------------------------
    # MODÜL 3: ECHO TEST (Özelleştirilebilir Mesaj ile Lokal Loopback)
    # --------------------------------------------------------------------------
    def run_echo_test(self):
        self._set_status("Loopback Echo testi yürütülüyor...", "TESTTE", STATUS_AMBER)
        self.log_divider("MODÜL 03 • TCP ECHO TEST SİMÜLASYONU")

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            port = server.getsockname()[1]

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", port))

            conn, addr = server.accept()
            test_mesaji = self.echo_msg_var.get().strip() or "NETCORE_ECHO_TEST_PACKET"

            baslangic = time.perf_counter()
            client.sendall(test_mesaji.encode('utf-8'))
            gelen_ham = conn.recv(1024)
            conn.sendall(gelen_ham)
            yanki = client.recv(1024).decode('utf-8')
            rtt_ms = (time.perf_counter() - baslangic) * 1000

            self.log(f"Bağlantı Noktası : 127.0.0.1:{port}  (İstemci: {addr[0]}:{addr[1]})", "info")
            self.log(f"Gönderilen Paket : \"{test_mesaji}\" ({len(gelen_ham)} Byte)", "info")
            self.log(f"Geri Dönen Yankı : \"{yanki}\" (RTT: {rtt_ms:.2f} ms)", "info")

            if test_mesaji == yanki:
                self.log("✔ DOĞRULAMA BAŞARILI: Gönderilen ve yankılanan veri %100 eşleşiyor!\n", "success")
                self._set_status("Echo testi başarıyla doğrulandı.", "BAŞARILI", STATUS_GREEN)
            else:
                self.log("✖ Paket içeriği uyuşmuyor!\n", "error")
                self._set_status("Echo veri uyuşmazlığı!", "HATA", STATUS_RED)

            client.close()
            conn.close()
            server.close()
        except Exception as e:
            self.log(f"✖ Echo Test Hatası: {e}\n", "error")
            self._set_status("Echo testi başarısız.", "HATA", STATUS_RED)

    # --------------------------------------------------------------------------
    # MODÜL 4: HATA YÖNETİMİ VE SOKET BUFFER AYARLARI (Non-blocking Thread)
    # --------------------------------------------------------------------------
    def run_error_mgmt(self):
        threading.Thread(target=self._error_mgmt_worker, daemon=True).start()

    def _error_mgmt_worker(self):
        self.root.after(0, lambda: self._set_status("Soket buffer ve hata yönetimi testleri çalışıyor...", "TESTTE", STATUS_AMBER))
        self.root.after(0, lambda: self.log_divider("MODÜL 04 • HATA YÖNETİMİ & BUFFER (1903 B)"))

        try:
            r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1903)
            r.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1903)
            snd = r.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            rcv = r.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            self.root.after(0, lambda: self.log(f"✔ Soket Buffer Ayarlandı -> SO_SNDBUF: {snd} Byte | SO_RCVBUF: {rcv} Byte", "success"))
            r.close()
        except Exception as e:
            self.root.after(0, lambda: self.log(f"✖ Buffer Ayar Hatası: {e}", "error"))

        for blocking_mod in [True, False]:
            r_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                if blocking_mod:
                    r_test.settimeout(1.903)
                    self.root.after(0, lambda: self.log("▸ [1/2 Blocking Mod] 10.255.255.1:1903 adresine bağlanılıyor (Timeout: 1.903s)...", "warning"))
                else:
                    r_test.setblocking(False)
                    self.root.after(0, lambda: self.log("▸ [2/2 Non-Blocking Mod] 10.255.255.1:1903 anında bağlantı deneniyor...", "warning"))

                r_test.connect(("10.255.255.1", 1903))
            except socket.timeout:
                self.root.after(0, lambda: self.log("  ✔ Beklenen Hata Yakalandı -> socket.timeout (1.903 sn doldu)", "success"))
            except BlockingIOError:
                self.root.after(0, lambda: self.log("  ✔ Beklenen Hata Yakalandı -> BlockingIOError (Anında fırlatıldı)\n", "success"))
            except OSError as e:
                self.root.after(0, lambda err=e: self.log(f"  ✔ Yakalanan OSError -> {err}\n", "info"))
            finally:
                r_test.close()

        self.root.after(0, lambda: self._set_status("Hata yönetimi senaryoları başarıyla tamamlandı.", "BAŞARILI", STATUS_GREEN))

    # --------------------------------------------------------------------------
    # MODÜL 5: DOĞRUDAN ARAYÜZ İÇİ CANLI SOHBET PENCERESİ
    # --------------------------------------------------------------------------
    def open_chat_window(self):
        self.log_divider("MODÜL 05 • CANLI SOHBET ARAYÜZÜ AÇILDI")
        self.log("✔ Doğrudan GUI Sohbet (Server/Client) penceresi başlatıldı.", "success")
        self._set_status("Canlı Sohbet Arayüzü Aktif (Port 1903)", "CHAT AKTİF", STATUS_GREEN)
        NetworkChatWindow(self)

    def show_chat_logs(self):
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sohbet_kayitlari.txt")
        self.log_divider("SOHBET KAYITLARI (sohbet_kayitlari.txt)")
        if not os.path.exists(log_path):
            self.log("Henüz kayıtlı bir sohbet geçmişi bulunamadı.\n", "warning")
            return
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            if not lines:
                self.log("Sohbet kayıt dosyası şu an boş.\n", "warning")
            else:
                for line in lines:
                    tag = "success" if line.startswith("Server:") else "info"
                    self.log(f"  💬 {line}", tag, show_time=False)
                self.log(f"✔ Toplam {len(lines)} mesaj kaydı listelendi.\n", "section")
            self._set_status("Sohbet kayıtları konsola yüklendi.", "ONLINE", STATUS_GREEN)
        except Exception as e:
            self.log(f"✖ Kayıt dosyası okunamadı: {e}\n", "error")

    # --------------------------------------------------------------------------
    # TÜM TESTLERİ SIRAYLA ÇALIŞTIR
    # --------------------------------------------------------------------------
    def run_all_diagnostics(self):
        def _runner():
            self.root.after(0, self.run_machine_info)
            time.sleep(0.3)
            self.root.after(0, self.run_echo_test)
            time.sleep(0.3)
            self._sntp_worker()
            time.sleep(0.3)
            self._error_mgmt_worker()

        threading.Thread(target=_runner, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkDiagnosticApp(root)
    root.mainloop()
