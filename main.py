import requests
from bs4 import BeautifulSoup
import csv

def scrape_site(url: str, headers: dict[str, str]) -> str:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f'Błąd podczas pobierania strony: {response.status_code}')


def scrape_table(html_content: str, index: int):
    soup = BeautifulSoup(html_content, 'html.parser')

    tables = soup.find_all('table')
    table = tables[index]

    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            cell_data = [cell.get_text(strip=True) for cell in cells]
            print(cell_data)
    else:
        print('Nie znaleziono tabeli na stronie.')





def main():
    url = 'https://soc.th.gl/wielders/Cecilia'
    headers = {'User-Agent': 'Mozilla/5.0'}
    html_content = scrape_site(url, headers)

    table_index = 1
    scrape_table(html_content, table_index)



if __name__ == '__main__':
    main()
