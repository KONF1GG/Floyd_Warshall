import numpy as np
from typing import List, Tuple, Dict
import logging
from pydantic import ValidationError
from requests.exceptions import RequestException
import requests

from config import LOCALITY_URL
from schemas import LocalityResponse, Locality

# Настройка логгера
logger = logging.getLogger(__name__)
TIMEOUT = 10  # сек

def get_localities() -> LocalityResponse:
    """
    Получает список населенных пунктов с удаленного сервера.
    Возвращает LocalityResponse с данными или ошибкой.
    """
    try:
        response = requests.get(LOCALITY_URL, timeout=TIMEOUT)
        response.raise_for_status()
        localities = parse_localities(response.json())
        return LocalityResponse(data=localities)
    except RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return LocalityResponse(error=f"Connection error: {str(e)}")
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return LocalityResponse(error=f"Invalid data format: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error occurred")
        return LocalityResponse(error=f"Unexpected error: {str(e)}")

def parse_localities(raw_data: List[dict]) -> List[Locality]:
    """Парсит сырые данные в список объектов Locality с валидацией."""
    localities = []
    for item in raw_data:
        try:
            localities.append(Locality(**item))
        except ValidationError as e:
            logger.warning(f"Skipping invalid locality item: {str(e)}")
    return localities

def build_adjacency_matrices(localities: List[Locality], nodes: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """Строит матрицы смежности для времени и расстояния."""
    n = len(nodes)
    time_matrix = np.full((n, n), float('inf'))
    distance_matrix = np.full((n, n), float('inf'))
    np.fill_diagonal(time_matrix, 0)
    np.fill_diagonal(distance_matrix, 0)
    
    node_index = {node: i for i, node in enumerate(nodes)}
    
    for locality in localities:
        i = node_index[locality.city1]
        j = node_index[locality.city2]
        time_matrix[i][j] = locality.min
        time_matrix[j][i] = locality.min
        distance_matrix[i][j] = locality.km if locality.km is not None else locality.min
        distance_matrix[j][i] = locality.km if locality.km is not None else locality.min
    
    return time_matrix, distance_matrix

def floyd_warshall(matrix: np.ndarray) -> np.ndarray:
    """Применяет алгоритм Флойда-Уоршелла и возвращает матрицу расстояний."""
    n = matrix.shape[0]
    dist = matrix.copy()

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist

def compute_all_pairs_shortest_paths(localities: List[Locality]) -> Tuple[
    Dict[Tuple[str, str], float],
    Dict[Tuple[str, str], float]
]:
    """Вычисляет кратчайшие пути между всеми парами вершин по времени и расстоянию."""
    nodes = list(set([locality.city1 for locality in localities] + [locality.city2 for locality in localities]))
    time_matrix, distance_matrix = build_adjacency_matrices(localities, nodes)
    
    time_dist = floyd_warshall(time_matrix)
    distance_dist = floyd_warshall(distance_matrix)
    
    node_index = {node: i for i, node in enumerate(nodes)}
    
    time_shortest = {}
    distance_shortest = {}
    
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes):
            if i != j:
                time_shortest[(node1, node2)] = time_dist[i][j]
                distance_shortest[(node1, node2)] = distance_dist[i][j]
    
    return time_shortest, distance_shortest

def main_response() -> List[Locality]:
    response = get_localities()
    if response.error:
        print(f"Ошибка: {response.error}")
        return
    
    localities = response.data
    time_shortest, distance_shortest = compute_all_pairs_shortest_paths(localities)
    
    dist = []
    for (start, end) in time_shortest:
        time_value = time_shortest[(start, end)]
        distance_value = distance_shortest[(start, end)]
        dist.append(Locality(city1=start, city2=end, min=time_value, km=distance_value))

    return dist