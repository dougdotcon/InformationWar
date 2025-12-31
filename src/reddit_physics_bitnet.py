import os
import sys
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import requests
import re

# Correção Protobuf para Windows
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class HeuristicPhysicsModel:
    """Modelo de Física Social de Fallback (Caso BitNet não carregue)."""
    def generate(self, **kwargs):
        # Simula atraso de inferência
        time.sleep(0.1)
        return None 

    def analyze(self, text):
        # Heurística de palavras-chave para 'Dor'
        pain_keywords = ['hate', 'problem', 'stuck', 'angry', 'fail', 'slow', 'expensive', 'hard', 'impossible', 'sucks', 'pain', 'worst', 'help']
        text_lower = text.lower()
        score = 0.1
        for word in pain_keywords:
            if word in text_lower:
                score += 0.15
        
        # Adiciona aleatoriedade térmica (Temperatura T)
        thermal_noise = np.random.normal(0, 0.1)
        return min(max(score + thermal_noise, 0.0), 1.0)

class RedditPhysicsIntelligence:
    def __init__(self, model_path: str, subreddit_url: str):
        self.url = f"{subreddit_url}/.json"
        
        print(f"[INIT] Carregando Modelo Neural de: {model_path}")
        self.use_bitnet = False
        self.model = None
        self.tokenizer = None
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Tentar carregar como Llama (com config hackeado)
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path, 
                    device_map="cpu", 
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                self.use_bitnet = True
                print("[INIT] Modelo BitNet (Llama-Kernel) Carregado Vital!")
            except Exception as e_load:
                print(f"[WARN] Falha ao carregar pesos BitNet: {e_load}")
                print("[INFO] Ativando Fallback para Modelo Heurístico de Física Social.")
                self.model = HeuristicPhysicsModel()

        except Exception as e:
            print(f"[WARN] Erro crítico de Importação ({e}). Usando modo Heurístico.")
            self.model = HeuristicPhysicsModel()

        self.headers = {'User-agent': 'PhysicsBot 2.0'}

    def fetch_market_energy(self, limit=10):
        print(f"[NET] Coletando fótons de informação (Posts) de {self.url}...")
        try:
            response = requests.get(f"{self.url}?limit={limit}", headers=self.headers)
            if response.status_code != 200:
                return []
            return response.json()['data']['children']
        except:
            return []

    def analyze_pain(self, text):
        if not self.use_bitnet:
            return self.model.analyze(text)
        
        # Inferência BitNet real
        prompt = f"Rate pain 0-10: '{text[:200]}'\nScore:"
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                out = self.model.generate(**inputs, max_new_tokens=3)
            resp = self.tokenizer.decode(out[0], skip_special_tokens=True)
            match = re.search(r'\d+', resp)
            if match: return min(float(match.group())/10, 1.0)
        except:
            pass
        return 0.2

    def scan_market(self):
        posts = self.fetch_market_energy(limit=8)
        results = []
        
        print(f"\n[PHYSICS] Processando {len(posts)} estados de spin...")
        for p in posts:
            data = p['data']
            title = data.get('title', '')
            
            h = np.log(data.get('ups', 1) + 1) # Campo Externo
            J = np.log(data.get('num_comments', 1) + 1) # Interação
            
            pain = self.analyze_pain(title + " " + data.get('selftext', ''))
            print(f"  > Post: '{title[:30]}...' | Dor (Spin): {pain:.2f} | Campo h: {h:.1f}")
            
            results.append({'title': title, 'h': h, 'J': J, 'pain': pain})
            
        return results

def compute_susceptibility(results):
    if not results: return 0.0
    pains = [r['pain'] for r in results]
    return len(results) * np.var(pains) / 1.0 # T=1

if __name__ == "__main__":
    MODEL_PATH = r"c:\Users\Douglas\Desktop\ising_socials\model-bitnet-b1.58-2b-4t"
    target = "https://www.reddit.com/r/Entrepreneur"
    
    bot = RedditPhysicsIntelligence(MODEL_PATH, target)
    data = bot.scan_market()
    
    if data:
        chi = compute_susceptibility(data)
        print(f"\n[RELATÓRIO] Susceptibilidade de Mercado: {chi:.4f}")
        
        # Plot
        h = [d['h'] for d in data]
        s = [d['pain'] for d in data]
        
        plt.figure(figsize=(10,6))
        plt.scatter(h, s, c=s, cmap='magma', s=120, edgecolors='white')
        plt.colorbar(label='Intensidade de Dor')
        plt.xlabel('Visibilidade (h)')
        plt.ylabel('Dor do Cliente (S)')
        plt.title(f'Mapa de Calor Termodinâmico (Chi={chi:.2f})')
        plt.grid(True, alpha=0.2)
        
        os.makedirs('assets', exist_ok=True)
        plt.savefig('assets/reddit_opportunity_map.png')
        print("Mapa salvo em assets/reddit_opportunity_map.png")
