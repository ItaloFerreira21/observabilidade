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
- Coleta de logs com mascaramento adicional no Alloy antes do envio ao Loki.
- Container da API executando com usuario nao-root.
- `read_only`, `tmpfs`, `cap_drop` e `no-new-privileges` no Compose da API.

## Producao

Antes de expor em producao:

- Alterar `GRAFANA_ADMIN_PASSWORD`.
- Definir `ENVIRONMENT=production`.
- Definir `CORS_ALLOWED_ORIGINS` com dominios reais.
- Definir `TRUSTED_HOSTS` com hosts reais.
- Manter `/metrics` acessivel apenas ao Prometheus.
- Manter Loki, Alloy e Prometheus acessiveis apenas em rede interna.
- Usar TLS/HTTPS no proxy.
- Ativar rate limiting no proxy ou gateway.
- Enviar logs para uma solucao centralizada com politica de retencao.

## Docker socket

O Alloy local usa `/var/run/docker.sock` em modo somente leitura para descobrir containers e coletar stdout/stderr. Esse socket ainda representa uma permissao sensivel no host.

Em producao:

- Prefira executar o coletor em uma rede/host dedicado ou como agente gerenciado da plataforma.
- Use allowlist de containers/labels, nao coleta irrestrita de todo o host.
- Nao exponha a UI/porta do Alloy publicamente.
- Em Kubernetes, prefira coletar logs via runtime/DaemonSet com permissoes minimas em vez de montar Docker socket diretamente.

## Dados que nao devem ser logados

- Senhas.
- Tokens e API keys.
- Cookies.
- Headers de autenticacao.
- CPF.
- E-mail completo.
- Payloads confidenciais.
