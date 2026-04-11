"""Entidades do domínio - Modelos de negócio do SisCaixa."""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum


class TransactionType(Enum):
    """Tipos de transação financeira."""

    RECEITA = "receita"
    DESPESA = "despesa"


@dataclass
class Transaction:
    """
    Entidade de transação financeira.

    Atributos:
        id: Identificador único da transação (None para novas).
        type: Tipo da transação (receita ou despesa).
        amount_cents: Valor em centavos (inteiro positivo).
        description: Descrição da transação.
        date: Data da transação.

    Regra de Negócio Crítica:
        O valor é armazenado como Integer representando centavos.
        Ex: R$ 50,00 -> amount_cents=5000
        Esta abordagem elimina erros de precisão de ponto flutuante.
    """

    type: TransactionType
    amount_cents: int
    description: str
    date: date
    id: int | None = None

    def __post_init__(self) -> None:
        """Valida a transação após inicialização."""
        if self.amount_cents < 0:
            raise ValueError("O valor em centavos não pode ser negativo")
        if not self.description.strip():
            raise ValueError("A descrição não pode ser vazia")

    @staticmethod
    def _coerce_decimal(value: Decimal | float | int | str) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @property
    def amount_decimal(self) -> Decimal:
        """Converte centavos para representação decimal (apenas para exibição)."""
        return Decimal(self.amount_cents) / Decimal("100")

    @classmethod
    def from_decimal(
        cls,
        type: TransactionType,
        amount_decimal: Decimal | float | int | str,
        description: str,
        date: date,
        id: int | None = None,
    ) -> "Transaction":
        """
        Cria uma transação a partir de valor decimal.

        Args:
            type: Tipo da transação.
            amount_decimal: Valor em reais (ex: 50.00).
            description: Descrição da transação.
            date: Data da transação.
            id: ID opcional.

        Returns:
            Nova instância de Transaction.

        Raises:
            ValueError: Se amount_decimal for negativo.
        """
        amount_decimal = cls._coerce_decimal(amount_decimal)

        if amount_decimal < 0:
            raise ValueError("O valor da transação não pode ser negativo")
        if amount_decimal.as_tuple().exponent < -2:
            raise ValueError("O valor da transação deve ter no máximo 2 casas decimais")

        amount_cents = int(
            (amount_decimal * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )
        return cls(
            type=type,
            amount_cents=amount_cents,
            description=description,
            date=date,
            id=id,
        )
