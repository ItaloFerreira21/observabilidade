# Metricas

## Endpoint

`GET /metrics`

O formato e compativel com Prometheus.

## Metricas da aplicacao

- `http_requests_total`: total de requisicoes por metodo, rota e status.
- `http_request_duration_seconds`: histograma de duracao por metodo e rota.
- `http_requests_in_progress`: requisicoes em andamento por metodo.
- `service_info`: metadados estaticos do servico.

## Metricas do gateway

O job `observability-gateway` coleta metricas expostas pelo Traefik em `gateway:9100/metrics`.

Metricas uteis:

- `traefik_service_requests_total`: requisicoes por service e status.
- `traefik_service_request_duration_seconds`: latencia por service.
- `traefik_entrypoint_requests_total`: requisicoes por entrypoint.
- `traefik_router_requests_total`: requisicoes por router.

Essas metricas representam a visao do proxy. Elas nao substituem metricas internas da aplicacao, como JVM, banco ou regras de negocio.

## Cuidados

- A label `path` usa o template da rota, como `/health/live`, para evitar cardinalidade alta.
- Query strings nao sao usadas em metricas.
- O endpoint `/metrics` nao gera metricas sobre ele mesmo para evitar ruido.

## Exemplos de PromQL

Requests por segundo:

```promql
sum by (path, status_code) (rate(http_requests_total[5m]))
```

Latencia p95:

```promql
histogram_quantile(0.95, sum by (le, path) (rate(http_request_duration_seconds_bucket[5m])))
```

Taxa de erro 5xx:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
```
