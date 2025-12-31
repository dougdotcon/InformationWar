import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional

class SocialBubbleSimulation:
    """
    Simula a formação de bolhas sociais e tendências usando 
    Modelo de Ising em Redes de Barabási-Albert.
    
    A topologia Scale-Free (Barabási-Albert) emula redes sociais reais,
    onde poucos influenciadores (hubs) possuem muitas conexões.
    """
    def __init__(self, n_users: int, m_edges: int, seed: int = 42):
        """
        Inicializa a simulação.
        """
        np.random.seed(seed)
        self.graph = nx.barabasi_albert_graph(n_users, m_edges, seed=seed)
        self.states = np.random.choice([-1, 1], size=n_users)
        self.n_users = n_users
        
        # Cache de vizinhos para otimização
        self._neighbors = {node: list(self.graph.neighbors(node)) for node in range(n_users)}

    def compute_energy_change(self, node: int, external_field: float, J: float) -> float:
        """
        Calcula a variação de energia (dE).
        """
        neighbor_sum = sum(self.states[n] for n in self._neighbors[node])
        return 2 * self.states[node] * (J * neighbor_sum + external_field)

    def run_metropolis(self, steps: int, T: float, h: float, J: float = 1.0, pinned_nodes: set = None) -> List[float]:
        """
        Executa a dinâmica de Monte Carlo.
        Suporta 'Pinning Control': nós no conjunto pinned_nodes não mudam de estado.
        """
        history = []
        pinned = pinned_nodes if pinned_nodes else set()
        
        for _ in range(steps):
            node = np.random.randint(0, self.n_users)
            
            # Se o nó foi "comprado" (pinned), ele não muda de opinião.
            if node in pinned:
                continue
                
            delta_E = self.compute_energy_change(node, h, J)
            
            if delta_E <= 0 or np.random.random() < np.exp(-delta_E / T):
                self.states[node] *= -1
            
            # Otimização: append histórico apenas a cada N passos se desejado, 
            # mas manteremos a cada passo para consistência.
            history.append(np.mean(self.states))
            
        return history

    def identify_influencers(self, top_k: int = 5) -> List[Tuple[int, float]]:
        """Identifica os principais influenciadores baseados na Centralidade de Grau."""
        centrality = nx.degree_centrality(self.graph)
        sorted_influencers = sorted(centrality.items(), key=lambda item: item[1], reverse=True)
        return sorted_influencers[:top_k]
        
    def identify_eigenvector_hubs(self, top_k: int = 5) -> List[Tuple[int, float]]:
        """Identifica influenciadores estratégicos por Centralidade de Autovetor."""
        try:
            centrality = nx.eigenvector_centrality(self.graph, max_iter=1000)
            sorted_influencers = sorted(centrality.items(), key=lambda item: item[1], reverse=True)
            return sorted_influencers[:top_k]
        except:
            return self.identify_influencers(top_k)

    def simulate_attack(self, target_nodes: List[int], steps: int, T: float, h: float, J: float = 1.0) -> List[float]:
        """
        Simula um ataque onde os 'target_nodes' são forçados a -1 (oposição) e fixados.
        Retorna a evolução da magnetização.
        """
        pinned = set(target_nodes)
        
        # Forçar alvos para a nova tendência (-1)
        for node in target_nodes:
            self.states[node] = -1
            
        return self.run_metropolis(steps, T, h, J, pinned_nodes=pinned)

    def compute_susceptibility(self, history: List[float], T: float) -> float:
        """Calcula a Susceptibilidade Magnética (Social)."""
        if not history:
            return 0.0
        magnetization = np.array(history[len(history)//2:])
        variance = np.var(magnetization)
        return (variance * self.n_users) / T

    def detect_communities(self) -> List[set]:
        """Detecta comunidades usando o algoritmo de Louvain."""
        try:
            return nx.community.louvain_communities(self.graph, seed=42)
        except AttributeError:
            return nx.community.greedy_modularity_communities(self.graph)
        except Exception as e:
            return nx.community.greedy_modularity_communities(self.graph)

    def analyze_communities(self, communities: List[set], h: float, J: float) -> Dict[int, Dict]:
        """Analisa cada comunidade para classificar como 'Orgânica' ou 'Forçada'."""
        analysis = {}
        for idx, community in enumerate(communities):
            nodes = list(community)
            size = len(nodes)
            if size == 0: continue
            
            states_vals = [self.states[n] for n in nodes]
            avg_state = np.mean(states_vals)
            
            internal_links_energy = 0
            for i in nodes:
                for neighbor in self._neighbors[i]:
                    if neighbor in community: 
                        internal_links_energy += -J * self.states[i] * self.states[neighbor]
            
            internal_links_energy /= 2.0
            avg_internal_energy = abs(internal_links_energy / size)

            external_energy = -h * np.sum(states_vals)
            avg_external_energy = abs(external_energy / size)
            
            dominance_ratio = avg_internal_energy / (avg_external_energy + 1e-9)
            
            if abs(avg_state) < 0.2:
                type_label = "Desorganizada"
            elif dominance_ratio > 3.0:
                type_label = "Orgânica (Forte)"
            elif dominance_ratio > 1.0:
                type_label = "Mista"
            else:
                type_label = "Induzida (Artificial)"

            analysis[idx] = {
                "size": size,
                "avg_state": avg_state,
                "internal_E_avg": avg_internal_energy,
                "external_E_avg": avg_external_energy,
                "ratio": dominance_ratio,
                "type": type_label
            }
        return analysis

    def visualize_network(self, highlight_nodes: List[int] = None, title: str = "Rede Social"):
        """Visualiza a rede."""
        pos = nx.spring_layout(self.graph, seed=42, k=0.1)
        node_colors = ['red' if s == 1 else 'blue' for s in self.states]
        
        plt.figure(figsize=(10, 8))
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=20, alpha=0.7)
        nx.draw_networkx_edges(self.graph, pos, alpha=0.1)
        
        if highlight_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=highlight_nodes, 
                                 node_size=150, node_color='yellow', edgecolors='black', label='Alvos/Influencers')
            plt.legend()

        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(f"{title.replace(' ', '_').replace(':', '').lower()}.png")
        plt.close()

if __name__ == "__main__":
    # --- Configuração ---
    N_USERS = 1000
    M_EDGES = 3 
    STEPS = 50000 
    TEMP = 2.0    
    FIELD = 0.1   
    
    print(f"--- Fase 1: Estabelecendo Consenso (+1) ---")
    sim = SocialBubbleSimulation(N_USERS, M_EDGES)
    # Start biased para +1
    sim.states = np.random.choice([1, 1, 1, -1], size=N_USERS) 
    sim.run_metropolis(steps=20000, T=TEMP, h=FIELD)
    initial_mag = np.mean(sim.states)
    print(f"Magnetização Inicial Estabilizada: {initial_mag:.2f}")
    
    # Identificar alvos - Eigenvector é mais "sagaz" que apenas Grau
    eigen_hubs = [n for n, _ in sim.identify_eigenvector_hubs(60)]
    random_users = list(np.random.choice(range(N_USERS), 60, replace=False))
    
    print(f"\n--- Fase 2: Simulação de Ataque Direcionado (Pinning) ---")
    print(f"Objetivo: Reverter tendência de +{initial_mag:.1f} para valores negativos.")
    print(f"Campo Externo Hostil (Mantido a favor do +1): h={FIELD} (Ataque luta contra o algoritmo)")
    
    results = {'Hubs (Eigen)': [], 'Random': []}
    budget_range = [0, 5, 10, 20, 30, 40, 50, 60]
    
    initial_states_backup = sim.states.copy()
    
    for budget in budget_range:
        # --- Simulação Hubs ---
        sim.states = initial_states_backup.copy()
        targets = eigen_hubs[:budget]
        
        # O ataque consiste em fixar esses nós em -1
        # E rodar a simulação para ver se o resto da rede vira
        hist = sim.simulate_attack(targets, steps=30000, T=TEMP, h=FIELD, J=1.0)
        final_mag_hub = np.mean(hist[-1000:]) # média dos últimos 1000 passos
        results['Hubs (Eigen)'].append(final_mag_hub)
        
        # --- Simulação Random ---
        sim.states = initial_states_backup.copy()
        targets_rnd = random_users[:budget]
        hist_rnd = sim.simulate_attack(targets_rnd, steps=30000, T=TEMP, h=FIELD, J=1.0)
        final_mag_rnd = np.mean(hist_rnd[-1000:])
        results['Random'].append(final_mag_rnd)
        
        print(f"Budget: {budget:2d} | Mag Hub: {final_mag_hub:+.2f} | Mag Random: {final_mag_rnd:+.2f}")

    # Visualização
    plt.figure(figsize=(10, 6))
    plt.plot(budget_range, results['Hubs (Eigen)'], 'o-', label='Ataque a Hubs (Eigenvector)', color='firebrick', linewidth=2)
    plt.plot(budget_range, results['Random'], 's--', label='Ataque Aleatório', color='gray', alpha=0.7)
    
    plt.axhline(y=0, color='black', linestyle=':', linewidth=2, label='Inversão de Tendência')
    plt.axhline(y=initial_mag, color='green', linestyle='--', alpha=0.3, label='Consenso Original')
    
    plt.xlabel("Número de Influenciadores Comprados (Pinning)")
    plt.ylabel("Consenso Final da Rede (Magnetização)")
    plt.title(f"Targeted Phase Transition: Custo para Inverter Opinião Pública")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("ataque_direcionado.png")
    print("\nGráfico salvo: ataque_direcionado.png")
    
    # Análise Final
    critical_budget = next((b for b, m in zip(budget_range, results['Hubs (Eigen)']) if m < 0), None)
    
    if critical_budget:
        print(f"\n[RELATÓRIO DE INTELIGÊNCIA]")
        print(f"PONTO DE RUPTURA IDENTIFICADO: {critical_budget} Influenciadores Estratégicos.")
        print(f"Isso representa apenas {critical_budget/N_USERS:.1%} da população para derrubar o regime/tendência.")
    else:
        print("\n[RELATÓRIO DE INTELIGÊNCIA]")
        print("A rede resistiu ao ataque máximo. Necessário aumentar orçamento de hubs ou temperatura (T).")
