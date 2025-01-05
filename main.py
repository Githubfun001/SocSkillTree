import requests
from bs4 import BeautifulSoup
import csv
import re

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

data = []
if table:
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])  # Znajdź wszystkie komórki
        cell_data = [cell.get_text(strip=True) for cell in cells]
        data.append(cell_data)
else:
    print('Nie znaleziono tabeli na stronie.')
print(data)


def process_required_skills(required):
    # Nowa wersja, aby obsługiwać wielosłowne skille poprawnie
    # Używamy re.split, ale musimy zadbać o multi-słowne skille, więc zatrzymujemy wielosłowne frazy w nawiasach
    requirements = re.split(r'\s*(?:and|or)\s*', required)  # Rozdzielamy na 'and' i 'or', ale zachowujemy skille z więcej niż jednym słowem

    processed_requirements = []

    for req in requirements:
        # Spróbujmy wyłapać nazwę skilla z poziomem (np. "Taxes(2)")
        match = re.match(r'([a-zA-Z\s]+?)\((\d+)\)', req)  # Wyciągamy nazwę skilla i liczbę w nawiasach
        if match:
            skill_name = match.group(1).strip()  # Nazwa skilla
            level = match.group(2)  # Poziom skilla
            # Jeśli poziom to (0), to go pomijamy
            if level == '0':  # Usuń (0)
                continue
            elif level == '1':  # Usuń (1)
                processed_requirements.append(skill_name)  # Zostaw tylko nazwę skilla
            else:
                processed_requirements.append(f"{skill_name}({level})")  # Zachowujemy liczbę, jeśli > 1
        else:
            # Jeśli brak liczby w nawiasie, dodajemy tylko nazwę skilla
            processed_requirements.append(req.strip())

    return processed_requirements



# Konwersja danych do słownika zależności
dependencies = {}
for row in data[1:]:  # Pomijamy nagłówki
    if len(row) >= 3:  # Upewniamy się, że wiersz ma co najmniej 3 elementy
        skill, required, _ = row[:3]  # Bierzemy tylko pierwsze 3 elementy
        if required:  # Jeśli są wymagania
            dependencies[skill] = process_required_skills(required)
        else:  # Jeśli brak wymagań
            dependencies[skill] = []

print("Zależności skilli:", dependencies)


# Funkcja do budowania hierarchii
def build_hierarchy(dependencies):
    levels = {}  # Słownik poziomów: poziom -> lista skilli
    visited = set()  # Przetworzone skille

    def add_to_level(skill, current_level):
        if skill in visited:  # Skill już przypisany do poziomu
            return
        visited.add(skill)

        # Dodaj skill do odpowiedniego poziomu
        if current_level not in levels:
            levels[current_level] = []
        levels[current_level].append(skill)

        # Przetwarzaj zależne skille
        for dependent_skill, required_skills in dependencies.items():
            if skill in required_skills:  # Jeśli jest zależność
                add_to_level(dependent_skill, current_level + 1)

    # Zacznij od skilli bez zależności (najniższy poziom)
    for skill, reqs in dependencies.items():
        if not reqs:
            add_to_level(skill, 0)

    return levels

hierarchy = build_hierarchy(dependencies)
print("Hierarchia:", hierarchy)

import networkx as nx
import matplotlib.pyplot as plt

# Budowanie grafu na podstawie hierarchii
def visualize_hierarchy(hierarchy, dependencies):
    G = nx.DiGraph()

    # Dodawanie krawędzi zgodnie z zależnościami
    for skill, reqs in dependencies.items():
        for req in reqs:
            skill_name = re.sub(r'\(\d+\)', '', skill)  # Usuwamy liczbę w nawiasach z nazwy skilla
            req_name = re.sub(r'\(\d+\)', '', req)  # Usuwamy liczbę w nawiasach z nazwy skilla
            G.add_edge(req_name, skill_name)

    # Pozycje węzłów na podstawie hierarchii
    pos = {}
    for level, skills in hierarchy.items():
        for i, skill in enumerate(skills):
            pos[skill] = (i, -level)  # Poziomy w dół (-level)

    # Rysowanie grafu
    plt.figure(figsize=(12, 8))
    nx.draw(
        G, pos, with_labels=True, node_size=2000, node_color="lightblue",
        font_size=10, font_weight="bold", arrowsize=20
    )
    plt.title("Hierarchia skilli")
    plt.show()

visualize_hierarchy(hierarchy, dependencies)
