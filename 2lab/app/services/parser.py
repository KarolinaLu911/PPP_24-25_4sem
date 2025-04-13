import networkx as nx
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from io import StringIO
from app.services.task_manager import create_task, update_task
import time
from sqlalchemy.orm import Session


def parse_website(task_id: str, url: str, max_depth: int, format: str = "graphml", db: Session = None,
                  timeout: int = 60) -> str:
    try:
        # Преобразуем url в строку, если он bytes
        if isinstance(url, bytes):
            url = url.decode('utf-8', errors='ignore')
        print(f"Starting parsing for task_id: {task_id}, URL: {url}")

        start_time = time.time()
        create_task(task_id, db)
        update_task(task_id, status="running", progress=0, db=db)

        G = nx.DiGraph()
        G.add_node(url)  # Уже строка

        visited = set()
        to_visit = [(url, 0)]
        total_urls = 1

        while to_visit:
            if time.time() - start_time > timeout:
                print(f"Timeout exceeded for task_id: {task_id}")
                update_task(task_id, status="failed", progress=0, result="Timeout exceeded", db=db)
                return "Timeout exceeded"

            current_url, depth = to_visit.pop(0)
            if depth > max_depth or current_url in visited:
                continue
            if not isinstance(current_url, str):
                print(f"Invalid current_url at depth {depth}: {repr(current_url)}")
                continue

            visited.add(current_url)
            try:
                print(f"Visiting: {current_url}, depth: {depth}")
                response = requests.get(current_url, timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links:
                    href = link.get('href')
                    if not href or not isinstance(href, str):
                        if isinstance(href, bytes):
                            href = href.decode('utf-8', errors='ignore')
                        else:
                            print(f"Skipping invalid href: {repr(href)} on {current_url}")
                            continue
                    href = href.strip()
                    if not href:
                        print(f"Skipping empty href on {current_url}")
                        continue
                    if href.startswith(('javascript:', 'mailto:', '#')):
                        print(f"Skipping non-URL href: {href} on {current_url}")
                        continue

                    try:
                        absolute_url = urljoin(current_url, href)
                        if isinstance(absolute_url, bytes):
                            absolute_url = absolute_url.decode('utf-8', errors='ignore')
                    except TypeError as e:
                        print(f"Error in urljoin for current_url: {current_url}, href: {repr(href)}, error: {str(e)}")
                        continue

                    # Убедимся, что absolute_url — это строка
                    if not isinstance(absolute_url, str):
                        print(f"Skipping invalid absolute_url: {repr(absolute_url)}")
                        continue

                    # Логируем добавление узла и ребра
                    print(f"Adding node: {absolute_url}")
                    G.add_node(absolute_url)
                    print(f"Adding edge: {current_url} -> {absolute_url}")
                    G.add_edge(current_url, absolute_url)
                    if absolute_url not in visited:
                        to_visit.append((absolute_url, depth + 1))
                        total_urls += 1

                progress = min(100, int(len(visited) / total_urls * 100))
                update_task(task_id, status="running", progress=progress, db=db)
            except requests.RequestException as e:
                print(f"Error visiting {current_url}: {str(e)}")
                continue

        if format.lower() != "graphml":
            raise ValueError("Поддерживается только формат GraphML")

        # Проверяем узлы, рёбра и их атрибуты перед записью
        print("Checking graph nodes, edges, and attributes before writing...")
        for node in G.nodes():
            if not isinstance(node, str):
                raise ValueError(f"Graph node must be a string, got {repr(node)}")
            node_attrs = G.nodes[node]
            print(f"Node {node} attributes: {node_attrs}")
            for attr_key, attr_value in node_attrs.items():
                if isinstance(attr_value, bytes):
                    raise ValueError(f"Node {node} has attribute {attr_key} with bytes value: {repr(attr_value)}")
        for edge in G.edges():
            if not isinstance(edge[0], str) or not isinstance(edge[1], str):
                raise ValueError(f"Graph edge must contain strings, got {repr(edge)}")
            edge_attrs = G.edges[edge]
            print(f"Edge {edge} attributes: {edge_attrs}")
            for attr_key, attr_value in edge_attrs.items():
                if isinstance(attr_value, bytes):
                    raise ValueError(f"Edge {edge} has attribute {attr_key} with bytes value: {repr(attr_value)}")

        # Записываем граф в файл вместо StringIO для отладки
        print("Writing graph to file for debugging...")
        nx.write_graphml(G, "debug_graph.graphml")
        with open("debug_graph.graphml", "r", encoding="utf-8") as f:
            graphml_str = f.read()

        print(f"Parsing completed for task_id: {task_id}")
        update_task(task_id, status="completed", progress=100, result=graphml_str, db=db)
        return graphml_str
    except Exception as e:
        print(f"Error in parse_website for task_id {task_id}: {str(e)}")
        update_task(task_id, status="failed", progress=0, result=f"Error: {str(e)}", db=db)
        return f"Error: {str(e)}"