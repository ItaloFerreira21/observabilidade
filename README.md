# Observabilidade

Base profissional para um sistema de observabilidade em Python, preparada para integração com aplicações corporativas.

## Stack inicial

- FastAPI para API e middlewares.
- Prometheus para coleta de métricas.
- Grafana com datasource e dashboard provisionados.
- Loki para logs centralizados.
- Grafana Alloy para coleta de logs de containers e arquivos locais.
- Logs estruturados em JSON com mascaramento de dados sensíveis.
- OpenTelemetry preparado, desativado por padrão até existir um collector.
- Docker Compose para execução local.

## Execução local

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:create_app --factory --reload
```

Endpoints úteis:

- API: `http://localhost:8000`
- Health: `http://localhost:8000/health/live`
- Métricas: `http://localhost:8000/metrics`
- Docs locais: `http://localhost:8000/docs`

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Serviços:

- Gateway observavel: `http://localhost:8088`
- API: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Loki: `http://localhost:3100`
- Alloy: `http://localhost:12345`

Credenciais locais do Grafana ficam em `.env`. Troque `GRAFANA_ADMIN_PASSWORD` antes de qualquer ambiente compartilhado.

## Testes e qualidade

```bash
pytest
ruff check .
mypy app
```

## Documentação

- [Arquitetura](docs/architecture.md)
- [Segurança](docs/security.md)
- [Métricas](docs/metrics.md)
- [Logs](docs/logs.md)
- [Operação](docs/operations.md)
- [Spring Boot sem muita alteração](docs/spring-boot-agent.md)
