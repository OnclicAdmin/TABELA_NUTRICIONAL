# Gerador de Tabela Nutricional - RDC 429 ANVISA

Sistema inteligente para geração automática de tabelas nutricionais conforme legislação ANVISA RDC 429.

## 🎯 Funcionalidades

- ✅ Interface intuitiva e prática
- ✅ Busca fuzzy de ingredientes na tabela TACO
- ✅ Cálculo automático de composição nutricional
- ✅ Normalização de unidades (g, ml, colher, xícara, etc)
- ✅ Formatação conforme RDC 429 ANVISA
- ✅ Cálculo de %VD (Valor Diário de Referência)
- ✅ Exportação para PDF e impressão

## 🚀 Quick Start

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar aplicação
```bash
python app.py
```

### 3. Acessar
Abra o navegador em: `http://localhost:5000`

## 📋 Como Usar

1. Digite o **nome do produto** (ex: "Bolo de Laranja")
2. Escolha o **tipo de porção** (100g ou 100ml)
3. Informe **quantos ingredientes** terá a receita
4. Preencha **nome, quantidade e unidade** de cada ingrediente
5. Clique em **"Calcular Tabela Nutricional"**
6. Visualize, imprima ou exporte em PDF

## 📊 Dados TACO

A tabela TACO deve estar em: `taco/taco.csv`

Esperado: CSV com colunas contendo informações de alimentos e seus nutrientes.

## 🏗️ Arquitetura

```
app.py (Flask principal)
├── src/
│   ├── loader.py      (Carregamento TACO)
│   ├── normalizer.py  (Normalização de unidades)
│   ├── matcher.py     (Busca fuzzy)
│   ├── calculator.py  (Cálculo de nutrientes)
│   └── rd429.py       (Formatação RDC 429)
├── templates/
│   └── index.html     (Interface web)
├── static/
│   ├── css/style.css
│   └── js/app.js
└── taco/
    └── taco.csv       (Base TACO)
```

## 📝 RDC 429 - Conformidade

- ✅ Nutrientes obrigatórios listados
- ✅ Cálculo de %VD baseado em valores de referência
- ✅ Arredondamentos conforme norma
- ✅ Formatação de apresentação

## ⚠️ Limitações

- Valores estimados com base em tabelas (não substitui análise laboratorial)
- Densidade de ingredientes é aproximada para conversão volumétrica
- Algumas correspondências podem ser ajustadas manualmente

## 📧 Contato & Suporte

Sistema criado com Python + Flask + Bootstrap

---

**Nota:** Para fins comerciais/regulatórios, recomenda-se validação com análise laboratorial.