import requests
from bs4 import BeautifulSoup
import re
import networkx as nx
import matplotlib.pyplot as plt


def scrape_site(url: str, headers: dict[str, str]) -> str:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f'Błąd podczas pobierania strony: {response.status_code}')
        return ""


def scrape_table(html_content: str, index: int) -> list[list[str]]:
    soup = BeautifulSoup(html_content, 'html.parser')

    tables = soup.find_all('table')
    table = tables[index]

    data = []
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            cell_data = [cell.get_text(strip=True) for cell in cells]
            data.append(cell_data)
        return data
    else:
        print('Nie znaleziono tabeli na stronie.')


def skill_dependencies(data: list[list[str]]) -> dict:
    # Tworzymy 4 różne słowniki, jeden dla każdego przedziału poziomów
    dependencies_0_4 = {}
    dependencies_5_9 = {}
    dependencies_8_16_24 = {}
    dependencies_10_99 = {}

    for row in data[1:]:
        skill, required, level_range = row

        # Określamy zakres poziomów (trzecia kolumna)
        if '0-4' in level_range:
            target_dict = dependencies_0_4
        elif '5-9' in level_range:
            target_dict = dependencies_5_9
        elif '8, 16, 24' in level_range:
            target_dict = dependencies_8_16_24
        elif '10-99' in level_range:
            target_dict = dependencies_10_99
        else:
            continue  # Jeśli zakres nie pasuje, pomijamy dany wiersz

        # Krok 1: Użyj funkcji process_skills, aby przetworzyć wymagania
        if required:
            requirements = process_skills(required)
            requirements = remove_level_1(requirements)
        else:
            requirements = []

        # Dodajemy wymagania do odpowiedniego słownika
        target_dict[skill] = requirements

    return {
        "0-4": dependencies_0_4,
        "5-9": dependencies_5_9,
        "8, 16, 24": dependencies_8_16_24,
        "10-99": dependencies_10_99
    }

def process_skills(input_text: str) -> list[str]:
    # Krok 1: Usuń wszystkie spacje
    input_text = input_text.replace(" ", "")

    # Krok 2: Zamień `)(or|and)` na `),`
    input_text = re.sub(r"\)\s*(or|and)\s*", "),", input_text)

    # Krok 3: Podziel ciąg na listę
    skills = input_text.split(",")

    return skills

def remove_level_1(skills: list[str]) -> list[str]:
    # Usuwanie (1) z umiejętności, ale zachowanie (2) i (3)
    return [re.sub(r"\((1|0)\)", "", skill) for skill in skills]

def create_dependency_graph_from_data(dependency_data: dict, level_range: str):
    if level_range not in dependency_data:
        print(f"Nie znaleziono zakresu {level_range}")
        return

    G = nx.DiGraph()
    dependencies = dependency_data[level_range]

    # Unikalne dodawanie węzłów i krawędzi
    for skill, prerequisites in dependencies.items():
        for prereq in prerequisites:
            G.add_edge(prereq, skill)

    # Wyznaczanie poziomów dla węzłów
    levels = {node: 0 for node in G.nodes()}
    for node in nx.topological_sort(G):
        for pred in G.predecessors(node):
            levels[node] = max(levels[node], levels[pred] + 1)

    # Ustawienie pozycji węzłów
    pos = {node: (level, -list(levels.keys()).index(node)) for node, level in levels.items()}

    # Rysowanie grafu
    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=3000,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
        edge_color="gray",
    )
    plt.title(f"Dependency Graph: Level {level_range}")
    plt.show()






def main():
    url = 'https://soc.th.gl/wielders/Cecilia'
    headers = {'User-Agent': 'Mozilla/5.0'}
    html_content = scrape_site(url, headers)

    table_index = 1
    skill_table = scrape_table(html_content, table_index)
    dependencies = skill_dependencies(skill_table)
    for level_range in dependencies.keys():
        print(f"Tworzenie grafu dla poziomu {level_range}...")
        create_dependency_graph_from_data(dependencies, level_range)

if __name__ == '__main__':
    main()

