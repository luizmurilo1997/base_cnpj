# Consulta CNPJ

API REST em FastAPI para consultar a base pública de CNPJ da Receita Federal, com pipeline ETL para baixar e carregar os dados no PostgreSQL.

## O que este projeto faz

1. **Pipeline ETL** — baixa os arquivos mensais da Receita Federal e importa no PostgreSQL
2. **API REST** — consulta CNPJ, empresas, sócios, CNAE, UF, município e estatísticas
3. **Docker Compose** — sobe API, PostgreSQL e Redis com um comando

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- (Opcional) [uv](https://docs.astral.sh/uv/) e Python 3.12+ para desenvolvimento local

## Início rápido (Docker)

```bash
# 1. Subir infraestrutura + API
docker compose up -d postgres redis api

# 2. Carregar a base da Receita (pode levar várias horas na primeira vez)
docker compose run --rm pipeline --list
docker compose run --rm pipeline

# 3. Abrir a documentação
# Swagger: http://localhost:8000/docs
# ReDoc:   http://localhost:8000/redoc
```

Aguarde o Postgres ficar healthy antes do pipeline. Se o container estiver em recovery, espere alguns minutos e rode de novo.

## Conexão com o banco de dados

| Item | Valor |
|------|-------|
| Host (na máquina) | `localhost` |
| Porta | `5435` |
| Banco | `cnpj` |
| Usuário | `postgres` |
| Senha | `postgres` |
| URL (apps na máquina) | `postgresql+psycopg://postgres:postgres@localhost:5435/cnpj` |
| URL (containers) | `postgresql+psycopg://postgres:postgres@postgres:5432/cnpj` |

Dados persistentes no disco **E:** (`docker-compose.yml`):

| Pasta | Conteúdo |
|-------|----------|
| `E:/project_cnpj/postgres` | Dados do PostgreSQL |
| `E:/project_cnpj/redis` | Dados do Redis |
| `E:/project_cnpj/temp` | Downloads / temporários do pipeline |
| `E:/project_cnpj/parquet` | Export Parquet (se usar) |

Antes da primeira execução:
```powershell
mkdir E:\project_cnpj\postgres, E:\project_cnpj\redis, E:\project_cnpj\temp, E:\project_cnpj\parquet -Force
```

### Exemplos de conexão

**psql**
```bash
psql postgresql://postgres:postgres@localhost:5435/cnpj
```

**Docker**
```bash
docker exec -it cnpj-postgres psql -U postgres -d cnpj
```

**DBeaver / DataGrip / pgAdmin**
- Host: `localhost`
- Port: `5435`
- Database: `cnpj`
- Username: `postgres`
- Password: `postgres`

### Redis (cache opcional)

| Item | Valor |
|------|-------|
| Host | `localhost` |
| Porta | `6380` |
| URL | `redis://localhost:6380/0` |

## Variáveis de ambiente

O arquivo `.env` já vem no repositório com os valores padrão de desenvolvimento:

```env
SECRET_KEY=change-me-in-production
API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5435/cnpj
REDIS_URL=redis://localhost:6380/0
REDIS_ENABLED=true

LOADING_STRATEGY=upsert
DOWNLOAD_WORKERS=4
PROCESS_WORKERS=1
```

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | Conexão PostgreSQL (API usa dialeto `postgresql+psycopg`) |
| `REDIS_URL` | Cache de consultas `/cnpj/{cnpj}` |
| `API_PORT` | Porta HTTP da API (default `8000`) |
| `LOADING_STRATEGY` | `upsert` (seguro) ou `replace` (mais rápido, limpa tabelas) |
| `PROCESS_WORKERS` | Arquivos processados em paralelo (ex.: `4`) |
| `DOWNLOAD_WORKERS` | Downloads paralelos da Receita |

## Serviços Docker

```bash
docker compose up -d postgres redis api   # sobe tudo
docker compose ps                         # status
docker compose logs -f api                # logs da API
docker compose down                       # para (mantém volume do banco)
docker compose down -v                    # para e APAGA os dados do Postgres
```

| Serviço | Container | Porta |
|---------|-----------|-------|
| API | `cnpj-api` | `8000` |
| PostgreSQL | `cnpj-postgres` | `5435` |
| Redis | `cnpj-redis` | `6380` |
| Pipeline | sob demanda | — |

## Pipeline ETL (carregar / atualizar dados)

```bash
# Listar meses disponíveis na Receita
docker compose run --rm pipeline --list

# Processar o mês mais recente
docker compose run --rm pipeline

# Processar um mês específico
docker compose run --rm pipeline --month 2026-06

# Forçar reprocessamento de um mês
docker compose run --rm pipeline --month 2026-06 --force
```

Arquivos já processados ficam registrados em `processed_files`. Rodar de novo o mesmo mês **não baixa tudo de novo**, a menos que use `--force`.

Atualização mensal típica:
```bash
docker compose run --rm pipeline --list
docker compose run --rm pipeline --month 2026-07
```

Para carga completa mais rápida (primeira vez), no `.env`:
```env
LOADING_STRATEGY=replace
PROCESS_WORKERS=4
```

## Endpoints da API

Documentação interativa: [http://localhost:8000/docs](http://localhost:8000/docs)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/cnpj/{cnpj}` | Detalhe completo (razão social, CNAE, endereço, sócios…) |
| `GET` | `/empresas` | Busca com filtros e paginação |
| `GET` | `/socios` | Busca de sócios |
| `GET` | `/municipios/{codigo}` | Empresas por município |
| `GET` | `/estados/{uf}` | Empresas por UF (matrizes ativas) |
| `GET` | `/cnae/{codigo}` | Empresas por CNAE |
| `GET` | `/estatisticas` | Totais e distribuições |
| `GET` | `/health` | Liveness |
| `GET` | `/ready` | Readiness (Postgres + Redis) |

### Exemplos

```bash
# Consulta por CNPJ
curl http://localhost:8000/cnpj/00000000000191

# Busca por razão social (prefixo)
curl "http://localhost:8000/empresas?nome=PETROBRAS&size=10"

# Filtros
curl "http://localhost:8000/empresas?uf=SP&situacao=02&cnae=6201501&page=1&size=20"

# Sócios
curl "http://localhost:8000/socios?nome=JOAO&size=10"

# Health
curl http://localhost:8000/health
```

### Paginação

Respostas de listagem usam:

```json
{
  "items": [...],
  "page": 1,
  "size": 20,
  "has_more": true,
  "total": null,
  "pages": null
}
```

`has_more` indica se há próxima página. Não há `COUNT(*)` global (evita lentidão em dezenas de milhões de linhas).

Filtros úteis em `/empresas`: `nome`, `nome_fantasia`, `cidade`, `uf`, `cnae`, `situacao`, `natureza_juridica`, `porte`, `capital_minimo`, `capital_maximo`, `apenas_matriz`, `busca_contem`, `page`, `size`.

## Desenvolvimento local (sem rebuild da imagem)

```bash
# Infra
docker compose up -d postgres redis

# Dependências
uv sync --extra api --group dev

# API com hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testes
uv run pytest tests/api -v

# Índices extras (se o banco já existia antes dos scripts de init)
uv run alembic upgrade head
```

## Estrutura

```
app/                 # API FastAPI (Router → Service → Repository)
main.py              # Entrypoint do pipeline ETL
processor.py         # Processamento dos CSVs
downloader.py        # Download dos ZIPs da Receita
database.py          # Carga no PostgreSQL
initial.sql          # Schema inicial
alembic/             # Índices / migrações da API
docker-compose.yml   # API + Postgres + Redis + pipeline
Dockerfile.api       # Imagem da API
Dockerfile           # Imagem do pipeline
.env                 # Variáveis de ambiente
```

## Observações

- A primeira carga completa da Receita é grande (dezenas de GB) e demora várias horas
- O volume Docker `cnpj_pipeline_data` persiste o banco entre reinícios
- `docker compose down -v` apaga os dados
- Situação cadastral comum: `02` = Ativa, `08` = Baixada
- Porte: `01` Microempresa, `03` EPP, `05` Demais
