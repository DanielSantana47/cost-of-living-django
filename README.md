# Cost of Living Dashboard — Backend Django

Backend REST API do desafio técnico Tact/BCB Consultoria.  
Dataset: **Global Cost of Living (Numbeo)** — 4.874 cidades, 204 países, 55 métricas de custo de vida em USD.

---

## Tecnologias

- **Python 3.10+**
- **Django 4.2**
- **Django REST Framework**
- **django-cors-headers**
- **SQLite** (dev) — substituível por PostgreSQL em produção

---

## Instalação e execução

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd cost_of_living_project

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Aplique as migrações
python manage.py migrate

# 5. Importe o dataset
#    O CSV deve estar em api/cost-of-living.csv (já incluso)
python manage.py import_data

# 6. (Opcional) Crie superusuário para o admin
python manage.py createsuperuser

# 7. Suba o servidor
python manage.py runserver
```

A API estará disponível em `http://localhost:8000/api/`

---

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/cities/` | Lista todas as cidades (paginado) |
| GET | `/api/cities/?search=london` | Busca por cidade ou país |
| GET | `/api/cities/?country=Brazil` | Filtra por país |
| GET | `/api/cities/?ordering=-avg_net_salary` | Ordenação |
| GET | `/api/cities/<id>/` | Detalhes de uma cidade |
| GET | `/api/cities/<id>/breakdown/` | Breakdown completo por categoria |
| GET | `/api/stats/global/` | KPIs globais (total cidades, médias, extremos) |
| GET | `/api/stats/countries/` | Estatísticas agregadas por país |
| GET | `/api/stats/countries/?limit=10&order_by=-avg_salary` | Top países por salário |
| GET | `/api/rankings/?metric=avg_net_salary&limit=10&order=desc` | Ranking de cidades por métrica |
| GET | `/api/compare/?cities=London,Paris,Tokyo` | Comparação lado a lado (até 5 cidades) |
| GET | `/api/salary-rent-ratio/?limit=20&order=desc` | Índice de acessibilidade (salário/aluguel) |
| GET | `/api/countries/` | Lista de todos os países |
| GET | `/api/metrics/` | Lista de métricas disponíveis para ranking |

### Parâmetros úteis

**`/api/rankings/`**
- `metric` — qualquer chave retornada por `/api/metrics/`
- `limit` — número de resultados (padrão: 10)
- `order` — `asc` ou `desc`
- `country` — filtrar por país

**`/api/stats/countries/`**
- `limit` — número de países
- `order_by` — `avg_salary`, `-avg_salary`, `avg_meal`, `avg_rent_1br_center`, `city_count`, etc.

**`/api/salary-rent-ratio/`**
- Retorna quantos meses de aluguel (1BR centro) cabem em 1 salário médio
- Quanto maior, mais acessível a cidade

---

## Estrutura do Projeto

```
cost_of_living_project/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/
│   ├── models.py          # Modelo City com 55 campos de custo
│   ├── serializers.py     # Serializers por caso de uso
│   ├── views.py           # Views e lógica de negócio
│   ├── urls.py            # Rotas da API
│   ├── admin.py           # Admin Django
│   ├── cost-of-living.csv # Dataset original
│   └── management/
│       └── commands/
│           └── import_data.py  # Comando de importação do CSV
├── requirements.txt
├── manage.py
└── README.md
```

---

## Exemplos de resposta

### GET /api/stats/global/
```json
{
  "total_cities": 4874,
  "total_countries": 204,
  "global_avg_salary": 3207.17,
  "global_avg_rent_1br": 710.70,
  "global_avg_meal": 8.45,
  "most_expensive_city": "Hamilton, Bermuda",
  "cheapest_city": "...",
  "highest_salary_city": "..."
}
```

### GET /api/rankings/?metric=avg_net_salary&limit=5
```json
{
  "metric": "avg_net_salary",
  "metric_label": "Average Net Salary",
  "order": "desc",
  "results": [
    {"city": "Zurich", "country": "Switzerland", "value": 7000.0},
    ...
  ]
}
```

### GET /api/cities/1/breakdown/
```json
{
  "city": "Delhi",
  "country": "India",
  "categories": {
    "restaurants": { "label": "Restaurants", "items": { "Meal (Inexpensive)": 4.9, ... } },
    "rent": { "label": "Rent (monthly)", "items": { "1BR - City Center": 223.87, ... } },
    ...
  }
}
```

---

## CORS

Por padrão, `CORS_ALLOW_ALL_ORIGINS = True` — o frontend React pode rodar em qualquer porta local.  
Em produção, ajuste `CORS_ALLOWED_ORIGINS` em `config/settings.py`.

---

## Comando de importação

```bash
# Importação padrão (api/cost-of-living.csv)
python manage.py import_data

# CSV personalizado
python manage.py import_data --csv /caminho/para/arquivo.csv

# Limpar dados antes de reimportar
python manage.py import_data --clear
```
"# cost-of-living-django" 
