import os
import sys
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import requests
import re
from collections import Counter

# Correção Protobuf
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class PainMapper:
    """Extrai o 'DNA Linguístico' da dor de mercado."""
    
    def __init__(self, subreddit="Entrepreneur"):
        self.url = f"https://www.reddit.com/r/{subreddit}/.json"
        self.headers = {'User-agent': 'PhysicsBot DeepScan/3.1'}
        # Stopwords expandidas para limpar ruído gramatical e comum
        self.stop_words = set([
            'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'for', 'you', 'that', 'with', 'on', 'are', 'this', 'my', 'have', 'be', 'as', 'but', 'or', 'not', 'what', 'can', 'if', 'so', 'just', 'me', 'do', 'how', 'about', 'from', 'an', 'they', 'we', 'was', 'would', 'your', 'at', 'one', 'has', 'will', 'all', 'there', 'some', 'like', 'out', 'up', 'get', 'more', 'who', 'when', 'don', 'time', 'make', 'people', 'know', 'want', 'need', 'business', 'entrepreneur',
            'them', 'here', 'first', 'something', 'been', 'before', 'other', 'actually', 'real', 'work', 'started', 'start', 'doing', 'into', 'much', 'even', 'most', 'very', 'back', 'only', 'going', 'where', 'because', 'through', 'which', 'after', 'then', 'also', 'over', 'still', 'while', 'those', 'these', 'could', 'should', 'their', 'than',
            'company', 'year', 'years', 'really', 'good', 'better', 'best', 'think', 'idea', 'marketing', 'product', 'service', 'client', 'sales', 'money', 'help', 'advice', 'anyone', 'does', 'did', 'had', 'got', 'its', 'now', 'too', 'well', 'way', 'look', 'see', 'use', 'find', 'give', 'take', 'come', 'go', 'made', 'new', 'own', 'many', 'lot', 'few', 'big', 'small', 'hard', 'easy', 'right', 'left', 'long', 'short', 'high', 'low', 'free', 'paid', 'day', 'week', 'month', 'things', 'thing', 'being', 'down', 'getting', 'anyone', 'else', 'never', 'ever', 'always', 'today', 'tomorrow', 'yesterday', 'please', 'thanks', 'thank', 'looking', 'trying', 'post', 'reddit', 'guys', 'everyone'
        ])

    def fetch_deep_data(self, limit=100):
        """Coleta profunda de dados."""
        print(f"[SCAN] Iniciando Deep Dive em r/Entrepreneur (Limit={limit})...")
        try:
            r = requests.get(f"{self.url}?limit={limit}", headers=self.headers, timeout=10)
            if r.status_code == 200:
                posts = r.json()['data']['children']
                print(f"[SCAN] {len(posts)} amostras de tecido social recuperadas.")
                return posts
        except Exception as e:
            print(f"[ERRO] {e}")
        return []

    def calculate_pain_score(self, text):
        """Heurística de Dor (Reuso da lógica validada)."""
        pain_keywords = ['hate', 'problem', 'stuck', 'angry', 'fail', 'slow', 'expensive', 'hard', 'impossible', 'sucks', 'pain', 'need', 'worst', 'help', 'desperate', 'struggle', 'anxiety', 'lost', 'burnout', 'broke', 'debt', 'scam', 'fraud', 'lawsuit', 'fired', 'quit']
        text_lower = text.lower()
        score = 0.1
        for word in pain_keywords:
            if word in text_lower:
                score += 0.25 # Amplifiquei o sinal
        return min(score, 1.2)

    def extract_critical_terms(self, posts):
        """Calcula a 'Energia de Ligação' de cada palavra com a Dor."""
        term_stats = {} 
        
        print(f"[PHYSICS] Calculando Correlações Semânticas...")
        
        for p in posts:
            data = p['data']
            title = data.get('title', '')
            selftext = data.get('selftext', '')
            full_text = f"{title} {selftext}"
            
            # Métricas Físicas do Post
            pain = self.calculate_pain_score(full_text)
            h = np.log(data.get('ups', 1) + 1) 
            
            # Tokenização simples
            words = re.findall(r'\b[a-zA-Z]{4,}\b', full_text.lower())
            
            seen_in_post = set()
            for w in words:
                if w in self.stop_words: continue
                if w in seen_in_post: continue 
                seen_in_post.add(w)
                
                if w not in term_stats:
                    term_stats[w] = {'freq': 0, 'weighted_pain': 0.0}
                
                term_stats[w]['freq'] += 1
                # Energia de Ligação
                term_stats[w]['weighted_pain'] += (pain * h * 10) 

        # Ranking
        results = []
        for w, stats in term_stats.items():
            if stats['freq'] < 2: continue 
            
            score = stats['weighted_pain']
            results.append({'term': w, 'score': score, 'freq': stats['freq']})
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

def visualize_pain_cloud(terms, filename='assets/pain_cloud.png'):
    """Gera o Mapa de Termos Críticos."""
    top_terms = terms[:25]
    words = [t['term'] for t in top_terms]
    scores = [t['score'] for t in top_terms]
    
    # Normalizar scores para cor
    norm_scores = np.array(scores)
    # Evitar divisão por zero
    denom = norm_scores.max() - norm_scores.min()
    if denom == 0: denom = 1
    norm_scores = (norm_scores - norm_scores.min()) / denom

    plt.figure(figsize=(14, 10)) # Aumentei o tamanho
    bars = plt.barh(words, scores, color=plt.cm.inferno(norm_scores))
    plt.gca().invert_yaxis() 
    
    plt.xlabel('Energia de Ligação (Pain x Visibility)')
    plt.title('Nuvem de Dores: O Vocabulário da Oportunidade (r/Entrepreneur)', fontsize=16)
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    
    for i, v in enumerate(scores):
        plt.text(v + 1, i, f"{v:.0f}", va='center', fontsize=9, fontweight='bold')
        
    plt.savefig(filename)
    print(f"[VISUAL] Mapa salvo em {filename}")

if __name__ == "__main__":
    mapper = PainMapper("Entrepreneur")
    posts = mapper.fetch_deep_data()
    
    if posts:
        terms = mapper.extract_critical_terms(posts)
        
        print("\n--- TOP 15 TERMOS CRÍTICOS (VOCABULÁRIO DE ATAQUE) ---")
        for i, t in enumerate(terms[:15]):
            print(f"#{i+1} [{t['term']}] -> Score: {t['score']:.1f}")
            
        visualize_pain_cloud(terms)
        
        os.makedirs('relatos', exist_ok=True)
        with open('relatos/critical_terms.json', 'w') as f:
            json.dump(terms, f, indent=2)
