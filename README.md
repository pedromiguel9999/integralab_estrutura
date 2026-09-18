# ConectaShop — Laboratório de Interoperabilidade REST e gRPC

## 1. Sobre o projeto

Este projeto foi desenvolvido para a atividade de **Sistemas Distribuídos — Laboratório de Interoperabilidade REST e gRPC**.

O objetivo é implementar dois clientes capazes de consumir serviços de servidores externos:

- **Cliente REST**
- **Cliente gRPC**

Os clientes foram desenvolvidos para funcionar com servidores configuráveis, sem depender de endereços fixos no código.

O projeto realiza automaticamente os testes definidos no contrato da atividade e registra os resultados no arquivo:


logs/integration.log
2. Tecnologias utilizadas
Python 3
REST / HTTP
JSON
Requests
gRPC
Protocol Buffers
grpcio
grpcio-tools
Flask
PowerShell / Windows
Dependências Python

As principais bibliotecas utilizadas são:

requests
grpcio
grpcio-tools
flask

Elas também estão listadas no arquivo:

requirements.txt
3. Estrutura do projeto
integralab/
│
├── rest_client/
│   └── client_rest.py
│
├── grpc_client/
│   ├── client_grpc.py
│   ├── shipping.proto
│   └── generated/
│       ├── shipping_pb2.py
│       └── shipping_pb2_grpc.py
│
├── test_server/
│   └── server.py
│
├── test_server_grpc/
│   └── server.py
│
├── logs/
│   └── integration.log
│
├── requirements.txt
│
└── README.md
4. Pré-requisitos

Antes de executar o projeto, é necessário possuir:

Python instalado;
PowerShell;
acesso aos servidores REST e gRPC;
dependências instaladas.

Para verificar a versão do Python:

python --version
5. Ambiente virtual

O projeto utiliza um ambiente virtual Python.

No Windows, a ativação pode ser feita com:

..\.venv\Scripts\Activate.ps1

Após a ativação, o terminal deverá apresentar o ambiente virtual ativo.

6. Instalação das dependências

Com o ambiente virtual ativado, execute:

python -m pip install -r requirements.txt

Caso seja necessário instalar manualmente:

python -m pip install requests grpcio grpcio-tools flask
7. Configuração do cliente REST

O endereço do servidor REST é definido através da variável de ambiente:

REST_BASE_URL

O cliente também utiliza:

CLIENT_TEAM

para identificar a equipe cliente.

Exemplo:

$env:REST_BASE_URL="http://127.0.0.1:8080"
$env:CLIENT_TEAM="CLIENTE"

O endereço do servidor não deve ser fixado no código, permitindo executar o cliente contra diferentes servidores.

8. Execução do cliente REST

Primeiro, configure as variáveis:

$env:REST_BASE_URL="http://127.0.0.1:8080"
$env:CLIENT_TEAM="CLIENTE"

Depois execute:

python .\rest_client\client_rest.py

O cliente executará automaticamente os testes:

R1
R2
R3
R4
R5

Ao final, será apresentado um resumo semelhante a:

R1: PASS
R2: PASS
R3: PASS
R4: PASS
R5: PASS
9. Testes REST
R1 — Buscar produto

Requisição:

GET /api/v1/products/KB-100

Resultado esperado:

HTTP 200
unitPriceCents = 25990

Resultado obtido:

PASS
R2 — Produto inexistente

Requisição:

GET /api/v1/products/XX-999

Resultado esperado:

HTTP 404
code = PRODUCT_NOT_FOUND

Resultado obtido:

PASS
R3 — Cotação KB-100 + MS-200

Itens:

2x KB-100
1x MS-200

Valores esperados:

subtotalCents = 64970
discountCents = 3248
totalCents = 61722

Resultado obtido:

PASS
R4 — Cotação MN-400

Item:

1x MN-400

Valores esperados:

subtotalCents = 119990
discountCents = 11999
totalCents = 107991

Resultado obtido:

PASS
R5 — SKU inválido

Requisição utilizando produto inexistente:

XX-999

Resultado esperado:

HTTP 422
code = INVALID_PRODUCT

Resultado obtido:

PASS
10. Headers REST

Todas as requisições REST utilizam os headers obrigatórios:

X-Client-Team: CLIENTE
X-Request-ID: <UUID>

O X-Request-ID é gerado automaticamente para cada requisição.

Exemplo:

X-Request-ID: 84561eaf-e677-437d-8a26-8133f7ff7ea6

O ID também é utilizado para correlação entre cliente e servidor.

11. Configuração do cliente gRPC

O endereço do servidor gRPC é configurado através da variável:

GRPC_TARGET

A equipe cliente é configurada através de:

CLIENT_TEAM

Exemplo:

$env:GRPC_TARGET="localhost:50051"
$env:CLIENT_TEAM="CLIENTE"

O cliente não depende de um endereço de servidor fixado permanentemente no código.

12. Geração dos arquivos gRPC

O contrato utilizado pelo cliente está em:

grpc_client/shipping.proto

Os arquivos Python são gerados através de:

python -m grpc_tools.protoc -I grpc_client --python_out=grpc_client/generated --grpc_python_out=grpc_client/generated grpc_client/shipping.proto

Os arquivos gerados são:

grpc_client/generated/shipping_pb2.py
grpc_client/generated/shipping_pb2_grpc.py
13. Execução do cliente gRPC

Configure o servidor:

$env:GRPC_TARGET="localhost:50051"
$env:CLIENT_TEAM="CLIENTE"

Depois execute:

python .\grpc_client\client_grpc.py

O cliente executará automaticamente:

G1
G2
G3
G4
G5

Ao final, será apresentado o resultado dos testes.

14. Testes gRPC
G1 — Health

O cliente realiza uma chamada:

Health

Resultado esperado:

status = SERVING

Resultado obtido:

PASS
G2 — Envio LOCAL STANDARD

Parâmetros:

weight_grams = 1500
zone = LOCAL
mode = STANDARD

Resultado esperado:

price_cents = 1800
estimated_days = 2

Resultado obtido:

PASS
G3 — Envio REGIONAL EXPRESS

Parâmetros:

weight_grams = 2500
zone = REGIONAL
mode = EXPRESS

Resultado esperado:

price_cents = 4600
estimated_days = 2

Resultado obtido:

PASS
G4 — Envio NATIONAL STANDARD

Parâmetros:

weight_grams = 1000
zone = NATIONAL
mode = STANDARD

Resultado esperado:

price_cents = 3400
estimated_days = 7

Resultado obtido:

PASS
G5 — Peso inválido

Parâmetro:

weight_grams = 0

Resultado esperado:

INVALID_ARGUMENT
INVALID_WEIGHT

Resultado obtido:

PASS
15. Metadata gRPC

As chamadas gRPC utilizam a metadata obrigatória:

x-client-team

Também é enviado um request_id exclusivo para cada requisição.

Exemplo:

x-client-team: CLIENTE
request_id: 22f0eaae-36c1-4fe6-a0d7-d2f9095a63de

O request_id permite correlacionar as requisições realizadas pelo cliente com os registros do servidor.

16. Logs de integração

Os resultados das execuções são registrados em:

logs/integration.log

Cada registro contém informações como:

timestamp
protocol
operation
method
target
request_id
status
response
duration_ms
result

Exemplo:

2026-09-17 22:18:19 | protocol=REST | operation=R3 - Cotação KB-100 + MS-200 | method=POST | target=http://127.0.0.1:8080/api/v1/quotes | request_id=88e0b178-6c75-4848-a0aa-57fca0af7d04 | status=200 | response={'discountCents': 3248, 'discountPercent': 5, 'requestId': '88e0b178-6c75-4848-a0aa-57fca0af7d04', 'subtotalCents': 64970, 'totalCents': 61722} | duration_ms=4.62 | result=PASS

O arquivo deve ser preservado como evidência das execuções dos testes.

17. Resultado geral dos testes

Após a execução dos clientes:

REST
R1: PASS
R2: PASS
R3: PASS
R4: PASS
R5: PASS

Resultado:

5/5 PASS
gRPC
G1: PASS
G2: PASS
G3: PASS
G4: PASS
G5: PASS

Resultado:

5/5 PASS
Resultado final
REST: 5/5 PASS
gRPC: 5/5 PASS

TOTAL: 10/10 PASS
18. Execução contra servidores diferentes

Uma das características do projeto é permitir que os clientes sejam executados contra servidores diferentes sem alterar o código-fonte.

REST

Basta alterar:

$env:REST_BASE_URL="http://ENDERECO_DO_SERVIDOR:PORTA"

e executar:

python .\rest_client\client_rest.py
gRPC

Basta alterar:

$env:GRPC_TARGET="ENDERECO_DO_SERVIDOR:PORTA"

e executar:

python .\grpc_client\client_grpc.py

Dessa forma, os mesmos clientes podem ser utilizados para validar diferentes implementações do servidor.

19. Servidores de teste locais

Durante o desenvolvimento foram utilizados servidores locais para validar os clientes.

Servidor REST

O servidor de teste utiliza:

127.0.0.1:8080

Para executá-lo:

python .\test_server\server.py
Servidor gRPC

O servidor de teste utiliza:

localhost:50051

Para executá-lo:

python .\test_server_grpc\server.py

Esses servidores foram utilizados apenas para testes e validação durante o desenvolvimento.

20. Ordem recomendada de execução
REST
Terminal 1 — servidor
cd "$HOME\Desktop\integralab_estrutura\integralab"
..\.venv\Scripts\Activate.ps1
python .\test_server\server.py
Terminal 2 — cliente
cd "$HOME\Desktop\integralab_estrutura\integralab"
..\.venv\Scripts\Activate.ps1

$env:REST_BASE_URL="http://127.0.0.1:8080"
$env:CLIENT_TEAM="CLIENTE"

python .\rest_client\client_rest.py
gRPC
Terminal 1 — servidor
cd "$HOME\Desktop\integralab_estrutura\integralab"
..\.venv\Scripts\Activate.ps1
python .\test_server_grpc\server.py
Terminal 2 — cliente
cd "$HOME\Desktop\integralab_estrutura\integralab"
..\.venv\Scripts\Activate.ps1

$env:GRPC_TARGET="localhost:50051"
$env:CLIENT_TEAM="CLIENTE"

python .\grpc_client\client_grpc.py
21. Tratamento de falhas

Quando uma requisição não corresponde ao resultado esperado, o teste é marcado como:

FAIL

O cliente registra informações da requisição, incluindo:

operação;
protocolo;
destino;
request ID;
status;
resposta;
duração;
resultado.

Isso facilita a identificação da etapa em que ocorreu uma falha e permite realizar a correlação com os logs do servidor.

22. Reprodutibilidade

Para reproduzir os testes:

Clonar ou copiar o projeto.
Criar/ativar o ambiente virtual Python.
Instalar as dependências.
Configurar REST_BASE_URL para os testes REST.
Configurar GRPC_TARGET para os testes gRPC.
Configurar CLIENT_TEAM.
Executar os clientes.
Conferir os resultados no terminal.
Conferir os registros em:
logs/integration.log
23. Checklist de entrega
 Cliente REST implementado
 Cliente gRPC implementado
 Testes R1–R5 implementados
 Testes G1–G5 implementados
 Configuração do servidor REST por variável de ambiente
 Configuração do servidor gRPC por variável de ambiente
 X-Client-Team
 X-Request-ID
 Metadata x-client-team
 Request IDs únicos
 Resultados PASS/FAIL
 Medição de duração das requisições
 Registro em integration.log
 Validação das respostas REST
 Validação das respostas gRPC
 5/5 testes REST aprovados
 5/5 testes gRPC aprovados
 10/10 testes aprovados
24. Conclusão

Os clientes REST e gRPC foram implementados de acordo com os testes definidos para o laboratório.

Durante a validação local foram obtidos:

REST: 5/5 PASS
gRPC: 5/5 PASS
TOTAL: 10/10 PASS

Os clientes possuem configuração externa dos destinos dos servidores, geração de identificadores únicos para as requisições e registro das execuções para facilitar a análise e correlação dos testes.

O projeto está preparado para a próxima etapa de integração com os servidores fornecidos para a atividade.
