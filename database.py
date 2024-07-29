import sqlite3
import pandas as pd
import re

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query, params=(), fetch=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall() if fetch else None
        conn.commit()
        conn.close()
        return result

class UserDatabase(Database):
    def __init__(self, db_path):
        super().__init__(db_path)
        self.initialize_db()

    def initialize_db(self):
        query = '''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)'''
        self.execute_query(query)

    def register_user(self, first_name, last_name, email, password):
        query = '''INSERT INTO users (first_name, last_name, email, password) 
                   VALUES (?, ?, ?, ?)'''
        try:
            self.execute_query(query, (first_name, last_name, email, password))
            print("Kayıt başarılı!")
            return True
        except sqlite3.IntegrityError:
            print("Bu e-posta ile zaten kayıtlı bir kullanıcı bulunuyor.")
            return False

    def login_user(self, email, password):
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        user = self.execute_query(query, (email, password), fetch=True)
        if user:
            print("Giriş başarılı!")
            return True
        print("Kayıt bulunamadı veya şifre yanlış.")
        return False

class ClimateDataDatabase(Database):
    def __init__(self, db_path, excel_file_path=None):
        super().__init__(db_path)
        if excel_file_path:
            self.initialize_db_from_excel(excel_file_path)

    def initialize_db_from_excel(self, excel_file_path):
        df = pd.read_excel(excel_file_path)
        df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
        df['Saat'] = pd.to_datetime(df['Saat'], format='%H:%M:%S').dt.strftime('%H:%M:%S')
        
        # Sütun adlarını temizleyin
        cleaned_columns = {col: self.clean_column_name(col) for col in df.columns}
        df.rename(columns=cleaned_columns, inplace=True)

        conn = sqlite3.connect(self.db_path)
        df.to_sql('iklim_data', conn, if_exists='replace', index=False)
        conn.close()
        print("Excel dosyası SQLite veritabanına başarıyla aktarıldı!")

    def clean_column_name(self, col):
        # Parantez içindeki metni ve parantezleri silin
        col = re.sub(r'\(.*?\)', '', col)
        # Belirli özel karakterleri ve ifadeleri temizleyin
        col = re.sub(r'[©%]', '', col)
        col = re.sub(r'W/m2', '', col)  # 'W/m²' ifadesini temizleyin
        col = re.sub(r'[\s\W]+', '_', col)  # Boşlukları ve diğer özel karakterleri _ ile değiştirin
        col = col.strip('_')  # Başındaki ve sonundaki _ karakterlerini temizleyin

        # Sütun adlarını belirli bir formatta düzenleyin
        col = re.sub(r'Atmospheric_Pressure_kPa', 'Atmospheric_Pressure', col)
        return col

    def create_record(self):
        data = self.get_record_input()
        query = '''INSERT INTO iklim_data 
                   (Tarih, Saat, Dry_Bulb_Temperature, Wet_Bulb_Temperature, Atmospheric_Pressure, 
                   Relative_Humidity, Dew_Point_Temperature, Global_Solar, Normal_Solar, 
                   Diffuse_Solar, Wind_Speed) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        self.execute_query(query, data)
        print("Yeni veri oluşturuldu!")

    def delete_record(self):
        tarih = input("Silmek istediğiniz verinin tarihi (YYYY-MM-DD): ")
        saat = input("Silmek istediğiniz verinin saati (HH:MM:SS): ")
        query = "DELETE FROM iklim_data WHERE Tarih = ? AND Saat = ?"
        self.execute_query(query, (tarih, saat))
        print("Veri silindi!" if not self.check_record_exists(tarih, saat) else "Veri silinemedi!")

    def update_record(self):
        tarih, saat = input("Güncellemek istediğiniz verinin tarihi (YYYY-MM-DD): "), input("Saati (HH:MM:SS): ")
        column_name = self.get_column_choice()
        if column_name:
            yeni_deger = input(f"Yeni değer için {column_name} girin: ")
            query = f'''UPDATE iklim_data SET "{column_name}" = ? WHERE Tarih = ? AND Saat = ?'''
            self.execute_query(query, (yeni_deger, tarih, saat))
            print("Veri güncellendi!")

    def view_records(self):
        choice = input("\nVerileri görmek için bir seçenek belirleyin:\n1. Tarihe göre\n2. Saate göre\n3. Tüm verileri göster\nSeçiminiz: ")
        if choice == '1':
            tarih = input("Görmek istediğiniz tarihi girin (YYYY-MM-DD): ")
            query = "SELECT * FROM iklim_data WHERE Tarih = ?"
            rows = self.execute_query(query, (tarih,), fetch=True)
        elif choice == '2':
            saat = input("Görmek istediğiniz saati girin (HH:MM:SS): ")
            query = "SELECT * FROM iklim_data WHERE Saat = ?"
            rows = self.execute_query(query, (saat,), fetch=True)
        elif choice == '3':
            query = "SELECT * FROM iklim_data"
            rows = self.execute_query(query, fetch=True)
        else:
            print("Geçersiz seçim.")
            return

        for row in rows:
            print(row)

    def get_record_input(self):
        return (input("Tarih (YYYY-MM-DD): "), input("Saat (HH:MM:SS): "), input("Dry Bulb Temperature (°C): "),
                input("Wet Bulb Temperature (°C): "), input("Atmospheric Pressure (kPa): "), input("Relative Humidity (%): "),
                input("Dew Point Temperature (°C): "), input("Global Solar (W/m²): "), input("Normal Solar (W/m²): "),
                input("Diffuse Solar (W/m²): "), input("Wind Speed (m/s): "))

    def check_record_exists(self, tarih, saat):
        query = "SELECT * FROM iklim_data WHERE Tarih = ? AND Saat = ?"
        return self.execute_query(query, (tarih, saat), fetch=True)

    def get_column_choice(self):
        columns = ["Dry_Bulb_Temperature", "Wet_Bulb_Temperature", "Atmospheric_Pressure", 
                   "Relative_Humidity", "Dew_Point_Temperature", "Global_Solar", 
                   "Normal_Solar", "Diffuse_Solar", "Wind_Speed"]
        choice = input("\n".join([f"{i+1}. {col}" for i, col in enumerate(columns)]) + "\nSeçiminiz: ")
        return columns[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(columns) else None
