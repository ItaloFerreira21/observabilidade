# Operacao

## Ambiente local

```bash
cp .env.example .env
docker compose up --build
```

URLs:

- Gateway observavel: `http://localhost:8088`
- API: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Variaveis principais

- `ENVIRONMENT`: `local`, `development`, `staging` ou `production`.
- `CORS_ALLOWED_ORIGINS`: origens permitidas, separadas por virgula.
- `TRUSTED_HOSTS`: hosts aceitos pela API, separados por virgula.
- `METRICS_ENABLED`: habilita `/metrics`.
- `GATEWAY_PORT`: porta local usada pelo gateway observavel.
- `OTEL_ENABLED`: habilita instrumentacao OpenTelemetry.
- `OTEL_EXPORTER_OTLP_ENDPOINT`: endpoint do collector OTLP gRPC.

## Imagens Docker

As imagens de Prometheus e Grafana sao parametrizadas em `.env`:

- `PROMETHEUS_IMAGE`
- `GRAFANA_IMAGE`
- `TRAEFIK_IMAGE`

Isso permite atualizar a stack sem editar `docker-compose.yml`.

## Checklist antes de producao

- Rotacionar senhas e remover valores padrao.
- Publicar a API atras de proxy com HTTPS.
- Restringir Prometheus e Grafana a rede interna ou VPN.
- Configurar backup dos volumes persistentes.
- Definir retencao de metricas de acordo com custo e necessidade.
- Criar alertas para disponibilidade, latencia e erro 5xx.
