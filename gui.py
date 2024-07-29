import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from database import UserDatabase, ClimateDataDatabase

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Veri Yönetim Sistemi")
        self.geometry("800x600")
        
        # Veritabanı bağlantıları
        self.user_db = UserDatabase('/Users/andalib/Desktop/database/user_data.db')
        self.climate_db = ClimateDataDatabase('/Users/andalib/Desktop/database/İklim_Data.db', '/Users/andalib/Desktop/database/İklim_Data.xlsx')
        
        # GUI bileşenleri oluştur
        self.create_widgets()
    
    def create_widgets(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(pady=20)
        
        self.register_button = tk.Button(self.login_frame, text="Kayıt Ol", command=self.show_registration)
        self.register_button.pack(pady=5)
        
        self.login_button = tk.Button(self.login_frame, text="Giriş Yap", command=self.show_login)
        self.login_button.pack(pady=5)
    
    def show_registration(self):
        self.login_frame.pack_forget()
        self.register_frame = tk.Frame(self)
        self.register_frame.pack(pady=20)
        
        tk.Label(self.register_frame, text="Adınız:").grid(row=0, column=0)
        tk.Label(self.register_frame, text="Soyadınız:").grid(row=1, column=0)
        tk.Label(self.register_frame, text="E-posta:").grid(row=2, column=0)
        tk.Label(self.register_frame, text="Şifre:").grid(row=3, column=0)
        
        self.first_name_entry = tk.Entry(self.register_frame)
        self.last_name_entry = tk.Entry(self.register_frame)
        self.email_entry = tk.Entry(self.register_frame)
        self.password_entry = tk.Entry(self.register_frame, show="*")
        
        self.first_name_entry.grid(row=0, column=1)
        self.last_name_entry.grid(row=1, column=1)
        self.email_entry.grid(row=2, column=1)
        self.password_entry.grid(row=3, column=1)
        
        self.register_submit_button = tk.Button(self.register_frame, text="Kaydol", command=self.register_user)
        self.register_submit_button.grid(row=4, columnspan=2, pady=10)
        
        self.back_button = tk.Button(self.register_frame, text="Geri", command=self.go_back)
        self.back_button.grid(row=5, columnspan=2, pady=5)
    
    def show_login(self):
        self.login_frame.pack_forget()
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(pady=20)
        
        tk.Label(self.login_frame, text="E-posta:").grid(row=0, column=0)
        tk.Label(self.login_frame, text="Şifre:").grid(row=1, column=0)
        
        self.login_email_entry = tk.Entry(self.login_frame)
        self.login_password_entry = tk.Entry(self.login_frame, show="*")
        
        self.login_email_entry.grid(row=0, column=1)
        self.login_password_entry.grid(row=1, column=1)
        
        self.login_submit_button = tk.Button(self.login_frame, text="Giriş Yap", command=self.login_user)
        self.login_submit_button.grid(row=2, columnspan=2, pady=10)
        
        self.back_button = tk.Button(self.login_frame, text="Geri", command=self.go_back)
        self.back_button.grid(row=3, columnspan=2, pady=5)
    
    def register_user(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if first_name and last_name and email and password:
            if self.user_db.register_user(first_name, last_name, email, password):
                messagebox.showinfo("Başarı", "Kayıt başarılı!")
                self.go_back()
            else:
                messagebox.showerror("Hata", "Bu e-posta ile zaten kayıtlı bir kullanıcı bulunuyor.")
        else:
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")
    
    def login_user(self):
        email = self.login_email_entry.get()
        password = self.login_password_entry.get()
        
        if self.user_db.login_user(email, password):
            self.login_frame.pack_forget()
            self.data_frame = tk.Frame(self)
            self.data_frame.pack(fill=tk.BOTH, expand=True)
            
            # Configure grid layout for uniform button sizes
            for i in range(5):
                self.data_frame.grid_columnconfigure(i, weight=1, uniform="button")
            
            self.create_button = tk.Button(self.data_frame, text="Yeni Veri Oluştur", command=self.create_record)
            self.create_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            
            self.delete_button = tk.Button(self.data_frame, text="Veriyi Sil", command=self.delete_record)
            self.delete_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            self.update_button = tk.Button(self.data_frame, text="Veriyi Güncelle", command=self.update_record)
            self.update_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
            
            self.view_button = tk.Button(self.data_frame, text="Verileri Görüntüle", command=self.view_records)
            self.view_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
            
            self.logout_button = tk.Button(self.data_frame, text="Çıkış", command=self.logout)
            self.logout_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
            
            # Add search bar
            self.search_frame = tk.Frame(self.data_frame)
            self.search_frame.grid(row=1, column=0, columnspan=5, pady=10, sticky='ew')
            
            tk.Label(self.search_frame, text="Ara:").grid(row=0, column=0, padx=5)
            self.search_entry = tk.Entry(self.search_frame)
            self.search_entry.grid(row=0, column=1, padx=5, sticky='ew')
            self.search_button = tk.Button(self.search_frame, text="Ara", command=self.search_data)
            self.search_button.grid(row=0, column=2, padx=5)
            
            # Add table display
            self.display_data()
        else:
            messagebox.showerror("Giriş Hatası", "Giriş başarısız. E-posta veya şifre yanlış.")

    def search_data(self):
        search_term = self.search_entry.get()
        self.display_data(search_term)

    def display_data(self, search_term=""):
        if hasattr(self, 'tree'):
            self.tree.destroy()
        
        # Create a frame for the Treeview and Scrollbar
        table_frame = tk.Frame(self.data_frame)
        table_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky='nsew')
        
        # Configure the data_frame to expand and fill the available space
        self.data_frame.rowconfigure(2, weight=1)
        self.data_frame.columnconfigure(0, weight=1)
        
        # Create Treeview widget to display the database
        self.tree = ttk.Treeview(table_frame, columns=("Tarih", "Saat", "Dry_Bulb_Temperature", "Wet_Bulb_Temperature", 
                                                       "Atmospheric_Pressure", "Relative_Humidity", "Dew_Point_Temperature", 
                                                       "Global_Solar", "Normal_Solar", "Diffuse_Solar", "Wind_Speed"), show='headings')
        
        # Format columns
        for col in self.tree["columns"]:
            self.tree.column(col, anchor=tk.W, width=120)
            self.tree.heading(col, text=col, anchor=tk.W)
        
        # Add a vertical scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add a horizontal scrollbar
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Insert data into Treeview
        query = "SELECT * FROM iklim_data WHERE " + " OR ".join(f"{col} LIKE ?" for col in self.tree["columns"])
        params = [f"%{search_term}%" for _ in self.tree["columns"]]
        records = self.climate_db.execute_query(query, params, fetch=True)
        
        for record in records:
            self.tree.insert("", tk.END, values=record)
    
    def get_record_input(self):
        # Kullanıcıdan veri girmesini istiyoruz ve bu verileri döndürüyoruz
        return (simpledialog.askstring("Girdi", "Tarih (YYYY-MM-DD):"),
                simpledialog.askstring("Girdi", "Saat (HH:MM:SS):"),
                simpledialog.askstring("Girdi", "Dry Bulb Temperature (°C):"),
                simpledialog.askstring("Girdi", "Wet Bulb Temperature (°C):"),
                simpledialog.askstring("Girdi", "Atmospheric Pressure (kPa):"),
                simpledialog.askstring("Girdi", "Relative Humidity (%):"),
                simpledialog.askstring("Girdi", "Dew Point Temperature (°C):"),
                simpledialog.askstring("Girdi", "Global Solar (W/m²):"),
                simpledialog.askstring("Girdi", "Normal Solar (W/m²):"),
                simpledialog.askstring("Girdi", "Diffuse Solar (W/m²):"),
                simpledialog.askstring("Girdi", "Wind Speed (m/s):"))
        
    
    def create_record(self):
        # Kullanıcıdan yeni veri girmesini istiyoruz
        data = self.get_record_input()
        if None in data:
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return
        
        # Yeni veriyi veritabanına ekliyoruz
        self.climate_db.execute_query('''INSERT INTO iklim_data 
                                         (Tarih, Saat, Dry_Bulb_Temperature, Wet_Bulb_Temperature, 
                                          Atmospheric_Pressure, Relative_Humidity, Dew_Point_Temperature, 
                                          Global_Solar, Normal_Solar, Diffuse_Solar, Wind_Speed) 
                                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        self.view_records()
        messagebox.showinfo("Başarı", "Yeni veri oluşturuldu!")
    
    def delete_record(self):
        # Kullanıcının seçtiği satırı silmek için işlemleri yapıyoruz
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Seçim Hatası", "Lütfen silmek istediğiniz veriyi seçin.")
            return
        
        item_values = self.tree.item(selected_item[0], 'values')
        tarih, saat = item_values[0], item_values[1]
        query = "DELETE FROM iklim_data WHERE Tarih = ? AND Saat = ?"
        self.climate_db.execute_query(query, (tarih, saat))
        self.view_records()
        messagebox.showinfo("Başarı", "Veri silindi!")
    
    def update_record(self):
        # Kullanıcının seçtiği satırı güncellemek için işlemleri yapıyoruz
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Seçim Hatası", "Lütfen güncellemek istediğiniz veriyi seçin.")
            return
        
        item_values = self.tree.item(selected_item[0], 'values')
        updated_values = [simpledialog.askstring("Güncelle", f"Yeni değeri girin ({col}):", initialvalue=value)
                          for col, value in zip(self.tree["columns"], item_values)]
        
        if None in updated_values:
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return
        
        query = '''UPDATE iklim_data SET 
                   Tarih = ?, Saat = ?, Dry_Bulb_Temperature = ?, Wet_Bulb_Temperature = ?, 
                   Atmospheric_Pressure = ?, Relative_Humidity = ?, Dew_Point_Temperature = ?, 
                   Global_Solar = ?, Normal_Solar = ?, Diffuse_Solar = ?, Wind_Speed = ?
                   WHERE Tarih = ? AND Saat = ?'''
        self.climate_db.execute_query(query, (*updated_values, item_values[0], item_values[1]))
        self.view_records()
        messagebox.showinfo("Başarı", "Veri güncellendi!")
    
    def update_table(self, rows):
        # Tabloyu temizliyoruz ve yeni verileri ekliyoruz
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in rows:
            self.tree.insert("", tk.END, values=row)    
    
    def view_records(self):
        # Veritabanındaki tüm verileri alıyoruz ve tabloyu güncelliyoruz
        query = "SELECT * FROM iklim_data"
        rows = self.climate_db.execute_query(query, fetch=True)
        self.update_table(rows)
    
    def logout(self):
        self.data_frame.pack_forget()
        self.create_widgets()
        
    def go_back(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.pack_forget()
        self.login_frame.pack_forget()
        self.create_widgets()

if __name__ == "__main__":
    app = Application()
    app.mainloop()