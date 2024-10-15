import requests
from bs4 import BeautifulSoup
import sqlite3
import time

conn = sqlite3.connect('Atlas_charities.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS information (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    charity_name TEXT,
    Province_of_activity TEXT,
    City_of_activity TEXT,
    Area_of_activity TEXT,
    Field_of_activity TEXT,
    Sub_field_of_activity TEXT,
    Target_group TEXT,
    Type_of_assistance TEXT,
    Organization_type TEXT,
    National_ID TEXT,
    Registration_number TEXT,
    Establishment_date TEXT,
    Issuing_authority_of_license TEXT,
    Number_of_beneficiaries TEXT,
    Number_of_employees TEXT,
    Number_of_volunteer_forces TEXT,
    Landline_phone TEXT,
    Mobile_phone TEXT,
    Address TEXT,
    Postal_code TEXT,
    Website TEXT,
    Email TEXT,
    Instagram TEXT,
    Telegram TEXT
)
''')

c.execute('SELECT url FROM atlas_link')
urls = c.fetchall()

def scrape_charity_info(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        data = {}

        fields_map = {
            'استان فعالیت': 'Province_of_activity', 
            'شهر فعالیت': 'City_of_activity', 
            'محدوده فعالیت': 'Area_of_activity', 
            'عرصه فعالیت': 'Field_of_activity', 
            'زیر عرصه فعالیت': 'Sub_field_of_activity',
            'گروه هدف': 'Target_group', 
            'شیوه کمک': 'Type_of_assistance', 
            'نوع سازمان': 'Organization_type', 
            'شناسه ملی': 'National_ID', 
            'شماره ثبت': 'Registration_number', 
            'تاریخ تاسیس': 'Establishment_date', 
            'مرجع صادرکننده مجوز': 'Issuing_authority_of_license', 
            'تعداد مددجویان': 'Number_of_beneficiaries', 
            'تعداد کارمندان': 'Number_of_employees',
            'تعداد نیروهای داوطلب': 'Number_of_volunteer_forces', 
            'تلفن ثابت': 'Landline_phone', 
            'تلفن همراه': 'Mobile_phone', 
            'آدرس': 'Address', 
            'کدپستی': 'Postal_code', 
            'وب سایت': 'Website', 
            'ایمیل': 'Email', 
            'اینستاگرام': 'Instagram', 
            'تلگرام': 'Telegram'
        }

        charity_name_tag = soup.find('h1')
        if charity_name_tag:
            data['charity_name'] = charity_name_tag.text.strip()
        else:
            data['charity_name'] = None

        details = soup.select('#product-fields > div > div > div.col-lg-6')
        for detail in details:
            key_tag = detail.find('div', class_='col-6 col-lg-5')
            value_tag = detail.find('div', class_='col-6 col-lg-7')

            if key_tag and value_tag:
                key = key_tag.text.strip()
                value = value_tag.text.strip()
                if key in fields_map:
                    data[fields_map[key]] = value

        for field in fields_map.values():
            if field not in data:
                data[field] = None
        
        return data

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

for url_tuple in urls:
    url = url_tuple[0]
    charity_data = scrape_charity_info(url)
    
    if charity_data:
        c.execute('''
        INSERT INTO information (
            charity_name, Province_of_activity, City_of_activity, Area_of_activity, Field_of_activity,
            Sub_field_of_activity, Target_group, Type_of_assistance, Organization_type, National_ID,
            Registration_number, Establishment_date, Issuing_authority_of_license, Number_of_beneficiaries,
            Number_of_employees, Number_of_volunteer_forces, Landline_phone, Mobile_phone, Address, 
            Postal_code, Website, Email, Instagram, Telegram
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            charity_data['charity_name'], charity_data['Province_of_activity'], charity_data['City_of_activity'], 
            charity_data['Area_of_activity'], charity_data['Field_of_activity'], charity_data['Sub_field_of_activity'], 
            charity_data['Target_group'], charity_data['Type_of_assistance'], charity_data['Organization_type'], 
            charity_data['National_ID'], charity_data['Registration_number'], charity_data['Establishment_date'], 
            charity_data['Issuing_authority_of_license'], charity_data['Number_of_beneficiaries'], 
            charity_data['Number_of_employees'], charity_data['Number_of_volunteer_forces'], 
            charity_data['Landline_phone'], charity_data['Mobile_phone'], charity_data['Address'], 
            charity_data['Postal_code'], charity_data['Website'], charity_data['Email'], charity_data['Instagram'], 
            charity_data['Telegram']
        ))

        conn.commit()
        print(f"Data from {url} saved successfully.")
    else:
        print(f"Failed to scrape data from {url}")

    time.sleep(1)

conn.close()