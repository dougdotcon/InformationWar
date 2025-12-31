# The Gold Rush List: Relatório de Oportunidades por Setor

**Data da Análise:** 30/12/2025
**Algoritmo:** FT-PHY-001 (Portfolio Scanner)
**Setores Monitorados:** 13

---

## 1. O Vencedor da Rodada: r/Entrepreneur

Com um **Opportunity Score de 2.20**, este setor apresenta a combinação termodinâmica ideal para lucro rápido:
*   **Alta Susceptibilidade ($\chi \approx 0.70$)**: O mercado está "quente", com opiniões polarizadas e muita interação. Não é um lago estagnado.
*   **Dor Latente ($S \approx 0.31$)**: Apesar do ruído, a densidade de palavras-chave de dor (frustração, necessidade, problemas) é a mais alta do portfólio.

**Conclusão Tática**: Lançar produtos B2B ou infoprodutos aqui tem a maior probabilidade de conversão viral (Phase Transition) devido à instabilidade do sistema.

## 2. O Ranking Completo (Top 5)

| Rank | Setor (Subreddit) | Score (Ouro) | Chi (Volatilidade) | Dor Média (Demanda) |
| :--- | :--- | :--- | :--- | :--- |
| **#1** | **Entrepreneur** | **2.20** | **0.70** | **0.31** |
| #2 | Startups | 1.70 | 0.62 | 0.27 |
| #3 | Productivity | 1.41 | 0.49 | 0.28 |
| #4 | SideProject | 1.02 | 0.41 | 0.24 |
| #5 | Python | 0.79 | 0.30 | 0.26 |

*Nota: `Python` aparecer no ranking sugere dores técnicas não resolvidas (ferramentas de dev, libs, debugging).*

## 3. Matriz de Decisão Estratégica

O gráfico abaixo (`assets/portfolio_matrix.png`) plota todos os setores monitorados.

*   **Quadrante Superior Direito (GOLD MINE)**: Onde você deve focar. Alta Volatilidade + Alta Dor.
*   **Quadrante Inferior Esquerdo (CEMITÉRIO)**: Setores estagnados. Baixa interação e baixa dor (ex: nichos saturados ou "vitrines" sem discussão real).

![Portfolio Matrix](../assets/portfolio_matrix.png)

## 4. Próximos Passos Sugeridos

1.  **Ataque Cirúrgico no #1**: Usar o script `social_ising.py` focado apenas no grafo de usuários do r/Entrepreneur para identificar os 30 Hubs que controlam esse consenso.
2.  **Monitoramento 24h**: Deixar o script `reddit_market_scanner.py` rodando em loop (cronjob) para alertar via Telegram quando o Chi de um setor disparar (indício de nova tendência emergente).
