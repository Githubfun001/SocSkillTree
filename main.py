import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_site(url: str, headers: dict[str, str]) -> str:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f'Błąd podczas pobierania strony: {response.status_code}')


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
    dependencies = {}

    for row in data[1:]:
        skill, required, _ = row

        if not required:  # Jeśli pole 'required' jest puste
            dependencies[skill] = []
        else:
            # Krok 1: Użyj funkcji process_skills, aby przetworzyć wymagania
            requirements = process_skills(required)

            # Dodaj wymagania do słownika
            dependencies[skill] = requirements

    return dependencies

def process_skills(input_text: str) -> list[str]:
    # Krok 1: Usuń wszystkie spacje
    input_text = input_text.replace(" ", "")

    # Krok 2: Zamień `)(or|and)` na `),`
    input_text = re.sub(r"\)\s*(or|and)\s*", "),", input_text)

    # Krok 3: Podziel ciąg na listę
    skills = input_text.split(",")

    return skills

def main():
    url = 'https://soc.th.gl/wielders/Cecilia'
    headers = {'User-Agent': 'Mozilla/5.0'}
    html_content = scrape_site(url, headers)

    table_index = 1
    skill_table = scrape_table(html_content, table_index)
    print(skill_table)
    print(skill_dependencies(skill_table))



# def process_required_skills(required):
#     # Nowa wersja, aby obsługiwać wielosłowne skille poprawnie
#     # Używamy re.split, ale musimy zadbać o multi-słowne skille, więc zatrzymujemy wielosłowne frazy w nawiasach
#     requirements = re.split(r'\s*(?:and|or)\s*', required)  # Rozdzielamy na 'and' i 'or', ale zachowujemy skille z więcej niż jednym słowem
#
#     processed_requirements = []
#
#     for req in requirements:
#         # Spróbujmy wyłapać nazwę skilla z poziomem (np. "Taxes(2)")
#         match = re.match(r'([a-zA-Z\s]+?)\((\d+)\)', req)  # Wyciągamy nazwę skilla i liczbę w nawiasach
#         if match:
#             skill_name = match.group(1).strip()  # Nazwa skilla
#             level = match.group(2)  # Poziom skilla
#             # Jeśli poziom to (0), to go pomijamy
#             if level == '0':  # Usuń (0)
#                 continue
#             elif level == '1':  # Usuń (1)
#                 processed_requirements.append(skill_name)  # Zostaw tylko nazwę skilla
#             else:
#                 processed_requirements.append(f"{skill_name}({level})")  # Zachowujemy liczbę, jeśli > 1
#         else:
#             # Jeśli brak liczby w nawiasie, dodajemy tylko nazwę skilla
#             processed_requirements.append(req.strip())
#
#     return processed_requirements
#
#
#
#
#

# # Funkcja do budowania hierarchii
# def build_hierarchy(dependencies):
#     levels = {}  # Słownik poziomów: poziom -> lista skilli
#     visited = set()  # Przetworzone skille
#
#     def add_to_level(skill, current_level):
#         if skill in visited:  # Skill już przypisany do poziomu
#             return
#         visited.add(skill)
#
#         # Dodaj skill do odpowiedniego poziomu
#         if current_level not in levels:
#             levels[current_level] = []
#         levels[current_level].append(skill)
#
#         # Przetwarzaj zależne skille
#         for dependent_skill, required_skills in dependencies.items():
#             if skill in required_skills:  # Jeśli jest zależność
#                 add_to_level(dependent_skill, current_level + 1)
#
#     # Zacznij od skilli bez zależności (najniższy poziom)
#     for skill, reqs in dependencies.items():
#         if not reqs:
#             add_to_level(skill, 0)
#
#     return levels
#
# hierarchy = build_hierarchy(dependencies)
# print("Hierarchia:", hierarchy)
#
# import networkx as nx
# import matplotlib.pyplot as plt
#
# # Budowanie grafu na podstawie hierarchii
# def visualize_hierarchy(hierarchy, dependencies):
#     G = nx.DiGraph()
#
#     # Dodawanie krawędzi zgodnie z zależnościami
#     for skill, reqs in dependencies.items():
#         for req in reqs:
#             skill_name = re.sub(r'\(\d+\)', '', skill)  # Usuwamy liczbę w nawiasach z nazwy skilla
#             req_name = re.sub(r'\(\d+\)', '', req)  # Usuwamy liczbę w nawiasach z nazwy skilla
#             G.add_edge(req_name, skill_name)
#
#     # Pozycje węzłów na podstawie hierarchii
#     pos = {}
#     for level, skills in hierarchy.items():
#         for i, skill in enumerate(skills):
#             pos[skill] = (i, -level)  # Poziomy w dół (-level)
#
#     # Rysowanie grafu
#     plt.figure(figsize=(12, 8))
#     nx.draw(
#         G, pos, with_labels=True, node_size=2000, node_color="lightblue",
#         font_size=10, font_weight="bold", arrowsize=20
#     )
#     plt.title("Hierarchia skilli")
#     plt.show()
#
# visualize_hierarchy(hierarchy, dependencies)





if __name__ == '__main__':
    main()

