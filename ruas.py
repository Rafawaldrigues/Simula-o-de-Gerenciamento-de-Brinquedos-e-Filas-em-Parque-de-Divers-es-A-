import tkinter as tk
from PIL import Image, ImageTk
import json
# script criado com o intuito de mapear o grafo e gerar os caminhos (ruas) e brinquedos 
class EditorRuas:
    def __init__(self, master):
        self.master = master
        self.master.title("Editor de Ruas - Criar Grafo de Caminhos")
        
        self.canvas = tk.Canvas(self.master, width=1020, height=900)
        self.canvas.pack()
        
        self.img = Image.open("parque.png")
        self.img = self.img.resize((1020, 900))
        self.fundo = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image=self.fundo, anchor=tk.NW)
        
        # dados do grafo
        self.nos = {}  # id: (x,y)
        self.arestas = []  # (id_no1, id_no2)
        self.no_id_seq = 1
        
        # para criar arestas: armazenar o nó selecionado para conectar
        self.no_selecionado = None
        
        # para seleção e remoção de arestas
        self.aresta_selecionada = None
        
        # interface para remover arestas
        btn_remover = tk.Button(self.master, text="Remover Aresta Selecionada", command=self.remover_aresta)
        btn_remover.pack(pady=5)
        
        btn_salvar = tk.Button(self.master, text="Salvar Grafo", command=self.salvar_grafo)
        btn_salvar.pack(pady=5)
        
        btn_carregar = tk.Button(self.master, text="Carregar Grafo", command=self.carregar_grafo)
        btn_carregar.pack(pady=5)
        
        self.canvas.bind("<Button-1>", self.clique)
        self.canvas.bind("<Button-3>", self.clique_direito)
        
        self.desenhar()
        
    def clique(self, event):
        x, y = event.x, event.y
        
        # verificar se clicou perto de um nó existente
        no_clicado = self.no_proximo(x, y)
        if no_clicado:
            # se já tem um nó selecionado para conexão
            if self.no_selecionado is None:
                self.no_selecionado = no_clicado
            else:
                if self.no_selecionado != no_clicado:
                    # criar aresta entre os dois nós
                    if not self.existe_aresta(self.no_selecionado, no_clicado):
                        self.arestas.append((self.no_selecionado, no_clicado))
                self.no_selecionado = None
        else:
            # criar novo nó
            self.nos[self.no_id_seq] = (x, y)
            self.no_id_seq += 1
            self.no_selecionado = None
        
        self.aresta_selecionada = None
        self.desenhar()
        
    def clique_direito(self, event):
        x, y = event.x, event.y
        
        # clique direito para selecionar aresta próxima
        aresta = self.aresta_proxima(x, y)
        if aresta:
            self.aresta_selecionada = aresta
        else:
            self.aresta_selecionada = None
        self.desenhar()
    
    def no_proximo(self, x, y, tol=15):
        # retorna o id do nó que estiver a menos de tol pixels de (x,y)
        for no_id, (nx, ny) in self.nos.items():
            if abs(nx - x) <= tol and abs(ny - y) <= tol:
                return no_id
        return None
    
    def existe_aresta(self, n1, n2):
        return (n1, n2) in self.arestas or (n2, n1) in self.arestas
    
    def remover_aresta(self):
        if self.aresta_selecionada:
            a, b = self.aresta_selecionada
            if (a,b) in self.arestas:
                self.arestas.remove((a,b))
            elif (b,a) in self.arestas:
                self.arestas.remove((b,a))
            self.aresta_selecionada = None
            self.desenhar()
    
    def aresta_proxima(self, x, y, tol=10):
        # retorna a aresta que está próxima do ponto (x,y)
        for (a, b) in self.arestas:
            x1, y1 = self.nos[a]
            x2, y2 = self.nos[b]
            # distância do ponto a linha (x1,y1)-(x2,y2)
            if self.ponto_perto_linha(x, y, x1, y1, x2, y2, tol):
                return (a,b)
        return None
    
    def ponto_perto_linha(self, px, py, x1, y1, x2, y2, tol):
        # cálculo da distância do ponto (px,py) à linha (x1,y1)-(x2,y2)
        if (x1, y1) == (x2, y2):
            return False
        # fórmula da distância ponto-linha
        num = abs((y2 - y1)*px - (x2 - x1)*py + x2*y1 - y2*x1)
        den = ((y2 - y1)**2 + (x2 - x1)**2)**0.5
        dist = num / den
        if dist > tol:
            return False
        
        # verificar se projeção está entre os pontos (segmento)
        dot1 = (px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)
        dot2 = (px - x2)*(x1 - x2) + (py - y2)*(y1 - y2)
        return dot1 >= 0 and dot2 >= 0
    
    def desenhar(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.fundo, anchor=tk.NW)
        
        # desenhar arestas
        for (a, b) in self.arestas:
            x1, y1 = self.nos[a]
            x2, y2 = self.nos[b]
            cor = "red" if self.aresta_selecionada == (a,b) or self.aresta_selecionada == (b,a) else "black"
            self.canvas.create_line(x1, y1, x2, y2, fill=cor, width=3)
        
        # desenhar nós
        for no_id, (x, y) in self.nos.items():
            cor = "orange" if self.no_selecionado == no_id else "blue"
            self.canvas.create_oval(x-8, y-8, x+8, y+8, fill=cor)
            self.canvas.create_text(x, y, text=str(no_id), fill="white")
    
    def salvar_grafo(self):
        data = {
            "nos": self.nos,
            "arestas": self.arestas
        }
        with open("grafo_ruas.json", "w") as f:
            json.dump(data, f)
        print("Grafo salvo em grafo_ruas.json")
    
    def carregar_grafo(self):
        try:
            with open("grafo_ruas.json", "r") as f:
                data = json.load(f)
            self.nos = {int(k): tuple(v) for k, v in data["nos"].items()}
            self.arestas = [tuple(a) for a in data["arestas"]]
            self.no_id_seq = max(self.nos.keys()) + 1 if self.nos else 1
            self.no_selecionado = None
            self.aresta_selecionada = None
            self.desenhar()
            print("Grafo carregado de grafo_ruas.json")
        except Exception as e:
            print("Erro ao carregar grafo:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorRuas(root)
    root.mainloop()
