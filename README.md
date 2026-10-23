CEN437 - Network Programming: Project 01
 Network Diagnostic and Tool Package

Name & Surname: Rohat Sarıgül 
Student ID: 2022556051

 1. Project Overview
This project is a network diagnostic tool developed to practice basic socket programming, time synchronization, and error handling. All modules are written in separate files and connected to both a terminal menu and a graphical interface.

 2. Requirements
- Python 3
- Libraries: socket, struct, time, sys, tkinter

No external packages need to be installed. Everything runs on standard Python libraries.

 3. Files and Modules
-`frontend.py`: Graphical user interface to run the tools with buttons.

-`main.py`: Terminal menu to select and run the modules from the console.

-`makine_bilgisi.py`: Finds and prints the computer's hostname and IP address.

- `echo_test.py`: Starts a TCP server on port 1903, takes data from the client, and sends the exact same data back to test the connection.
  
-`sntp_module.py`: Connects to pool.ntp.org on UDP port 123, gets the current time using a 48-byte packet, and compares it with the local system time.

-`sohbet_modulu.py`: Simple TCP chat tool. It can be started as a server or a client. Messages are shown on the screen and saved into `sohbet_kayitlari.txt`.

- `hata_yonetimi.py`: Changes socket buffer sizes, sets a 2-second timeout, enables non-blocking mode, and catches connection errors.

4. How to Run
Open a terminal in the project folder.

To start the graphical interface:
```bash
python3 frontend.py
To start the terminal menu:

Bash
python3 main.py
5. Usage Examples
Running Diagnostic Tools:
Run python3 main.py and type 1 for Machine Info, 4 for SNTP Time, or 5 for Error Management. The result will be printed on the terminal and it will return to the main menu.

Running the Chat Module:
Open two terminals to test the chat between server and client:

In the first terminal, run python3 main.py, select 3, and type s to start the server.

In the second terminal, run python3 main.py, select 3, and type c to start the client.

Enter the server IP address when asked. You can use 127.0.0.1 if you are testing on the same PC.

Type your messages and press Enter. Type cikis to close the chat. All messages will be saved in sohbet_kayitlari.txt.
