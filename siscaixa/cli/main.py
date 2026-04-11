"""CLI layer - Interface com usuário usando Typer."""

import os
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

import typer
from sqlalchemy.exc import SQLAlchemyError

from siscaixa.domain.models import Transaction, TransactionType
from siscaixa.repository.database import TransactionRepository, create_engine_from_url

app = typer.Typer(
    name="siscaixa",
    help="SisCaixa - Gestão de fluxo de caixa para MEIs",
    add_completion=False,
)


def get_repository() -> TransactionRepository:
    """
    Cria e retorna o repositório de transações.

    Usa o banco de dados do ambiente ou padrão.
    """
    db_path = Path(
        os.environ.get(
            "SISCAIXA_DB",
            str(Path.home() / ".siscaixa" / "siscaixa.db"),
        )
    ).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine_from_url(database_url)
    return TransactionRepository(engine)


def _parse_money(raw_value: str) -> Decimal:
    try:
        value = Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValueError("Erro: Valor inválido") from exc

    if value < 0:
        raise ValueError("Erro: Valor não pode ser negativo")
    if value.as_tuple().exponent < -2:
        raise ValueError("Erro: Valor deve ter no máximo 2 casas decimais")

    return value


def _parse_add_args(raw_args: list[str]) -> tuple[str, str, str, str | None]:
    tokens = list(raw_args)
    if tokens and tokens[0] == "add":
        tokens = tokens[1:]

    transaction_type: str | None = None
    raw_value: str | None = None
    description_parts: list[str] = []
    transaction_date: str | None = None

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {"-d", "--date"}:
            index += 1
            if index >= len(tokens):
                raise ValueError("Erro: Data inválida. Use o formato YYYY-MM-DD")
            transaction_date = tokens[index]
        elif transaction_type is None:
            transaction_type = token
        elif raw_value is None:
            raw_value = token
        else:
            description_parts.append(token)
        index += 1

    if transaction_type is None:
        raise ValueError("Erro: Tipo deve ser 'receita' ou 'despesa'")
    if raw_value is None:
        raise ValueError("Erro: Valor da transação é obrigatório")
    if not description_parts:
        raise ValueError("Erro: Descrição da transação é obrigatória")

    return transaction_type, raw_value, " ".join(description_parts), transaction_date


def format_currency(cents: int) -> str:
    """
    Formata centavos como moeda brasileira.

    Args:
        cents: Valor em centavos.

    Returns:
        String formatada (ex: "R$ 50,00").
    """
    reais = Decimal(cents) / Decimal("100")
    signal = "-" if cents < 0 else ""
    formatted = f"{abs(reais):,.2f}".replace(",", "X").replace(".", ",")
    return f"{signal}R$ {formatted.replace('X', '.')}"


@app.command(
    "add",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
def add_transaction(ctx: typer.Context) -> None:
    """
    Registra uma nova transação no fluxo de caixa.

    Exemplos:
        siscaixa add receita 50.00 "Venda de produto"
        siscaixa add despesa 15.50 "Café do escritório" -d 2024-01-15
    """
    try:
        type_raw, value_raw, description, transaction_date = _parse_add_args(ctx.args)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None

    if type_raw not in ["receita", "despesa"]:
        typer.echo("Erro: Tipo deve ser 'receita' ou 'despesa'")
        raise typer.Exit(code=1)

    try:
        parsed_value = _parse_money(value_raw)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None

    if transaction_date:
        try:
            trans_date = date.fromisoformat(transaction_date)
        except ValueError:
            typer.echo("Erro: Data inválida. Use o formato YYYY-MM-DD")
            raise typer.Exit(code=1) from None
    else:
        trans_date = date.today()

    repo = get_repository()
    transaction = Transaction.from_decimal(
        type=TransactionType(type_raw),
        amount_decimal=parsed_value,
        description=description,
        date=trans_date,
    )

    try:
        saved = repo.add(transaction)
    except SQLAlchemyError:
        typer.echo("Erro de banco de dados ao cadastrar a transação")
        raise typer.Exit(code=1) from None

    typer.echo(f"Transação cadastrada com sucesso! ID: {saved.id}")
    typer.echo(f"  Tipo: {saved.type.value}")
    typer.echo(f"  Valor: {format_currency(saved.amount_cents)}")
    typer.echo(f"  Descrição: {saved.description}")
    typer.echo(f"  Data: {saved.date.isoformat()}")


@app.command("extrato")
def list_transactions(
    period: str = typer.Option(
        "diario",
        "--period",
        "-p",
        help="Período: 'diario' ou 'mensal'",
    ),
    reference_date: str | None = typer.Option(
        None,
        "--date",
        "-d",
        help="Data de referência (YYYY-MM-DD). Padrão: hoje",
    ),
) -> None:
    """
    Exibe o extrato de transações de um período.

    Exemplos:
        siscaixa extrato
        siscaixa extrato -p mensal -d 2024-01-15
    """
    if period not in ["diario", "mensal"]:
        typer.echo("Erro: Período deve ser 'diario' ou 'mensal'")
        raise typer.Exit(code=1)

    if reference_date:
        try:
            ref_date = date.fromisoformat(reference_date)
        except ValueError:
            typer.echo("Erro: Data inválida. Use o formato YYYY-MM-DD")
            raise typer.Exit(code=1) from None
    else:
        ref_date = date.today()

    if period == "diario":
        start_date = ref_date
        end_date = ref_date
    else:
        start_date = ref_date.replace(day=1)
        if ref_date.month == 12:
            next_year = ref_date.replace(year=ref_date.year + 1, month=1, day=1)
            end_date = next_year - timedelta(days=1)
        else:
            next_month = ref_date.replace(month=ref_date.month + 1, day=1)
            end_date = next_month - timedelta(days=1)

    repo = get_repository()
    try:
        transactions = repo.list_by_period(start_date, end_date)
        balance = repo.calculate_balance(start_date, end_date)
    except SQLAlchemyError:
        typer.echo("Erro de banco de dados ao consultar o extrato")
        raise typer.Exit(code=1) from None

    typer.echo(f"\n{'=' * 50}")
    typer.echo(f"Extrato {'Diário' if period == 'diario' else 'Mensal'}")
    typer.echo(f"Período: {start_date.isoformat()} a {end_date.isoformat()}")
    typer.echo(f"{'=' * 50}\n")

    if not transactions:
        typer.echo("Nenhuma transação encontrada no período.")
    else:
        for t in sorted(transactions, key=lambda x: x.date):
            signal = "+" if t.type == TransactionType.RECEITA else "-"
            is_receita = t.type == TransactionType.RECEITA
            amount = t.amount_cents if is_receita else -t.amount_cents
            typer.echo(
                f"[{t.date.isoformat()}] [{t.id}] {signal} "
                f"{t.description}: {format_currency(amount)}"
            )

    typer.echo(f"\n{'=' * 50}")
    typer.echo(f"Saldo: {format_currency(balance)}")
    typer.echo(f"{'=' * 50}\n")


@app.command("update")
def update_transaction(
    transaction_id: int = typer.Argument(..., help="ID da transação a atualizar"),
    value: str | None = typer.Option(
        None,
        "--value",
        "-v",
        help="Novo valor em reais",
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help="Nova descrição",
    ),
) -> None:
    """
    Atualiza uma transação existente.

    Exemplos:
        siscaixa update 5 -v 60.00
        siscaixa update 5 -d "Nova descrição"
        siscaixa update 5 -v 60.00 -d "Nova descrição"
    """
    repo = get_repository()
    existing = repo.get_by_id(transaction_id)

    if existing is None:
        typer.echo(f"Erro: Transação com ID {transaction_id} não encontrada")
        raise typer.Exit(code=1)

    update_kwargs = {}
    if value is not None:
        try:
            parsed_value = _parse_money(value)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        update_kwargs["amount_cents"] = int(parsed_value * 100)
    if description is not None:
        if not description.strip():
            typer.echo("Erro: Descrição não pode ser vazia")
            raise typer.Exit(code=1)
        update_kwargs["description"] = description

    try:
        updated = repo.update(transaction_id, **update_kwargs)
    except SQLAlchemyError:
        typer.echo("Erro de banco de dados ao atualizar a transação")
        raise typer.Exit(code=1) from None

    typer.echo(f"Transação {transaction_id} atualizada com sucesso!")
    typer.echo(f"  Tipo: {updated.type.value}")
    typer.echo(f"  Valor: {format_currency(updated.amount_cents)}")
    typer.echo(f"  Descrição: {updated.description}")
    typer.echo(f"  Data: {updated.date.isoformat()}")


@app.command("remove")
def remove_transaction(
    transaction_id: int = typer.Argument(..., help="ID da transação a excluir"),
) -> None:
    """
    Exclui uma transação existente.

    Exemplo:
        siscaixa remove 5
    """
    repo = get_repository()
    try:
        deleted = repo.delete(transaction_id)
    except SQLAlchemyError:
        typer.echo("Erro de banco de dados ao excluir a transação")
        raise typer.Exit(code=1) from None

    if not deleted:
        typer.echo(f"Erro: Transação com ID {transaction_id} não encontrada")
        raise typer.Exit(code=1)

    typer.echo(f"Transação {transaction_id} excluída com sucesso!")


def main() -> None:
    """Ponto de entrada da CLI."""
    app()


if __name__ == "__main__":
    main()
