import tkinter as tk
import random
import time
import threading
import math
from PIL import Image, ImageTk
import heapq
from collections import deque
import cv2
import os


# Dados do mapa (Comuns para ambos os parques)


novo_grafo = {
    "nos": {
        "1": [11, 746], "2": [111, 691], "3": [259, 778], "4": [409, 698],
        "5": [253, 620], "6": [608, 604], "7": [144, 546], "8": [473, 534],
        "9": [619, 453], "10": [787, 530], "11": [770, 681], "12": [609, 755],
        "13": [506, 831], "14": [421, 862], "15": [325, 460], "16": [481, 386],
        "17": [456, 349], "18": [509, 326], "19": [440, 266], "20": [212, 376],
        "21": [11, 464], "22": [17, 346], "23": [74, 263], "24": [166, 276],
        "25": [215, 245], "26": [130, 188], "27": [202, 156], "28": [339, 169],
        "29": [455, 100], "30": [475, 230], "31": [524, 212], "32": [695, 292],
        "33": [672, 315], "34": [824, 404], "35": [1020, 314], "36": [877, 243],
        "37": [833, 177], "38": [738, 417], "39": [599, 347], "40": [642, 524],
        "41": [612, 674], "42": [729, 778], "43": [736, 593], "44": [449, 774],
        "45": [239, 696], "46": [115, 604], "47": [328, 590], "48": [142, 470],
        "49": [348, 369], "50": [287, 201], "51": [137, 117], "52": [338, 99],
        "53": [481, 184], "54": [783, 109], "55": [922, 180], "56": [807, 319],
        "57": [741, 362], "58": [187, 735], "59": [530, 719], "60": [459, 686],
        "61": [504, 654], "62": [481, 642], "63": [514, 590], "64": [684, 634],
        "65": [486, 470], "66": [515, 508], "67": [679, 470], "68": [280, 404],
        "69": [110, 339], "70": [114, 407], "71": [284, 314], "72": [253, 145],
        "73": [417, 212], "74": [353, 262], "75": [265, 289], "76": [400, 72],
        "77": [714, 106], "78": [962, 307], "79": [800, 209], "80": [182, 652],
        "81": [899, 580], "82": [815, 502], "83": [895, 442], "84": [760, 260],
        "85": [702, 221], "86": [104, 230], "87": [909, 131], "88": [840, 80]
    },
    "arestas": [
        [1, 2], [3, 2], [2, 5], [5, 4], [3, 4], [45, 58], [2, 58], [3, 58],
        [14, 3], [14, 13], [13, 44], [13, 12], [12, 11], [41, 59], [59, 12],
        [60, 59], [60, 4], [63, 62], [62, 61], [61, 60], [6, 61], [6, 11],
        [64, 43], [6, 64], [11, 64], [8, 6], [8, 47], [8, 15], [15, 16],
        [16, 9], [66, 65], [8, 66], [66, 9], [6, 40], [10, 6], [67, 9],
        [67, 10], [67, 38], [17, 16], [17, 18], [18, 19], [68, 49], [68, 15],
        [68, 20], [20, 69], [70, 22], [21, 70], [21, 7], [7, 15], [70, 48],
        [20, 70], [71, 20], [71, 24], [24, 25], [25, 26], [26, 27], [27, 51],
        [72, 27], [72, 28], [73, 28], [73, 74], [50, 74], [74, 75], [73, 30],
        [30, 31], [31, 53], [28, 29], [29, 76], [76, 52], [77, 31], [77, 54],
        [31, 32], [32, 33], [33, 57], [57, 34], [34, 35], [78, 35], [35, 36],
        [36, 55], [79, 37], [79, 36], [80, 46], [80, 2], [80, 5], [82, 10],
        [10, 81], [34, 83], [12, 42], [32, 84], [84, 56], [79, 85], [24, 23],
        [86, 23], [37, 87], [88, 77], [88, 87]
    ]
}

# Converter para o formato anterior (chaves como inteiros)
coordenadas_base = {int(k): v for k, v in novo_grafo["nos"].items()}
ruas_base = [[int(a), int(b)] for a, b in novo_grafo["arestas"]]
entrada_saida_base = (90, 810) # Ponto de entrada/saída original


PARK_WIDTH = 500
PARK_HEIGHT = 450

# Tamanho das imagens das pessoas
PERSON_IMAGE_SIZE = 40 # Pixels (Aumentado para 40)

# ============================
# Configurações Globais (para o menu de controle)
# ============================
class GlobalConfig:
    def __init__(self):
        self.velocidade_entrada = tk.DoubleVar(value=0.5)
        self.quant_pessoas_por_segundo = tk.IntVar(value=1) # Não usado no código atual
        self.limite_pessoas_parque = tk.IntVar(value=50)
        self.gerar_pessoas_ativo = tk.BooleanVar(value=True)
        self.velocidade_movimento_pessoa = tk.DoubleVar(value=5.0)
        self.tempo_no_brinquedo = tk.DoubleVar(value=3.0)


person_images = {} # Dicionário para armazenar as PhotoImages

def load_person_images():
    """Carrega as imagens das pessoas e as converte para PhotoImage."""
    global person_images
    try:
        # Imagens Heurística
        img_qiqi_eletrica = Image.open("qiqi_eletrica.png").resize((PERSON_IMAGE_SIZE, PERSON_IMAGE_SIZE), Image.LANCZOS)
        person_images['heuristica_indo'] = ImageTk.PhotoImage(img_qiqi_eletrica)
        person_images['heuristica_no_brinquedo'] = ImageTk.PhotoImage(img_qiqi_eletrica)
        person_images['heuristica_na_fila'] = ImageTk.PhotoImage(img_qiqi_eletrica)

        img_qiqi_eletrica2 = Image.open("qiqi_eletrica2.png").resize((PERSON_IMAGE_SIZE, PERSON_IMAGE_SIZE), Image.LANCZOS)
        person_images['heuristica_saindo'] = ImageTk.PhotoImage(img_qiqi_eletrica2)

        # Imagens Aleatório
        img_qiqi_hextec = Image.open("qiqi_hextec.png").resize((PERSON_IMAGE_SIZE, PERSON_IMAGE_SIZE), Image.LANCZOS)
        person_images['aleatorio_indo'] = ImageTk.PhotoImage(img_qiqi_hextec)
        person_images['aleatorio_no_brinquedo'] = ImageTk.PhotoImage(img_qiqi_hextec)
        person_images['aleatorio_na_fila'] = ImageTk.PhotoImage(img_qiqi_hextec)

        img_qiqi_hextec2 = Image.open("qiqi_hextec2.png").resize((PERSON_IMAGE_SIZE, PERSON_IMAGE_SIZE), Image.LANCZOS)
        person_images['aleatorio_saindo'] = ImageTk.PhotoImage(img_qiqi_hextec2)

    except FileNotFoundError as e:
        print(f"Erro: Arquivo de imagem não encontrado. Certifique-se de que '{e.filename}' está no mesmo diretório do script.")
        person_images = None 
    except Exception as e:
        print(f"Erro ao carregar imagens: {e}")
        person_images = None 


# Classe Base para o Parque (contém lógica comum)

class ParqueBase:
    def __init__(self, master, offset_x=0, title_suffix="", strategy_type=""):
        self.master = master
        self.offset_x = offset_x
        self.title_suffix = title_suffix
        self.strategy_type = strategy_type

        
        self.canvas = tk.Canvas(master, bg='white', highlightbackground="black", highlightthickness=2)
        self.canvas.pack(expand=True, fill="both")

        
        try:
            self.imagem_fundo_pil = Image.open("parque.png")
            self.fundo = None # Inicializa como None para evitar erro antes do resize
            self.canvas_fundo_id = self.canvas.create_image(0, 0, image=self.fundo, anchor=tk.NW) # ID do objeto imagem
            
            
            self.canvas.bind("<Configure>", self._on_canvas_resize)

        except FileNotFoundError:
            print("Erro: Imagem de fundo 'parque.png' não encontrada. Usando fundo branco.")
            self.fundo = None # Nenhuma imagem de fundo para usar
            self.canvas.config(bg='white') # Garante fundo branco se imagem não carregar
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}. Usando fundo branco.")
            self.fundo = None
            self.canvas.config(bg='white')


        
        original_graph_width = 1020
        original_graph_height = 900
        
        self.coordenadas_originais = coordenadas_base 
        self.ruas = ruas_base
        self.entrada_saida_original = entrada_saida_base

        # O grafo é construído com base nas coordenadas originais
        self.grafo = self.gerar_grafo(self.coordenadas_originais)
        self.brinquedos = self.identificar_brinquedos()

        self.pessoas = []
        self.rodando = True
        self.pessoa_id_counter = 0

        self.last_person_spawn_time = 0

        
        self.animation_id = self.master.after(50, self.atualizar) 

    def _on_canvas_resize(self, event):
        
        if self.imagem_fundo_pil:
            new_width = self.canvas.winfo_width()
            new_height = self.canvas.winfo_height()
            
            
            if new_width > 0 and new_height > 0:
                resized_img = self.imagem_fundo_pil.resize((new_width, new_height), Image.LANCZOS)
                self.fundo = ImageTk.PhotoImage(resized_img)
                self.canvas.itemconfig(self.canvas_fundo_id, image=self.fundo)
                self.canvas.coords(self.canvas_fundo_id, 0, 0)
            
        
        self.atualizar_elementos_no_canvas()

    def _get_scaled_coords(self, node_id):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Use dimensões padrão se o canvas ainda não foi renderizado
        # PARK_WIDTH e PARK_HEIGHT são as dimensões padrão esperadas para um único parque
        default_canvas_width = PARK_WIDTH
        default_canvas_height = PARK_HEIGHT

        x_orig, y_orig = self.coordenadas_originais[node_id]

        if canvas_width == 0 or canvas_height == 0:
            # Se as dimensões do canvas ainda não estão disponíveis, use as dimensões padrão
            scale_x = default_canvas_width / 1020
            scale_y = default_canvas_height / 900
            return [x_orig * scale_x, y_orig * scale_y]
        else:
            # Se as dimensões do canvas estão disponíveis, use-as
            scale_x = canvas_width / 1020
            scale_y = canvas_height / 900
            return [x_orig * scale_x, y_orig * scale_y]

    def _get_scaled_entry_exit(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        default_canvas_width = PARK_WIDTH
        default_canvas_height = PARK_HEIGHT

        x_orig_entry, y_orig_entry = self.entrada_saida_original

        if canvas_width == 0 or canvas_height == 0:
            scale_x = default_canvas_width / 1020
            scale_y = default_canvas_height / 900
            return (x_orig_entry * scale_x, y_orig_entry * scale_y)
        else:
            scale_x = canvas_width / 1020
            scale_y = canvas_height / 900
            return (x_orig_entry * scale_x, y_orig_entry * scale_y)

    def identificar_brinquedos(self):
        brinquedos = {}
        for no in self.grafo:
            if len(self.grafo[no]) == 1:
                brinquedos[no] = {
                    'ocupados': 0,
                    'fila': deque(),
                    'capacidade': 4
                }
        return brinquedos

    def gerar_grafo(self, coords_dict):
        grafo = {n: [] for n in coords_dict}
        for a, b in self.ruas:
            x1, y1 = coords_dict[a]
            x2, y2 = coords_dict[b]
            distancia_segmento = math.hypot(x2 - x1, y2 - y1)
            grafo[a].append((b, distancia_segmento))
            grafo[b].append((a, distancia_segmento))
        return grafo

    def caminho_dijkstra(self, inicio, destino):
        fila = [(0, inicio, [])]
        visitados = set()
        custos = {no: float('inf') for no in self.grafo}
        custos[inicio] = 0

        while fila:
            (custo_atual, no_atual, caminho_acumulado) = heapq.heappop(fila)

            if no_atual in visitados:
                continue

            caminho_completo = caminho_acumulado + [no_atual]

            if no_atual == destino:
                return caminho_completo

            visitados.add(no_atual)

            for vizinho, peso in self.grafo[no_atual]:
                novo_custo = custo_atual + peso
                if novo_custo < custos[vizinho]:
                    custos[vizinho] = novo_custo
                    heapq.heappush(fila, (novo_custo, vizinho, caminho_completo))
        return []

    def calcular_caminho_a_star(self, inicio, destino):
        fila_prioridade = [(0, inicio, [], 0)] # (f_cost, node, path, g_cost)
        g_costs = {no: float('inf') for no in self.grafo}
        g_costs[inicio] = 0
        
        # Para evitar ciclos infinitos em casos problemáticos ou grafos desconectados
        came_from = {} 

        while fila_prioridade:
            (f_cost, no_atual, caminho, g_cost) = heapq.heappop(fila_prioridade)

            if no_atual == destino:
                return caminho + [no_atual], g_cost

            # Melhoria para evitar reprocessar nós com custos piores
            if g_cost > g_costs[no_atual]:
                continue

            for vizinho, peso in self.grafo[no_atual]:
                novo_g_cost = g_cost + peso
                if novo_g_cost < g_costs[vizinho]:
                    g_costs[vizinho] = novo_g_cost
                    f_cost_novo = novo_g_cost + self.distancia(self.coordenadas_originais[vizinho], self.coordenadas_originais[destino])
                    heapq.heappush(fila_prioridade, (f_cost_novo, vizinho, caminho + [no_atual], novo_g_cost))
        return [], float('inf')

    def desenha_ruas(self):
        for rua in self.ruas:
            x1, y1 = self._get_scaled_coords(rua[0])
            x2, y2 = self._get_scaled_coords(rua[1])
            self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=1, tags="ruas")

    def desenha_pontos(self):
        for id_ in self.grafo.keys():
            x_draw, y_draw = self._get_scaled_coords(id_)

            if id_ in self.brinquedos:
                self.canvas.create_rectangle(x_draw - 10, y_draw - 10, x_draw + 10, y_draw + 10, fill="blue", outline="black", width=1, tags="pontos")
                brinquedo = self.brinquedos[id_]
                ocupacao = brinquedo['ocupados']
                capacidade = brinquedo['capacidade']
                cor_ocupacao = "red" if ocupacao >= capacidade else ("yellow" if ocupacao > 0 else "green") 
                self.canvas.create_oval(x_draw - 5, y_draw - 5, x_draw + 5, y_draw + 5, fill=cor_ocupacao, outline="black", tags="pontos")
                self.canvas.create_text(x_draw, y_draw, text=f"{ocupacao}/{capacidade}", fill="black", font=('Arial', 6, 'bold'), tags="pontos")
                fila = len(brinquedo['fila'])
                if fila > 0:
                    self.canvas.create_text(x_draw, y_draw + 15, text=f"Fila: {fila}", fill="red", font=('Arial', 6, 'bold'), tags="pontos")
            else:
                self.canvas.create_oval(x_draw - 3, y_draw - 3, x_draw + 3, y_draw + 3, fill="gray", tags="pontos")

        # Entrada/Saída
        x_entry, y_entry = self._get_scaled_entry_exit()
        self.canvas.create_oval(x_entry - 8, y_entry - 8, x_entry + 8, y_entry + 8, fill="green", outline="black", width=1, tags="pontos")
        self.canvas.create_text(x_entry, y_entry + 15, text="Entrada/Saída", fill="black", font=('Arial', 6, 'bold'), tags="pontos")

    def caminho_saida(self, inicio_node_id):
        mais_proximo_saida = min(self.coordenadas_originais.keys(), key=lambda n: self.distancia(self.entrada_saida_original, self.coordenadas_originais[n]))
        return self.caminho_dijkstra(inicio_node_id, mais_proximo_saida)

    def distancia(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def mover_pessoa(self, pessoa):
        if pessoa['indice'] >= len(pessoa['caminho']):
            return

        alvo_node_id = pessoa['caminho'][pessoa['indice']]
        alvo_x_scaled, alvo_y_scaled = self._get_scaled_coords(alvo_node_id)
        
        dx = alvo_x_scaled - pessoa['x']
        dy = alvo_y_scaled - pessoa['y']
        distancia_restante = math.hypot(dx, dy)

        step = global_config.velocidade_movimento_pessoa.get()

        if distancia_restante < step:
            pessoa['x'] = alvo_x_scaled
            pessoa['y'] = alvo_y_scaled
            pessoa['indice'] += 1
        else:
            pessoa['x'] += dx / distancia_restante * step
            pessoa['y'] += dy / distancia_restante * step

    def atualizar_elementos_no_canvas(self):
        self.canvas.delete("ruas")
        self.canvas.delete("pontos")
        self.canvas.delete("pessoas")
        self.canvas.delete("info")

        self.desenha_ruas()
        self.desenha_pontos()

        for pessoa in list(self.pessoas):
            if person_images and person_images.get(f"{self.strategy_type}_{pessoa['estado']}"):
                image_key = f"{self.strategy_type}_{pessoa['estado']}"
                person_img = person_images[image_key]
                self.canvas.create_image(
                    pessoa['x'], pessoa['y'],
                    image=person_img,
                    anchor=tk.CENTER,
                    tags="pessoas"
                )
            else:
                 self.canvas.create_oval(
                    pessoa['x'] - 5, pessoa['y'] - 5,
                    pessoa['x'] + 5, pessoa['y'] + 5,
                    fill="gray", outline="black",
                    tags="pessoas"
                )
        
        total_pessoas = len(self.pessoas)
        pessoas_em_brinquedos = sum(b['ocupados'] for b in self.brinquedos.values())
        pessoas_na_fila = sum(len(b['fila']) for b in self.brinquedos.values())

        # Posição do texto de informação
        self.canvas.create_text(self.canvas.winfo_width() // 2, 20,
                              text=f"Parque {self.title_suffix}\nTotal: {total_pessoas} | Brinquedos: {pessoas_em_brinquedos} | Fila: {pessoas_na_fila}",
                              fill="black", font=('Arial', 8, 'bold'), anchor=tk.N, tags="info")


    def atualizar(self):
        self.atualizar_elementos_no_canvas()

        for pessoa in list(self.pessoas):
            if pessoa['estado'] == 'no_brinquedo':
                if time.time() - pessoa['tempo_no_brinquedo'] >= global_config.tempo_no_brinquedo.get():
                    brinquedo = self.brinquedos[pessoa['destino']]
                    if brinquedo['ocupados'] > 0:
                        brinquedo['ocupados'] -= 1

                    pessoa['brinquedos_visitados'].add(pessoa['destino'])
                    pessoa['visitados_count'] += 1

                    if brinquedo['fila']:
                        proximo_id_na_fila = brinquedo['fila'].popleft()
                        for p_fila in self.pessoas:
                            if p_fila['id'] == proximo_id_na_fila and p_fila['estado'] == 'na_fila':
                                p_fila['estado'] = 'no_brinquedo'
                                p_fila['tempo_no_brinquedo'] = time.time()
                                brinquedo['ocupados'] += 1
                                break

                    ponto_partida_proximo_caminho = pessoa['destino']

                    brinquedos_nao_visitados_count = len([b for b in self.brinquedos.keys() if b not in pessoa['brinquedos_visitados']])

                    if pessoa['visitados_count'] >= 3 or brinquedos_nao_visitados_count == 0:
                        pessoa['saindo'] = True
                        caminho_saida_final = self.caminho_saida(ponto_partida_proximo_caminho)
                        if caminho_saida_final:
                            pessoa['caminho'] = caminho_saida_final
                            pessoa['indice'] = 0
                            pessoa['estado'] = 'saindo'
                        else:
                            # Se não há caminho para saída, remove a pessoa para evitar travamento
                            self.pessoas.remove(pessoa)
                            continue
                    else:
                        self.escolher_e_mover_para_proximo_brinquedo(pessoa, ponto_partida_proximo_caminho)

            elif pessoa['estado'] == 'indo':
                if pessoa['indice'] >= len(pessoa['caminho']):
                    if pessoa['destino'] in self.brinquedos:
                        brinquedo = self.brinquedos[pessoa['destino']]
                        if brinquedo['ocupados'] < brinquedo['capacidade']:
                            brinquedo['ocupados'] += 1
                            pessoa['estado'] = 'no_brinquedo'
                            pessoa['tempo_no_brinquedo'] = time.time()
                        else:
                            brinquedo['fila'].append(pessoa['id'])
                            pessoa['estado'] = 'na_fila'
                    else:
                        # Se não é um brinquedo (ex: nó intermediário do caminho de saída)
                        if not pessoa['saindo']:
                            self.escolher_e_mover_para_proximo_brinquedo(pessoa, pessoa['caminho'][-1])
                        else:
                            self.pessoas.remove(pessoa) # Já chegou ao final do caminho de saída
                            continue
                else:
                    self.mover_pessoa(pessoa)
            elif pessoa['estado'] == 'na_fila':
                pass # Pessoas na fila não se movem

            elif pessoa['estado'] == 'saindo':
                if pessoa['indice'] >= len(pessoa['caminho']):
                    self.pessoas.remove(pessoa)
                    continue
                else:
                    self.mover_pessoa(pessoa)
            
        self.animation_id = self.master.after(50, self.atualizar)

    def gerar_pessoas(self):
        # Esta função será sobrescrita pelas classes filhas (Aleatorio e Heuristica)
        
        raise NotImplementedError("gerar_pessoas deve ser implementado pela subclasse")

    def escolher_e_mover_para_proximo_brinquedo(self, pessoa, ponto_partida_proximo_caminho_node_id):
        # Este método precisa ser implementado pelas classes filhas com a lógica de escolha
        raise NotImplementedError("escolher_e_mover_para_proximo_brinquedo deve ser implementado pela subclasse")
    
    def escolher_proximo_brinquedo_a_star(self, current_node_id, visited_attractions):
        melhor_brinquedo = None
        menor_custo_total = float('inf')

        brinquedos_disponiveis = list(self.brinquedos.keys())
        
        # Priorizar brinquedos não visitados, com menor fila e menor custo A*
        candidatos_prioritarios = []
        for b_id in brinquedos_disponiveis:
            if b_id not in visited_attractions:
                # Calcula a "pressão" na fila + ocupação
                b_info = self.brinquedos[b_id]
                fator_fila = len(b_info['fila']) / b_info['capacidade'] if b_info['capacidade'] > 0 else len(b_info['fila'])
                # Custo da fila é um "peso" adicional no f_cost do A*
                
                # Calcular o caminho A* para cada brinquedo
                caminho, custo_caminho = self.calcular_caminho_a_star(current_node_id, b_id)
                if caminho:
                    # Adiciona uma penalidade à fila para influenciar a escolha
                    custo_total = custo_caminho + (fator_fila * 100) # Penalidade de 100 por unidade de fator_fila
                    candidatos_prioritarios.append((custo_total, b_id, caminho))

        # Ordenar os candidatos prioritários pelo custo total
        candidatos_prioritarios.sort()

        if candidatos_prioritarios:
            menor_custo_total, melhor_brinquedo, _ = candidatos_prioritarios[0]
            print(f"[{self.strategy_type}] Escolheu brinquedo NÃO VISITADO: {melhor_brinquedo} com custo total: {menor_custo_total:.2f}")
            return melhor_brinquedo, menor_custo_total
        
        # Se não há brinquedos não visitados com caminho, tenta os visitados (ainda priorizando fila/custo)
        candidatos_secundarios = []
        for b_id in brinquedos_disponiveis:
            b_info = self.brinquedos[b_id]
            fator_fila = len(b_info['fila']) / b_info['capacidade'] if b_info['capacidade'] > 0 else len(b_info['fila'])
            caminho, custo_caminho = self.calcular_caminho_a_star(current_node_id, b_id)
            if caminho:
                custo_total = custo_caminho + (fator_fila * 100)
                candidatos_secundarios.append((custo_total, b_id, caminho))
        
        candidatos_secundarios.sort()
        
        if candidatos_secundarios:
            menor_custo_total, melhor_brinquedo, _ = candidatos_secundarios[0]
            print(f"[{self.strategy_type}] Escolheu brinquedo VISITADO (sem opção não visitada): {melhor_brinquedo} com custo total: {menor_custo_total:.2f}")
            return melhor_brinquedo, menor_custo_total

        print(f"[{self.strategy_type}] A* não encontrou nenhum brinquedo acessível.")
        return None, float('inf')



# Parque com Estratégia Aleatória


class ParqueAleatorio(ParqueBase):
    def __init__(self, master, offset_x=0):
        super().__init__(master, offset_x, title_suffix="Aleatório", strategy_type="aleatorio")

    def gerar_pessoas(self):
        while self.rodando:
            if global_config.gerar_pessoas_ativo.get() and len(self.pessoas) < global_config.limite_pessoas_parque.get():
                current_time = time.time()
                time_since_last_spawn = current_time - self.last_person_spawn_time

                if time_since_last_spawn >= global_config.velocidade_entrada.get():
                    self.pessoa_id_counter += 1
                    pessoa_id = self.pessoa_id_counter

                    ponto_partida_parque_node_id = min(self.coordenadas_originais.keys(), key=lambda n: self.distancia(self.entrada_saida_original, self.coordenadas_originais[n]))

                    brinquedos_disponiveis = list(self.brinquedos.keys())
                    if not brinquedos_disponiveis:
                        time.sleep(0.05)
                        continue
                    
                    # Tenta escolher um brinquedo que não esteja com fila lotada/capacidade máxima( DEU PROBLEMA COM A ENTRADA)
                    brinquedos_candidatos = [b for b in brinquedos_disponiveis if self.brinquedos[b]['ocupados'] < self.brinquedos[b]['capacidade']]
                    if not brinquedos_candidatos:
                        # Se todos estão lotados, ainda assim escolhe um aleatório para ir para a fila
                        brinquedos_candidatos = brinquedos_disponiveis

                    destino = random.choice(brinquedos_candidatos)

                    caminho_para_destino = self.caminho_dijkstra(ponto_partida_parque_node_id, destino)

                    if caminho_para_destino:
                        initial_x, initial_y = self._get_scaled_coords(ponto_partida_parque_node_id)
                        self.pessoas.append({
                            'id': pessoa_id,
                            'caminho': caminho_para_destino,
                            'indice': 0,
                            'x': initial_x,
                            'y': initial_y,
                            'destino': destino,
                            'estado': 'indo',
                            'tempo_no_brinquedo': 0,
                            'brinquedos_visitados': set(),
                            'saindo': False,
                            'visitados_count': 0
                        })
                        self.last_person_spawn_time = current_time
                    else:
                        print(f"[{self.strategy_type}] Erro: Caminho Dijkstra vazio para o destino {destino} da pessoa {pessoa_id}.")
            time.sleep(0.05)

    def escolher_e_mover_para_proximo_brinquedo(self, pessoa, ponto_partida_proximo_caminho_node_id):
        brinquedos_nao_visitados = [b for b in self.brinquedos.keys() if b not in pessoa['brinquedos_visitados']]
        
        if brinquedos_nao_visitados:
            # Tenta ir para um não visitado que não esteja lotado
            candidatos_nao_lotados = [b for b in brinquedos_nao_visitados if self.brinquedos[b]['ocupados'] < self.brinquedos[b]['capacidade']]
            if candidatos_nao_lotados:
                novo_destino = random.choice(candidatos_nao_lotados)
            else:
                # Se todos os não visitados estão lotados, escolhe um aleatório para a fila
                novo_destino = random.choice(brinquedos_nao_visitados)
        else:
            # Se todos foram visitados, tenta um aleatório com menor fila
            brinquedos_com_fila_info = [(len(self.brinquedos[b]['fila']), b) for b in self.brinquedos.keys()]
            brinquedos_com_fila_info.sort() # Ordena pela fila
            novo_destino = brinquedos_com_fila_info[0][1] if brinquedos_com_fila_info else None

        if novo_destino is not None:
            pessoa['destino'] = novo_destino
            caminho_novo = self.caminho_dijkstra(ponto_partida_proximo_caminho_node_id, novo_destino)
            if caminho_novo:
                pessoa['caminho'] = caminho_novo
                pessoa['indice'] = 0
                pessoa['estado'] = 'indo'
            else:
                # Se não há caminho para o novo destino, direciona para a saída
                pessoa['saindo'] = True
                pessoa['caminho'] = self.caminho_saida(ponto_partida_proximo_caminho_node_id)
                pessoa['indice'] = 0
                pessoa['estado'] = 'saindo'
        else:
            # Não encontrou nenhum destino, direciona para a saída
            pessoa['saindo'] = True
            pessoa['caminho'] = self.caminho_saida(ponto_partida_proximo_caminho_node_id)
            pessoa['indice'] = 0
            pessoa['estado'] = 'saindo'


# Parque com Estratégia Heurística (A*)

class ParqueHeuristica(ParqueBase):
    def __init__(self, master, offset_x=0):
        super().__init__(master, offset_x, title_suffix="Heurística", strategy_type="heuristica")

    def gerar_pessoas(self):
        while self.rodando:
            if global_config.gerar_pessoas_ativo.get() and len(self.pessoas) < global_config.limite_pessoas_parque.get():
                current_time = time.time()
                time_since_last_spawn = current_time - self.last_person_spawn_time
                
                if time_since_last_spawn >= global_config.velocidade_entrada.get():
                    self.pessoa_id_counter += 1
                    pessoa_id = self.pessoa_id_counter

                    ponto_partida_parque_node_id = min(self.coordenadas_originais.keys(), key=lambda n: self.distancia(self.entrada_saida_original, self.coordenadas_originais[n]))
                    
                    brinquedos_disponiveis = list(self.brinquedos.keys())
                    if not brinquedos_disponiveis:
                        time.sleep(0.05)
                        continue

                    # O primeiro brinquedo é escolhido aleatoriamente
                    destino_inicial = random.choice(brinquedos_disponiveis)
                    proximo_destino = destino_inicial

                    if proximo_destino is not None:
                        caminho_para_destino, custo_caminho = self.calcular_caminho_a_star(ponto_partida_parque_node_id, proximo_destino)

                        if caminho_para_destino:
                            initial_x, initial_y = self._get_scaled_coords(ponto_partida_parque_node_id)
                            self.pessoas.append({
                                'id': pessoa_id,
                                'caminho': caminho_para_destino,
                                'indice': 0,
                                'x': initial_x,
                                'y': initial_y,
                                'destino': proximo_destino,
                                'estado': 'indo',
                                'tempo_no_brinquedo': 0,
                                'brinquedos_visitados': set(),
                                'saindo': False,
                                'visitados_count': 0 # Garante que a contagem de visitas começa em 0
                            })
                            self.last_person_spawn_time = current_time
                        else:
                            print(f"[{self.strategy_type}] Erro: Caminho vazio para o destino {proximo_destino} da pessoa {pessoa_id}. Não gerando pessoa.")
                    else:
                        print(f"[{self.strategy_type}] Não foi possível encontrar um destino para a pessoa {pessoa_id}. Não gerando pessoa.")
            time.sleep(0.05)

    def escolher_e_mover_para_proximo_brinquedo(self, pessoa, ponto_partida_proximo_caminho_node_id):
        # A partir da segunda visita (visitados_count > 0), usa A*
        novo_destino, _ = self.escolher_proximo_brinquedo_a_star(
            ponto_partida_proximo_caminho_node_id,
            pessoa['brinquedos_visitados']
        )
        
        if novo_destino is not None:
            pessoa['destino'] = novo_destino
            caminho_novo, _ = self.calcular_caminho_a_star(
                ponto_partida_proximo_caminho_node_id,
                novo_destino
            )
            if caminho_novo:
                pessoa['caminho'] = caminho_novo
                pessoa['indice'] = 0
                pessoa['estado'] = 'indo'
            else:
                print(f"[{self.strategy_type}] Erro: Caminho vazio para o novo destino {novo_destino} da pessoa {pessoa['id']}. Direcionando para saída.")
                pessoa['saindo'] = True
                pessoa['caminho'] = self.caminho_saida(ponto_partida_proximo_caminho_node_id)
                pessoa['indice'] = 0
                pessoa['estado'] = 'saindo'
        else:
            print(f"[{self.strategy_type}] Pessoa {pessoa['id']}: Não encontrou próximo destino, direcionando para saída.")
            pessoa['saindo'] = True
            pessoa['caminho'] = self.caminho_saida(ponto_partida_proximo_caminho_node_id)
            pessoa['indice'] = 0
            pessoa['estado'] = 'saindo'



# Inicia aplicação principal


class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulação de Parques - Heurística vs. Aleatório")

        self.master.state('zoomed')
        self.master.bind("<Escape>", lambda event: self.master.attributes('-fullscreen', False))

        self.master.grid_columnconfigure(0, weight=4)
        self.master.grid_columnconfigure(1, weight=1, minsize=180)
        self.master.grid_columnconfigure(2, weight=4)
        self.master.grid_rowconfigure(0, weight=1)

        self.frame_heuristica = tk.Frame(self.master)
        self.frame_heuristica.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.frame_controle = tk.Frame(self.master) # Removido bg aqui para que o place dos filhos defina o fundo
        self.frame_controle.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.frame_aleatorio = tk.Frame(self.master)
        self.frame_aleatorio.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.parque_heuristica = ParqueHeuristica(self.frame_heuristica)
        self.parque_aleatorio = ParqueAleatorio(self.frame_aleatorio)

        self.parque_heuristica.gerador_pessoas_thread = threading.Thread(target=self.parque_heuristica.gerar_pessoas, daemon=True)
        self.parque_heuristica.gerador_pessoas_thread.start()

        self.parque_aleatorio.gerador_pessoas_thread = threading.Thread(target=self.parque_aleatorio.gerar_pessoas, daemon=True)
        self.parque_aleatorio.gerador_pessoas_thread.start()

        
        self.controls_overlay_frame = tk.Frame(self.frame_controle, bg="#333333", bd=0, highlightthickness=0)
        self.controls_overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=0.6) # Ocupa os 60% superiores

        
        self.video_canvas_menu = tk.Canvas(self.frame_controle, bg="#333333", highlightthickness=0)
        self.video_canvas_menu.place(relx=0, rely=0.6, relwidth=1, relheight=0.3) # Ocupa os 30% seguintes
        self.video_canvas_image_id = self.video_canvas_menu.create_image(0, 0, anchor=tk.NW)
        self.video_canvas_menu.bind("<Configure>", self._resize_video_background)

        
        self.qiqi_label = tk.Label(self.frame_controle, text="parque das qiqis", fg="#FF69B4", bg="#333333",
                                   font=('Comic Sans MS', 20, 'bold')) # Aumentei o tamanho da fonte
        self.qiqi_label.place(relx=0, rely=0.9, relwidth=1, relheight=0.1) 

        self.setup_control_menu()
        
        self.video_capture = None #
        self._current_video_frame = None 
        self.load_video("qiqi_dancante.mp4")
        

    def _resize_video_background(self, event=None):
        canvas_width = self.video_canvas_menu.winfo_width()
        canvas_height = self.video_canvas_menu.winfo_height()

        if canvas_width == 0 or canvas_height == 0:
            
            return

        # Limpa o conteúdo anterior do canvas do vídeo
        self.video_canvas_menu.delete("all")

        if self._current_video_frame is not None:
            try:
                frame_rgb = cv2.cvtColor(self._current_video_frame, cv2.COLOR_BGR2RGB)
                
                frame_height, frame_width, _ = frame_rgb.shape
                aspect_ratio_frame = frame_width / frame_height
                aspect_ratio_canvas = canvas_width / canvas_height

                if aspect_ratio_frame > aspect_ratio_canvas:
                    new_width = canvas_width
                    new_height = int(canvas_width / aspect_ratio_frame)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * aspect_ratio_frame)
                
                resized_frame = cv2.resize(frame_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
                img = Image.fromarray(resized_frame)
                self.video_tk = ImageTk.PhotoImage(image=img) 
                
                
                self.video_canvas_menu.create_image(
                    (canvas_width - new_width) / 2, (canvas_height - new_height) / 2,
                    image=self.video_tk,
                    anchor=tk.NW,
                    tags="video_image"
                )
            except Exception as e:
                print(f"Erro ao redimensionar/desenhar frame de vídeo: {e}")
                self.video_canvas_menu.create_text(canvas_width / 2, canvas_height / 2,
                                                   text="Erro ao processar vídeo", fill="red", font=('Arial', 10, 'bold'))
        else:
            
            self.video_canvas_menu.create_text(canvas_width / 2, canvas_height / 2,
                                               text="Vídeo Não Disponível", fill="white", font=('Arial', 10, 'bold'))


    def animate_video(self):
        if self.video_capture and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if ret:
                self._current_video_frame = frame # Armazena o frame atual
                self._resize_video_background() 
                self.master.after(50, self.animate_video)
            else:
                
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.animate_video()
        else:
            
            self._resize_video_background()


    def setup_control_menu(self):
        
        tk.Label(self.controls_overlay_frame, text="Configurações do Parque", fg="white", bg=self.controls_overlay_frame.cget('bg'), font=('Arial', 10, 'bold')).pack(pady=3)

        tk.Label(self.controls_overlay_frame, text="Geração (segundos):", fg="white", bg=self.controls_overlay_frame.cget('bg')).pack(pady=1)
        scale_velocidade_entrada = tk.Scale(self.controls_overlay_frame, from_=0.1, to_=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                            variable=global_config.velocidade_entrada, fg="white", bg=self.controls_overlay_frame.cget('bg'), troughcolor="#555555", length=150)
        scale_velocidade_entrada.pack(pady=1)

        tk.Label(self.controls_overlay_frame, text="Movimento (unidades/s):", fg="white", bg=self.controls_overlay_frame.cget('bg')).pack(pady=1)
        scale_velocidade_movimento = tk.Scale(self.controls_overlay_frame, from_=1.0, to_=10.0, resolution=0.5, orient=tk.HORIZONTAL,
                                              variable=global_config.velocidade_movimento_pessoa, fg="white", bg=self.controls_overlay_frame.cget('bg'), troughcolor="#555555", length=150)
        scale_velocidade_movimento.pack(pady=1)

        tk.Label(self.controls_overlay_frame, text="Tempo no Brinquedo (s):", fg="white", bg=self.controls_overlay_frame.cget('bg')).pack(pady=1)
        scale_tempo_brinquedo = tk.Scale(self.controls_overlay_frame, from_=1.0, to_=10.0, resolution=1.0, orient=tk.HORIZONTAL,
                                         variable=global_config.tempo_no_brinquedo, fg="white", bg=self.controls_overlay_frame.cget('bg'), troughcolor="#555555", length=150)
        scale_tempo_brinquedo.pack(pady=1)

        tk.Label(self.controls_overlay_frame, text="Limite de Pessoas:", fg="white", bg=self.controls_overlay_frame.cget('bg')).pack(pady=1)
        scale_limite_pessoas = tk.Scale(self.controls_overlay_frame, from_=10, to_=200, resolution=10, orient=tk.HORIZONTAL,
                                        variable=global_config.limite_pessoas_parque, fg="white", bg=self.controls_overlay_frame.cget('bg'), troughcolor="#555555", length=150)
        scale_limite_pessoas.pack(pady=1)

        btn_toggle_geracao = tk.Button(self.controls_overlay_frame, text="Parar Geração", command=self.toggle_geracao_pessoas, bg="#008CBA", fg="white", relief=tk.RAISED, font=('Arial', 9))
        btn_toggle_geracao.pack(pady=5)
        self.btn_toggle_geracao = btn_toggle_geracao

        tk.Label(self.controls_overlay_frame, text="Legendas:", fg="white", bg=self.controls_overlay_frame.cget('bg'), font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Frame para as legendas em colunas
        legend_frame_columns = tk.Frame(self.controls_overlay_frame, bg=self.controls_overlay_frame.cget('bg'))
        legend_frame_columns.pack(pady=3)
        legend_frame_columns.grid_columnconfigure(0, weight=1)
        legend_frame_columns.grid_columnconfigure(1, weight=1)


        # LEGENDAS EM COLUNAS
        row_idx = 0
        if person_images:
            # Coluna 0: Heurística
            if person_images.get('heuristica_indo'):
                frame_leg_heur_indo = tk.Frame(legend_frame_columns, bg=self.controls_overlay_frame.cget('bg'))
                frame_leg_heur_indo.grid(row=row_idx, column=0, sticky="w", padx=2, pady=1)
                tk.Label(frame_leg_heur_indo, image=person_images['heuristica_indo'], bg=self.controls_overlay_frame.cget('bg')).pack(side=tk.LEFT)
                tk.Label(frame_leg_heur_indo, text="Heurística (Andando)", fg="white", bg=self.controls_overlay_frame.cget('bg'), font=('Arial', 10)).pack(side=tk.LEFT) # Font size increased
            row_idx += 1
            if person_images.get('heuristica_saindo'):
                frame_leg_heur_saindo = tk.Frame(legend_frame_columns, bg=self.controls_overlay_frame.cget('bg'))
                frame_leg_heur_saindo.grid(row=row_idx, column=0, sticky="w", padx=2, pady=1)
                tk.Label(frame_leg_heur_saindo, image=person_images['heuristica_saindo'], bg=self.controls_overlay_frame.cget('bg')).pack(side=tk.LEFT)
                tk.Label(frame_leg_heur_saindo, text="Heurística (Saindo)", fg="white", bg=self.controls_overlay_frame.cget('bg'), font=('Arial', 10)).pack(side=tk.LEFT) # Font size increased
            row_idx += 1

            # Coluna 1: Aleatório
            current_row_idx = 0
            if person_images.get('aleatorio_indo'):
                frame_leg_ale_indo = tk.Frame(legend_frame_columns, bg=self.controls_overlay_frame.cget('bg'))
                frame_leg_ale_indo.grid(row=current_row_idx, column=1, sticky="w", padx=2, pady=1)
                tk.Label(frame_leg_ale_indo, image=person_images['aleatorio_indo'], bg=self.controls_overlay_frame.cget('bg')).pack(side=tk.LEFT)
                tk.Label(frame_leg_ale_indo, text="Aleatório (Andando)", fg="white", bg=self.controls_overlay_frame.cget('bg'), font=('Arial', 10)).pack(side=tk.LEFT) 
            current_row_idx += 1
            if person_images.get('aleatorio_saindo'):
                frame_leg_ale_saindo = tk.Frame(legend_frame_columns, bg=self.controls_overlay_frame.cget('bg'))
                frame_leg_ale_saindo.grid(row=current_row_idx, column=1, sticky="w", padx=2, pady=1)
                tk.Label(frame_leg_ale_saindo, image=person_images['aleatorio_saindo'], bg=self.controls_overlay_frame.cget('bg')).pack(side=tk.LEFT)
                tk.Label(frame_leg_ale_saindo, text="Aleatório (Saindo)", fg="white", bg=self.controls_overlay_frame.cget('bg'), font=('Arial', 10)).pack(side=tk.LEFT) 
            current_row_idx += 1

    def toggle_geracao_pessoas(self):
        current_state = global_config.gerar_pessoas_ativo.get()
        global_config.gerar_pessoas_ativo.set(not current_state)
        if global_config.gerar_pessoas_ativo.get():
            self.btn_toggle_geracao.config(text="Parar Geração", bg="#008CBA")
        else:
            self.btn_toggle_geracao.config(text="Iniciar Geração", bg="#FFA500")

    def load_video(self, video_path):
        try:
            self.video_capture = cv2.VideoCapture(video_path)
            if not self.video_capture.isOpened():
                raise IOError(f"Não foi possível abrir o arquivo de vídeo: {video_path}")
            
            
            ret, frame = self.video_capture.read()
            if ret:
                self._current_video_frame = frame
            
            self.animate_video() 
        except Exception as e:
            print(f"Erro ao carregar ou reproduzir vídeo: {e}")
            self.video_capture = None
            self._current_video_frame = None # Garante que não há frame para tentar desenhar
            self._resize_video_background() 


    def on_closing(self):
        self.parque_heuristica.rodando = False
        self.parque_aleatorio.rodando = False
        if self.video_capture:
            self.video_capture.release()
        time.sleep(0.1)
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    global_config = GlobalConfig()
    load_person_images()
    app = MainApplication(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
