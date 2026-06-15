# Observabilidade para Spring Boot sem muita alteracao

## Arquitetura

Para observar uma API Spring Boot sem mexer muito no codigo, use o gateway como agente entre cliente e API:

```txt
cliente
  -> gateway observavel Traefik
  -> API Spring Boot existente

Prometheus
  -> coleta metricas do gateway

Grafana
  -> exibe metricas coletadas pelo Prometheus
```

## Como testar

Este e o caminho recomendado quando voce quer testar observabilidade sem alterar muito a API.

### Passo 1: confirme onde sua API Spring Boot esta rodando

Exemplo mais comum:

```txt
http://localhost:8080
```

Teste direto, sem gateway:

```bash
curl http://localhost:8080
```

Se sua API usa outro path, teste o endpoint real:

```bash
curl http://localhost:8080/api/alguma-rota
```

### Passo 2: configure o gateway para apontar para sua API

Abra [docker/traefik/dynamic.yml](../docker/traefik/dynamic.yml).

Se sua API roda em `localhost:8080`, mantenha:

```yaml
services:
  spring-api:
    loadBalancer:
      passHostHeader: true
      servers:
        - url: "http://host.docker.internal:8080"
```

Se sua API roda em outra porta, troque a URL. Exemplo:

```yaml
url: "http://host.docker.internal:9091"
```

### Passo 3: suba a stack de observabilidade

Na raiz deste projeto:

```bash
docker compose up --build
```

Ou, se os containers ja existem:

```bash
docker compose up -d gateway prometheus grafana
```

### Passo 4: pare de chamar sua API diretamente

Antes:

```txt
cliente -> http://localhost:8080
```

Agora:

```txt
cliente -> http://localhost:8088
```

Ou seja, o cliente deve chamar o gateway, e o gateway encaminha para sua API Spring Boot.

Exemplo:

```txt
http://localhost:8088/api/alguma-rota
```

O path deve ser o mesmo que existia na API. So muda host e porta.

### Passo 5: gere trafego

Faca algumas chamadas passando pelo gateway:

```bash
curl http://localhost:8088
curl http://localhost:8088/api/alguma-rota
```

Sem trafego, as metricas vao aparecer pobres ou quase zeradas.

### Passo 6: confira se o Prometheus esta coletando

Abra:

```txt
http://localhost:9090/targets
```

O job esperado e `observability-gateway`.

Ele deve aparecer como `UP`.

### Passo 7: consulte metricas no Prometheus

Abra:

```txt
http://localhost:9090
```

Exemplos de consultas:

```promql
traefik_service_requests_total
```

```promql
sum by (service, code) (rate(traefik_service_requests_total[5m]))
```

```promql
histogram_quantile(0.95, sum by (le, service) (rate(traefik_service_request_duration_seconds_bucket[5m])))
```

### Passo 8: veja no Grafana

Abra:

```txt
http://localhost:3000
```

O datasource Prometheus ja fica provisionado. Para testar, crie um painel usando uma das consultas PromQL acima.

## Se a API Spring Boot usar outra porta

Edite [docker/traefik/dynamic.yml](../docker/traefik/dynamic.yml) e troque:

```yaml
url: "http://host.docker.internal:8080"
```

por exemplo:

```yaml
url: "http://host.docker.internal:9091"
```

Depois reinicie o gateway:

```bash
docker compose restart gateway prometheus
```

## De onde vem as metricas

Neste modo sem alterar a API, as metricas vêm do gateway, nao da aplicacao Java.

O gateway consegue medir:

- quantidade de requisicoes;
- status HTTP retornado;
- latencia vista pelo cliente;
- bytes trafegados;
- falhas de roteamento;
- disponibilidade do servico roteado;
- metricas por router, service e entrypoint do Traefik.

Ele nao consegue enxergar diretamente:

- uso de heap da JVM;
- garbage collector;
- threads internas;
- pool de conexoes do banco;
- queries lentas;
- excecoes internas nao refletidas no HTTP;
- metricas de negocio, como pedidos criados ou pagamentos recusados.

Para essas metricas internas, o passo seguinte e adicionar Spring Boot Actuator com Micrometer ou usar OpenTelemetry Java Agent.

## Configuracao minima dentro da API, se aceitar pequena alteracao

Se puder fazer uma alteracao pequena, adicione Actuator + Micrometer Prometheus na API Spring Boot. Assim o Prometheus coleta tambem:

```txt
http://sua-api:8080/actuator/prometheus
```

Essa abordagem complementa o gateway:

- gateway mede a experiencia externa;
- Actuator mede a saude interna da aplicacao Java.

## Implementacao opcional dentro da API Spring Boot

Se voce quiser metricas internas da aplicacao Java, faca esta pequena alteracao.

### Maven

Adicione no `pom.xml`:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>

<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

### Gradle

Adicione no `build.gradle`:

```gradle
implementation 'org.springframework.boot:spring-boot-starter-actuator'
implementation 'io.micrometer:micrometer-registry-prometheus'
```

### application.yml

Exponha apenas health e Prometheus:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,prometheus
  metrics:
    tags:
      application: minha-api-spring
```

Depois a API deve expor:

```txt
http://localhost:8080/actuator/prometheus
```

Para o Prometheus coletar essas metricas internas, adicione tambem em [docker/prometheus/prometheus.yml](../docker/prometheus/prometheus.yml):

```yaml
- job_name: minha-api-spring-actuator
  metrics_path: /actuator/prometheus
  static_configs:
    - targets:
        - host.docker.internal:8080
```

Reinicie o Prometheus:

```bash
docker compose restart prometheus
```

## Qual caminho escolher

Use somente o gateway quando voce quer:

- testar rapido;
- nao alterar codigo Java;
- medir latencia, status HTTP e volume de chamadas;
- atuar como agente entre cliente e API.

Use gateway + Actuator quando voce tambem quer:

- JVM heap;
- garbage collector;
- threads;
- pool de conexoes;
- metricas internas do Spring;
- metricas de negocio customizadas.
