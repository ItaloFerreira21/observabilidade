# Arquitetura

## Objetivo

Criar uma base de observabilidade corporativa com uma API Python segura, simples de integrar e pronta para evoluir para uma stack completa de metricas, logs e traces.

## Fluxo inicial

```txt
cliente ou servico
  -> gateway observavel / proxy reverso
  -> FastAPI
  -> middlewares de contexto, seguranca, metricas e logs
  -> /metrics
  -> Prometheus
  -> Grafana
```

## Componentes

- `app/main.py`: cria a aplicacao e registra middlewares, rotas e handlers.
- `app/core/config.py`: configuracao tipada via variaveis de ambiente.
- `app/core/logging.py`: logs JSON com contexto do servico e mascaramento de dados sensiveis.
- `app/core/metrics.py`: metricas Prometheus da API.
- `app/core/telemetry.py`: preparacao para OpenTelemetry.
- `app/middlewares`: request ID, headers de seguranca, metricas e access log.
- `docker/prometheus`: scrape da API.
- `docker/traefik`: gateway observavel para rotear trafego externo e expor metricas.
- `docker/grafana`: datasource e dashboard provisionados.

## Decisoes tecnicas

- O projeto comeca sem PostgreSQL e Redis porque ainda nao existe regra de negocio que exija persistencia ou filas.
- O endpoint `/metrics` fica habilitado por padrao no ambiente local e deve ser exposto apenas para Prometheus em ambientes reais.
- A documentacao interativa do FastAPI e desativada automaticamente em `ENVIRONMENT=production`.
- Logs nao registram payloads, query string, cookies nem headers de autenticacao.
- O gateway mede a visao externa da aplicacao monitorada sem exigir alteracao pesada no codigo dela.

## Evolucao prevista

- Adicionar autenticacao e RBAC quando existirem usuarios ou recursos protegidos.
- Adicionar Loki ou outra solucao de logs quando houver ambiente de execucao centralizado.
- Adicionar collector OpenTelemetry e backend de traces, como Tempo ou Jaeger.
- Adicionar alertas Prometheus/Grafana para erro 5xx, latencia, saturacao e indisponibilidade.
