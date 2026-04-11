"""Testes unitários das entidades e regras de negócio."""

from datetime import date
from decimal import Decimal

import pytest

from siscaixa.domain.models import Transaction, TransactionType


class TestTransactionCreation:
    """Testes para criação de transações."""

    def test_create_receita_success(self) -> None:
        """Deve criar uma transação de receita com sucesso."""
        transaction = Transaction.from_decimal(
            type=TransactionType.RECEITA,
            amount_decimal=Decimal("50.00"),
            description="Venda de produto",
            date=date.today(),
        )

        assert transaction.type == TransactionType.RECEITA
        assert transaction.amount_cents == 5000
        assert transaction.description == "Venda de produto"
        assert transaction.date == date.today()
        assert transaction.id is None

    def test_create_despesa_success(self) -> None:
        """Deve criar uma transação de despesa com sucesso."""
        transaction = Transaction.from_decimal(
            type=TransactionType.DESPESA,
            amount_decimal=Decimal("15.50"),
            description="Café do escritório",
            date=date.today(),
        )

        assert transaction.type == TransactionType.DESPESA
        assert transaction.amount_cents == 1550
        assert transaction.description == "Café do escritório"

    def test_create_with_cents_precision(self) -> None:
        """Deve preservar centavos na conversão."""
        transaction = Transaction.from_decimal(
            type=TransactionType.RECEITA,
            amount_decimal=Decimal("99.99"),
            description="Teste precisão",
            date=date.today(),
        )

        assert transaction.amount_cents == 9999
        assert transaction.amount_decimal == Decimal("99.99")

    def test_create_with_id(self) -> None:
        """Deve criar transação com ID quando fornecido."""
        transaction = Transaction(
            type=TransactionType.RECEITA,
            amount_cents=10000,
            description="Com ID",
            date=date.today(),
            id=42,
        )

        assert transaction.id == 42


class TestTransactionValidation:
    """Testes de validação das transações."""

    def test_reject_negative_amount(self) -> None:
        """Deve rejeitar valor negativo na criação."""
        with pytest.raises(ValueError, match="não pode ser negativo"):
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=Decimal("-50.00"),
                description="Valor negativo",
                date=date.today(),
            )

    def test_reject_negative_amount_cents(self) -> None:
        """Deve rejeitar amount_cents negativo diretamente."""
        with pytest.raises(ValueError, match="não pode ser negativo"):
            Transaction(
                type=TransactionType.RECEITA,
                amount_cents=-100,
                description="Centavos negativos",
                date=date.today(),
            )

    def test_reject_empty_description(self) -> None:
        """Deve rejeitar descrição vazia."""
        with pytest.raises(ValueError, match="não pode ser vazia"):
            Transaction(
                type=TransactionType.RECEITA,
                amount_cents=1000,
                description="",
                date=date.today(),
            )

    def test_reject_whitespace_description(self) -> None:
        """Deve rejeitar descrição apenas com espaços."""
        with pytest.raises(ValueError, match="não pode ser vazia"):
            Transaction(
                type=TransactionType.RECEITA,
                amount_cents=1000,
                description="   ",
                date=date.today(),
            )

    def test_accept_zero_amount(self) -> None:
        """Deve aceitar valor zero."""
        transaction = Transaction.from_decimal(
            type=TransactionType.RECEITA,
            amount_decimal=Decimal("0.00"),
            description="Valor zero",
            date=date.today(),
        )

        assert transaction.amount_cents == 0

    def test_reject_more_than_two_decimals(self) -> None:
        """Deve rejeitar valores com mais de duas casas decimais."""
        with pytest.raises(ValueError, match="no máximo 2 casas decimais"):
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=Decimal("15.999"),
                description="Valor inválido",
                date=date.today(),
            )
