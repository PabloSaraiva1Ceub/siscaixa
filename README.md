# SisCaixa

**Sistema de Gestão de Fluxo de Caixa para Microempreendedores Individuais (MEIs)**

![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Funcionalidade Nova

O projeto agora possui integração com API pública de cotação monetária em tempo real utilizando a AwesomeAPI.

### Comando disponível

```bash
siscaixa cotacao
```

### Exemplo de saída

```bash
==================================================
Cotação Monetária
==================================================
Moeda: USD/BRL
Valor atual: R$ 5.47
Atualizado em: 2026-05-15
==================================================
```

Essa funcionalidade permite ao usuário consultar a cotação atual do dólar (USD/BRL) diretamente pelo terminal da aplicação.

---

## Problema

Microempreendedores Individuais (MEIs) frequentemente enfrentam dificuldades para controlar o fluxo de caixa diário de seus negócios. Planilhas complexas, aplicativos com muitas funcionalidades desnecessárias ou a falta de ferramentas simples e eficazes tornam o controle financeiro uma tarefa difícil.

O **SisCaixa** resolve essa necessidade oferecendo uma interface de linha de comando simples, rápida e eficiente para:

- Registrar receitas e despesas diárias
- Visualizar extrato diário ou mensal
- Calcular saldo automaticamente
- Corrigir lançamentos equivocados
- Consultar cotação monetária em tempo real

---

## Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.12+ |
| CLI | Typer |
| Banco de Dados | SQLite |
| ORM | SQLAlchemy 2.0 |
| Testes | pytest |
| Linting/Format | Ruff |
| Gerenciador de Dependências | uv |
| API Pública | AwesomeAPI |

---

## Arquitetura

O projeto segue os princípios da **Clean Architecture**, com separação em camadas:

```text
siscaixa/
├── domain/          # Entidades e regras de negócio
├── repository/      # Acesso a dados
├── services/        # Integrações externas e APIs
└── cli/             # Interface CLI
```

---

## Instalação

### Pré-requisitos

- Python 3.12 ou superior
- uv instalado

### Passos

```bash
# Clone o repositório
git clone <url-do-repositorio>

# Entre na pasta
cd siscaixa

# Instale as dependências
uv sync --all-extras
```

---

## Uso

### Exibir ajuda

```bash
uv run siscaixa --help
```

---

### Adicionar transação

```bash
siscaixa add receita 50.00 "Venda de produto"

siscaixa add despesa 15.50 "Café do escritório" -d 2024-01-15
```

---

### Visualizar extrato

```bash
siscaixa extrato

siscaixa extrato -p mensal -d 2024-01-15
```

---

### Atualizar transação

```bash
siscaixa update 5 -v 60.00

siscaixa update 5 -d "Nova descrição"
```

---

### Remover transação

```bash
siscaixa remove 5
```

---

### Consultar cotação monetária

```bash
siscaixa cotacao
```

---

## Desenvolvimento

### Rodar testes

```bash
uv run pytest -v
```

---

### Linting

```bash
uv run ruff check

uv run ruff format --check
```

---

## Teste de Integração

Foi implementado um teste automatizado para validar a integração com a API pública de cotação monetária.

O teste verifica:

- retorno correto da API;
- estrutura dos dados;
- valor monetário válido;
- funcionamento da comunicação HTTP.

---

## CI/CD

O projeto utiliza GitHub Actions para:

- execução automática dos testes;
- validação de lint;
- verificação contínua da aplicação.

A pipeline é executada a cada push ou pull request.

---

## Repositório

GitHub:
https://github.com/PabloSaraiva1Ceub/siscaixa

---

## Licença

Distribuído sob a licença MIT.
