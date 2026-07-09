# Logs

## Objetivo

A camada de logs centralizados complementa as metricas. Prometheus mostra que uma rota falhou; Loki ajuda a encontrar as mensagens emitidas pela aplicacao, pelo gateway e pelos containers no mesmo intervalo.

## Componentes

- `loki`: armazena e consulta logs.
- `alloy`: coleta logs de containers Docker e arquivos locais.
- `Grafana`: consulta logs pelo datasource `Loki` e pelo dashboard `Logs e Erros`.

## Coleta automatica de containers

O Alloy descobre containers pelo Docker socket e envia os logs de stdout/stderr para o Loki com labels de baixa cardinalidade.

Por seguranca, a configuracao local coleta apenas containers do compose project `observabilidade`, evitando capturar logs de outros projetos da maquina por acidente. Em producao, ajuste esse allowlist para o nome do projeto/servico que deve ser observado.

- `environment`
- `service`
- `container`
- `compose_project`
- `source`

Em producao, esse modelo funciona bem quando a aplicacao monitorada tambem roda em container na mesma rede/host. A porta do Loki nao deve ser publicada para a internet.

Logs com timestamp mais antigo que 15 minutos sao descartados no agente para evitar importacao acidental de historico antigo quando um container ja estava rodando antes da stack de logs.

## Coleta de aplicacoes fora do Docker

Para testes locais com a API CL rodando no IntelliJ, configure o Spring Boot para escrever logs dentro da pasta `logs` deste repositorio. No terminal aberto na raiz deste projeto, copie o caminho absoluto com:

```bash
printf '%s/logs/rep-cl.log\n' "$PWD"
```

No IntelliJ, adicione aos argumentos da aplicacao:

```bash
--logging.file.name="<CAMINHO_ABSOLUTO_COPIADO>/logs/rep-cl.log"
```

Se o caminho com acento nao for aceito pela IDE, use um caminho sem espacos e monte essa pasta no servico `alloy`.

## Consultas uteis no Grafana Explore

Todos os logs do ambiente local:

```logql
{environment="local"}
```

Logs de um servico:

```logql
{environment="local", service="rep-cl"}
```

Erros e excecoes:

```logql
{environment="local"} |~ "(?i)error|exception|fatal|status=500"
```

Logs proximos de erro 500 em metricas:

1. Abra o dashboard de metricas.
2. Identifique a rota e o horario do erro.
3. Abra o dashboard `Logs e Erros`.
4. Filtre pelo mesmo intervalo de tempo.

## Seguranca

O Alloy aplica mascaramento basico para tokens Bearer, headers `Authorization`/`Cookie` e campos comuns como senha/token/JWT. Isso reduz risco, mas nao substitui higiene nos logs da aplicacao.

Nao registre:

- senhas;
- tokens;
- cookies;
- payloads completos;
- CPF;
- dados pessoais sensiveis.

## Retencao local

O Loki local usa retencao de 7 dias (`168h`) em filesystem. Para producao, ajuste a retencao de acordo com custo, volume e requisitos legais.
