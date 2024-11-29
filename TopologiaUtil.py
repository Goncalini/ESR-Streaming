import json
from collections import defaultdict, deque
import heapq

# Carregar a topologia a partir do arquivo JSON
with open('config.json', 'r') as file:
    topologia = json.load(file)

# Inicializar o grafo bidirecional
grafo = defaultdict(dict)

# Preencher o grafo com as conexões bidirecionais e suas larguras de banda
for ip, dados in topologia.items():
    no_id = dados["id"]
    for vizinho in dados["Vizinhos"]:
        vizinho_id = vizinho["nome"]
        largura_banda = vizinho["bandwidth"]
        
        # Adiciona a conexão nos dois sentidos para garantir bidirecionalidade
        grafo[no_id][vizinho_id] = largura_banda
        grafo[vizinho_id][no_id] = largura_banda

# Escolher um nó raiz para iniciar a árvore
raiz = 'n3'  

# Função para construir a árvore a partir do grafo usando BFS
def construir_arvore(grafo, raiz):
    arvore = defaultdict(list)
    visitados = set()
    fila = deque([raiz])

    while fila:
        no_atual = fila.popleft()
         
        # Somente marcar o nó como visitado após processá-lo
        visitados.add(no_atual)

        # Para cada vizinho, adicionar aresta na árvore se ainda não foi visitado
        for vizinho, largura_banda in grafo[no_atual].items():
            if vizinho not in visitados:
                # Adicionar a aresta apenas se ainda não estiver na lista de filhos
                if (vizinho, largura_banda) not in arvore[no_atual]:
                    arvore[no_atual].append((vizinho, largura_banda))
                fila.append(vizinho)

    return arvore

# Construir a árvore a partir do nó raiz
arvore_topologia = construir_arvore(grafo, raiz)

'''
# Exibir a árvore resultante
for pai, filhos in arvore_topologia.items():
    filhos_str = ", ".join([f"{filho} (bw: {bw})" for filho, bw in filhos])
    print(f"{pai} -> [{filhos_str}]")
'''

def getparent(node):
    if node == raiz:
        return "Server"
    for pai, filhos in arvore_topologia.items():
        for filho, _ in filhos:
            if filho == node:
                #print(pai)
                return pai
    return None

getparent('n4')

def melhor_caminho_dijkstra(grafo, raiz, destino):
    # Usar uma heap para priorizar caminhos com maior largura de banda mínima
    heap = [(-float('inf'), raiz, [])]  # (-largura_banda_minima, no_atual, caminho_atual)
    visitados = set()

    while heap:
        largura_banda_minima, no_atual, caminho = heapq.heappop(heap)
        largura_banda_minima = -largura_banda_minima  # Reverter o valor negativo

        if no_atual in visitados:
            continue

        # Atualizar o caminho ao visitar o nó
        caminho = caminho + [no_atual]
        visitados.add(no_atual)

        # Verificar se chegamos ao destino
        if no_atual == destino:
            return caminho, largura_banda_minima

        # Adicionar vizinhos à heap
        for vizinho, largura_banda in grafo[no_atual].items():
            if vizinho not in visitados:
                # A largura de banda mínima no caminho considera o menor valor até agora
                nova_largura_banda_minima = min(largura_banda_minima, largura_banda)
                heapq.heappush(heap, (-nova_largura_banda_minima, vizinho, caminho))

    # Retornar vazio caso o destino não seja alcançável
    return None, 0

'''
# teste
destino = 'n9'  # Substitua pelo nó de destino desejado
caminho, largura_banda_minima = melhor_caminho_dijkstra(grafo, raiz, destino)
if caminho:
    print(f"Melhor caminho de {raiz} até {destino}: {' -> '.join(caminho)}")
    print(f"Largura de banda mínima ao longo do caminho: {largura_banda_minima}")
else:
    print(f"Não foi possível alcançar o nó {destino} a partir de {raiz}.")
'''
print("TopologiaUtil.py carregado com sucesso")