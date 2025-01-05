import requests
from bs4 import BeautifulSoup
import csv

url = 'https://soc.th.gl/wielders/Cecilia'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    html_content = response.text
else:
    print(f'Błąd podczas pobierania strony: {response.status_code}')

soup = BeautifulSoup(html_content, 'html.parser')

# Przykład: Znalezienie wszystkich wierszy w tabeli
allTables = soup.find_all('table')  # Znajdź tabelę (upewnij się, że to właściwa tabela)
table = allTables[1]

if table:
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])  # Znajdź wszystkie komórki
        cell_data = [cell.get_text(strip=True) for cell in cells]
        print(cell_data)
else:
    print('Nie znaleziono tabeli na stronie.')

