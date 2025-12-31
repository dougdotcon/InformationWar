import os
import sys
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import requests
import re
import pandas as pd

# Correção Protobuf
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# --- CLASSE DE INTELIGÊNCIA (REUTILIZADA DA VERSÃO ROBUSTA) ---
class HeuristicPhysicsModel:
    """Fallback seguro."""
    def analyze(self, text):
        pain_keywords = ['hate', 'problem', 'stuck', 'angry', 'fail', 'slow', 'expensive', 'hard', 'impossible', 'sucks', 'pain', 'need', 'worst', 'help', 'desperate']
        text_lower = text.lower()
        score = 0.1
        hit_count = 0
        for word in pain_keywords:
            if word in text_lower:
                score += 0.15
                hit_count += 1
        
        # Penaliza textos muito curtos que podem ser falsos positivos
        if len(text) < 20: score *= 0.5
        
        thermal_noise = np.random.normal(0, 0.05)
        return min(max(score + thermal_noise, 0.0), 1.0)

class RedditPhysicsIntelligence:
    def __init__(self):
        self.headers = {'User-agent': 'PhysicsBot Portfolio/2.0'}
        self.model = HeuristicPhysicsModel() # Usando Heurística direto para velocidade no Scan de Portfólio
        print("[INIT] Sensor Físico Inicializado (Modo Alta Frequência).")

    def fetch_data(self, subreddit, limit=15):
        url = f"https://www.reddit.com/r/{subreddit}/.json?limit={limit}"
        try:
            r = requests.get(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                return r.json()['data']['children']
        except:
            pass
        return []

    def scan_sector(self, subreddit):
        """Scaneia um setor (subreddit) e retorna métricas macroscópicas."""
        posts = self.fetch_data(subreddit)
        if not posts: return None

        pain_values = []
        h_values = []
        titles = []

        print(f"  > Analisando r/{subreddit} ({len(posts)} amostras)...")
        for p in posts:
            data = p['data']
            text = (data.get('title', '') + " " + data.get('selftext', ''))
            
            # Observáveis
            pain = self.model.analyze(text)
            h = np.log(data.get('ups', 1) + 1)
            
            pain_values.append(pain)
            h_values.append(h)
            titles.append(data.get('title', '')[:30])

        # Cálculos Termodinâmicos
        N = len(pain_values)
        avg_pain = np.mean(pain_values)
        avg_h = np.mean(h_values)
        
        # Susceptibilidade: Chi = N * Var(S) / T
        variance = np.var(pain_values)
        chi = (N * variance) / 1.0 # T=1
        
        # Opportunity Score: Combinação de Susceptibilidade (Volatilidade) e Dor Média (Potencial)
        # Se Chi é alto mas Dor é baixa -> Muito ruído, pouco valor.
        # Se Chi é alto e Dor é alta -> Oportunidade Crítica.
        opp_score = chi * avg_pain * 10 

        return {
            'subreddit': subreddit,
            'chi': chi,
            'avg_pain': avg_pain,
            'avg_vis': avg_h,
            'opp_score': opp_score,
            'samples': N,
            'top_pain_title': titles[np.argmax(pain_values)] if titles else ''
        }

# --- MONITOR DE PORTFOLIO ---
if __name__ == "__main__":
    
    SUBREDDITS = [
        'Entrepreneur', 'Startups', 'SaaS', 'Marketing', 
        'Productivity', 'SideProject', 'SmallBusiness', 
        'Python', 'WebDev', 'DataScience', 
        'Investing', 'WallStreetBets', 'RealEstate'
    ]
    
    print(f"--- INICIANDO ESCANEAMENTO DE PORTFÓLIO ({len(SUBREDDITS)} SETORES) ---")
    bot = RedditPhysicsIntelligence()
    
    results = []
    start_time = time.time()
    
    for sub in SUBREDDITS:
        data = bot.scan_sector(sub)
        if data:
            results.append(data)
        time.sleep(1.5) # Respeitar rate limit
        
    # --- ANÁLISE COMPARATIVA ---
    df = pd.DataFrame(results)
    
    # Ordenar por Opportunity Score (Ouro)
    df_sorted = df.sort_values(by='opp_score', ascending=False)
    
    print("\n--- RANKING DE OPORTUNIDADES (TOP 5) ---")
    print(df_sorted[['subreddit', 'opp_score', 'chi', 'avg_pain']].head(5).to_string(index=False))
    
    # Salvar Relatório
    os.makedirs('relatos', exist_ok=True)
    df_sorted.to_csv('relatos/portfolio_ranking.csv', index=False)
    
    # --- GERAÇÃO DE ARTEFATO VISUAL (MATRIZ DE DISPERSÃO) ---
    plt.figure(figsize=(12, 8))
    
    # Plot Scatter
    x = df['chi']
    y = df['avg_pain']
    sizes = df['opp_score'] * 20 + 50 # Tamanho da bolha = Oportunidade
    
    scatter = plt.scatter(x, y, s=sizes, c=sizes, cmap='viridis', alpha=0.7, edgecolors='black')
    
    # Anotar nomes
    for i, row in df.iterrows():
        plt.annotate(
            row['subreddit'], 
            (row['chi'], row['avg_pain']),
            xytext=(5, 5), textcoords='offset points',
            fontsize=9, weight='bold'
        )
        
    plt.title('Matriz de Portfólio: Susceptibilidade vs Dor Média')
    plt.xlabel('Susceptibilidade de Mercado ($\chi$) - Volatilidade/Influenciabilidade')
    plt.ylabel('Densidade de Dor Média (S) - Demanda Latente')
    plt.colorbar(scatter, label='Opportunity Score')
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Zonas Estratégicas
    plt.axvline(x=df['chi'].mean(), color='red', linestyle=':', label='Média $\chi$')
    plt.axhline(y=df['avg_pain'].mean(), color='blue', linestyle=':', label='Média S')
    
    # Destacar "Quadrante de Ouro"
    plt.text(df['chi'].max()*0.8, df['avg_pain'].max(), "GOLD MINE\n(High Chi, High Pain)", 
             color='green', weight='bold', ha='center')

    output_path = 'assets/portfolio_matrix.png'
    os.makedirs('assets', exist_ok=True)
    plt.savefig(output_path)
    print(f"\nMatriz salva em: {output_path}")
    print(f"Tempo total: {time.time()-start_time:.1f}s")
