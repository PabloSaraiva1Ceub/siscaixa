# SisCaixa

**Sistema de Gestão de Fluxo de Caixa para Microempreendedores Individuais (MEIs)**

![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Problema

Microempreendedores Individuais (MEIs) frequentemente enfrentam dificuldades para controlar o fluxo de caixa diário de seus negócios. Planilhas complexas, aplicativos com muitas funcionalidades desnecessárias ou a falta de ferramentas simples e eficazes tornam o controle financeiro uma tarefa árdua.

O **SisCaixa** resolve essa dor oferecendo uma interface de linha de comando simples, rápida e eficiente para:

- Registrar receitas e despesas diárias
- Visualizar extrato diário ou mensal
- Calcular saldo do período automaticamente
- Corrigir lançamentos equivocados (edição e exclusão)

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

---

## Arquitetura

O projeto segue os princípios da **Clean Architecture**, com separação estrita em camadas:

```
siscaixa/
├── domain/          # Entidades e regras de negócio
├── repository/      # Acesso a dados (SQLAlchemy)
└── cli/             # Interface com usuário (Typer)
```

### Precisão Monetária (Padrão Ouro)

**Problema:** Tipos de ponto flutuante (`float`, `real`) sofrem de erros de precisão binária, o que é inaceitável para cálculos financeiros.

**Solução:** Todos os valores monetários são armazenados como **inteiros representando centavos** e as entradas monetárias são validadas com `Decimal` (máximo de 2 casas decimais).

| Valor Visual | Armazenamento |
|--------------|---------------|
| R$ 50,00 | `5000` |
| R$ 0,99 | `99` |
| R$ 1.234,56 | `123456` |

A conversão entre centavos e reais para exibição é controlada pela aplicação, garantindo que:

1. O banco de dados armazene apenas inteiros
2. Nenhuma operação financeira crítica dependa de `float`
3. O usuário sempre veja valores formatados corretamente

---

## Instalação

### Pré-requisitos

- Python 3.12 ou superior
- [uv](https://github.com/astral-sh/uv) (gerenciador de dependências)

### Passos

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd siscaixa

# Instale as dependências
uv sync --all-extras

# (Opcional) Instale como pacote local
uv pip install -e .
```

---

## Uso

### Comandos Disponíveis

```bash
uv run siscaixa --help
```

#### 1. Adicionar Transação (`add`)

Registra uma nova receita ou despesa.

```bash
# Adicionar receita de R$ 50,00
siscaixa add receita 50.00 "Venda de produto"

# Adicionar despesa de R$ 15,50 com data específica
siscaixa add despesa 15.50 "Café do escritório" -d 2024-01-15
```

**Parâmetros:**
- `tipo`: `receita` ou `despesa`
- `valor`: Valor em reais com no máximo 2 casas decimais (ex: `15.99`)
- `descricao`: Descrição da transação
- `-d, --date`: Data opcional (YYYY-MM-DD). Padrão: data atual

**Validações:**
- Valores negativos são rejeitados
- Valores com mais de 2 casas decimais são rejeitados

#### 2. Visualizar Extrato (`extrato`)

Lista transações e calcula saldo do período.

```bash
# Extrato diário (hoje)
siscaixa extrato

# Extrato mensal de Janeiro/2024
siscaixa extrato -p mensal -d 2024-01-15
```

**Opções:**
- `-p, --period`: `diario` (padrão) ou `mensal`
- `-d, --date`: Data de referência (YYYY-MM-DD)

#### 3. Atualizar Transação (`update`)

Edita descrição ou valor de uma transação existente.

```bash
# Atualizar apenas o valor
siscaixa update 5 -v 60.00

# Atualizar apenas a descrição
siscaixa update 5 -d "Nova descrição"

# Atualizar ambos
siscaixa update 5 -v 60.00 -d "Descrição corrigida"
```

**Parâmetros:**
- `id`: ID da transação
- `-v, --value`: Novo valor em reais
- `-d, --description`: Nova descrição

#### 4. Remover Transação (`remove`)

Exclui uma transação cadastrada.

```bash
siscaixa remove 5
```

**Parâmetros:**
- `id`: ID da transação a excluir

---

## Desenvolvimento

### Rodar Testes

```bash
uv run pytest -v
```

### Linting e Formatação

```bash
# Verificar erros
uv run ruff check

# Formatar código
uv run ruff format

# Verificar formatação (usado na CI)
uv run ruff format --check
```

### Estrutura de Testes

Os testes utilizam **SQLite em memória** (`sqlite:///:memory:`) para garantir:

- Isolamento total entre testes
- Nenhum arquivo `.db` criado em disco
- Execução rápida da suíte

---

## CI/CD

O workflow do GitHub Actions (`.github/workflows/ci.yml`) é executado em cada `push` ou `pull_request` para a branch `main`:

1. **Checkout** do código
2. **Setup** do Python 3.12 e uv
3. **Instalação** de dependências (`uv sync --frozen --all-extras`)
4. **Linting** com `ruff check` e `ruff format --check`
5. **Testes** com `pytest -v`

O cache de dependências do `uv` é habilitado no workflow para reduzir tempo de execução da pipeline.

A pipeline **falha** se qualquer etapa de linting ou testes não passar.

---

## Versionamento

Este projeto segue [Versionamento Semântico](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Mudanças incompatíveis
- **MINOR** (1.0.0 → 1.1.0): Novas funcionalidades compatíveis
- **PATCH** (1.0.0 → 1.0.1): Correções de bugs compatíveis

**Versão Atual:** 1.0.0

---

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

**Importante:** Certifique-se de que todos os testes passam e o linting está limpo antes de submeter.
