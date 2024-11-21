import socket
from tkinter import Tk, Label, Entry, Button, Listbox, END, messagebox, filedialog, StringVar, OptionMenu
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading

# ===================== ตัวแปรสำหรับเก็บข้อมูล =====================
allowed_hostnames = []
blocked_hostnames = []
shared_folder = ""
username = ""
password = ""
permissions = "elradfmw"  # ค่าเริ่มต้นสำหรับสิทธิ์

# ===================== ฟังก์ชันหลัก =====================
def resolve_hostnames(hostnames):
    """แปลง Hostname เป็น IP Address"""
    ips = []
    for hostname in hostnames:
        try:
            ip = socket.gethostbyname(hostname)
            ips.append(ip)
        except socket.gaierror:
            print(f"ไม่สามารถแปลงชื่อเครื่อง {hostname} เป็น IP ได้")
    return ips

def select_shared_folder():
    """เปิดหน้าต่างให้ผู้ใช้เลือกโฟลเดอร์ที่ต้องการแชร์"""
    global shared_folder
    folder = filedialog.askdirectory()
    if folder:
        shared_folder = folder
        shared_folder_label.config(text=f"Shared Folder: {shared_folder}")

def start_ftp_server():
    """เริ่มต้น FTP Server"""
    global username, password, permissions
    if not shared_folder:
        messagebox.showerror("Error", "กรุณาเลือกโฟลเดอร์ที่ต้องการแชร์ก่อนเริ่ม FTP Server!")
        return
    if not username or not password:
        messagebox.showerror("Error", "กรุณากรอก Username และ Password ก่อนเริ่ม FTP Server!")
        return

    allowed_ips = resolve_hostnames(allowed_hostnames)
    blocked_ips = resolve_hostnames(blocked_hostnames)

    authorizer = DummyAuthorizer()
    try:
        authorizer.add_user(username, password, shared_folder, perm=permissions)
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถเพิ่มผู้ใช้ได้: {e}")
        return

    class CustomFTPHandler(FTPHandler):
        def on_connect(self):
            client_ip = self.remote_ip
            if client_ip in blocked_ips:
                print(f"การเชื่อมต่อจาก {client_ip} ถูกปฏิเสธ (อยู่ใน Blacklist)")
                self.close()
                return
            if client_ip not in allowed_ips:
                print(f"การเชื่อมต่อจาก {client_ip} ถูกปฏิเสธ (ไม่อยู่ใน Whitelist)")
                self.close()
                return
            print(f"การเชื่อมต่อจาก {client_ip} ได้รับอนุญาต")

    handler = CustomFTPHandler
    handler.authorizer = authorizer

    server = FTPServer(("0.0.0.0", 21), handler)
    print("FTP Server กำลังทำงานที่พอร์ต 21")
    server.serve_forever()

def start_server_thread():
    """รัน FTP Server ใน Thread แยก"""
    server_thread = threading.Thread(target=start_ftp_server)
    server_thread.daemon = True
    server_thread.start()
    messagebox.showinfo("FTP Server", "FTP Server เริ่มทำงานแล้ว!")

def set_user_credentials():
    """ตั้งค่า Username, Password และ Permissions"""
    global username, password, permissions
    username = username_entry.get()
    password = password_entry.get()
    permissions = permission_var.get()
    if username and password:
        messagebox.showinfo("User Settings", "ตั้งค่าผู้ใช้สำเร็จ!")
    else:
        messagebox.showerror("Error", "กรุณากรอก Username และ Password!")

# ===================== ฟังก์ชันจัดการ Whitelist/Blacklist =====================
def add_to_whitelist():
    hostname = whitelist_entry.get()
    if hostname and hostname not in allowed_hostnames:
        allowed_hostnames.append(hostname)
        whitelist_listbox.insert(END, hostname)
        whitelist_entry.delete(0, END)

def remove_from_whitelist():
    selected = whitelist_listbox.curselection()
    if selected:
        hostname = whitelist_listbox.get(selected)
        allowed_hostnames.remove(hostname)
        whitelist_listbox.delete(selected)

def add_to_blacklist():
    hostname = blacklist_entry.get()
    if hostname and hostname not in blocked_hostnames:
        blocked_hostnames.append(hostname)
        blacklist_listbox.insert(END, hostname)
        blacklist_entry.delete(0, END)

def remove_from_blacklist():
    selected = blacklist_listbox.curselection()
    if selected:
        hostname = blacklist_listbox.get(selected)
        blocked_hostnames.remove(hostname)
        blacklist_listbox.delete(selected)

# ===================== สร้างหน้าจอ UI =====================
root = Tk()
root.title("FTP Server Configuration")

# โฟลเดอร์ที่แชร์
Button(root, text="Select Shared Folder", command=select_shared_folder).grid(row=0, column=0, columnspan=3, pady=5)
shared_folder_label = Label(root, text="Shared Folder: None", fg="blue")
shared_folder_label.grid(row=1, column=0, columnspan=3, pady=5)

# กรอก Username และ Password
Label(root, text="Username").grid(row=2, column=0, pady=5)
username_entry = Entry(root)
username_entry.grid(row=2, column=1, pady=5)

Label(root, text="Password").grid(row=3, column=0, pady=5)
password_entry = Entry(root, show="*")
password_entry.grid(row=3, column=1, pady=5)

# เลือกสิทธิ์
Label(root, text="Permissions").grid(row=4, column=0, pady=5)
permission_var = StringVar(root)
permission_var.set("elradfmw")  # ค่าเริ่มต้น
permissions_menu = OptionMenu(root, permission_var, "elradfmw", "elr", "elrad")
permissions_menu.grid(row=4, column=1, pady=5)

Button(root, text="Set User", command=set_user_credentials).grid(row=5, column=0, columnspan=3, pady=10)

# Whitelist
Label(root, text="Whitelist").grid(row=6, column=0, pady=5)
whitelist_entry = Entry(root)
whitelist_entry.grid(row=7, column=0, pady=5)
Button(root, text="Add", command=add_to_whitelist).grid(row=7, column=1, pady=5)
Button(root, text="Remove", command=remove_from_whitelist).grid(row=7, column=2, pady=5)
whitelist_listbox = Listbox(root, height=10, width=40)
whitelist_listbox.grid(row=8, column=0, columnspan=3, pady=5)

# Blacklist
Label(root, text="Blacklist").grid(row=9, column=0, pady=5)
blacklist_entry = Entry(root)
blacklist_entry.grid(row=10, column=0, pady=5)
Button(root, text="Add", command=add_to_blacklist).grid(row=10, column=1, pady=5)
Button(root, text="Remove", command=remove_from_blacklist).grid(row=10, column=2, pady=5)
blacklist_listbox = Listbox(root, height=10, width=40)
blacklist_listbox.grid(row=11, column=0, columnspan=3, pady=5)

# ปุ่มเริ่มเซิร์ฟเวอร์
Button(root, text="Start FTP Server", command=start_server_thread).grid(row=12, column=0, columnspan=3, pady=20)

# ===================== เริ่ม UI =====================
root.mainloop()
