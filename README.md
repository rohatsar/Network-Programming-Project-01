# CEN437 - Network Programming: Project 01
## Network Diagnostic and Tool Package

**Name:** Rohat Sarıgül
**Student ID:** 2022556051

### 1. About This Project
In this project, I made a small network tool package with Python. I used it to learn socket programming, time synchronization and error handling. Every part is in a different file. You can use the tools from the terminal menu or from the graphical interface.

### 2. What You Need
- Python 3
- These libraries: socket, struct, time, sys, tkinter

You don't need to install anything. All libraries come with Python.

### 3. Files
- `frontend.py`: The graphical interface. You can run the tools with buttons.
- `main.py`: The terminal menu. You choose a number and the tool starts.
- `makine_bilgisi.py`: Shows the hostname and the IP address of the computer.
- `echo_test.py`: Opens a TCP server on port 1903. It sends back the same data that the client sends. I use it to test the connection.
- `sntp_module.py`: Connects to pool.ntp.org on UDP port 123. It sends a 48-byte packet, gets the time, and compares it with the time of my computer.
- `sohbet_modulu.py`: A simple TCP chat. You can open it as a server or as a client. The messages are shown on the screen and saved in `sohbet_kayitlari.txt`.
- `hata_yonetimi.py`: Changes the socket buffer sizes, sets a 2-second timeout, and tries non-blocking mode. It also catches connection errors.

### 4. How to Run
Open a terminal in the project folder.

For the graphical interface:
```bash
python3 frontend.py
```

For the terminal menu:
```bash
python3 main.py
```

### 5. Examples

**Diagnostic tools**
Run `python3 main.py`. Then type `1` for Machine Info, `4` for SNTP Time, or `5` for Error Management. The result is shown in the terminal, and then the program goes back to the main menu.

**Chat module**
You need two terminals to test the chat:

1. In the first terminal, run `python3 main.py`, choose `3`, and type `s` to start the server.
2. In the second terminal, run `python3 main.py`, choose `3`, and type `c` to start the client.
3. Write the server IP address when the program asks. If you test on the same computer, use `127.0.0.1`.
4. Write your message and press Enter. Type `cikis` to close the chat. All messages are saved in `sohbet_kayitlari.txt`.
