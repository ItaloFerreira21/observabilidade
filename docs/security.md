# Seguranca

## Principios

- Nenhum secret deve ser versionado.
- Dados sensiveis nao devem aparecer em logs, metricas ou traces.
- Configuracao muda por ambiente, nao por alteracao de codigo.
- Producao deve usar HTTPS no proxy reverso ou gateway.
- Menor privilegio deve ser o padrao para containers, redes e credenciais.

## Protecoes ja implementadas

- Headers de seguranca em todas as respostas.
- `TrustedHostMiddleware` para reduzir ataques por Host header.
- CORS configuravel e sem wildcard permitido em producao.
- Request ID e correlation ID validados antes de serem aceitos.
- Logs estruturados com mascaramento de tokens, senhas, cookies, CPF e e-mails.
- Container da API executando com usuario nao-root.
- `read_only`, `tmpfs`, `cap_drop` e `no-new-privileges` no Compose da API.

## Producao

Antes de expor em producao:

- Alterar `GRAFANA_ADMIN_PASSWORD`.
- Definir `ENVIRONMENT=production`.
- Definir `CORS_ALLOWED_ORIGINS` com dominios reais.
- Definir `TRUSTED_HOSTS` com hosts reais.
- Manter `/metrics` acessivel apenas ao Prometheus.
- Usar TLS/HTTPS no proxy.
- Ativar rate limiting no proxy ou gateway.
- Enviar logs para uma solucao centralizada com politica de retencao.

## Dados que nao devem ser logados

- Senhas.
- Tokens e API keys.
- Cookies.
- Headers de autenticacao.
- CPF.
- E-mail completo.
- Payloads confidenciais.

