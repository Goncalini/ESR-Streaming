import json
from collections import defaultdict, deque

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
raiz = 'n3'  # Podemos escolher qualquer nó existente como raiz

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

# Exibir a árvore resultante
for pai, filhos in arvore_topologia.items():
    filhos_str = ", ".join([f"{filho} (bw: {bw})" for filho, bw in filhos])
    print(f"{pai} -> [{filhos_str}]")
