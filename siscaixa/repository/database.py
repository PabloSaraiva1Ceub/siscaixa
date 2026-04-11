"""Repository layer - Acesso a dados com SQLAlchemy 2.0."""

from datetime import date

from sqlalchemy import Date, Integer, String, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from siscaixa.domain.models import Transaction, TransactionType


class Base(DeclarativeBase):
    """Base declarativa do SQLAlchemy."""

    pass


class TransactionModel(Base):
    """
    Modelo ORM da tabela de transações.

    A tabela armazena valores como INTEGER (centavos) para garantir
    precisão monetária absoluta.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)


class TransactionRepository:
    """
    Repositório para operações CRUD de transações.

    Esta classe encapsula todo o acesso ao banco de dados,
    mantendo a CLI isolada das consultas SQL.
    """

    def __init__(self, engine) -> None:
        """
        Inicializa o repositório com um engine SQLAlchemy.

        Args:
            engine: Engine do SQLAlchemy configurado.
        """
        self.engine = engine
        self._create_tables()

    def _create_tables(self) -> None:
        """Cria as tabelas no banco de dados."""
        Base.metadata.create_all(self.engine)

    def add(self, transaction: Transaction) -> Transaction:
        """
        Adiciona uma nova transação ao banco de dados.

        Args:
            transaction: Entidade Transaction a ser persistida.

        Returns:
            A transação com o ID gerado.
        """
        with Session(self.engine) as session:
            model = TransactionModel(
                type=transaction.type.value,
                amount_cents=transaction.amount_cents,
                description=transaction.description,
                date=transaction.date,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return Transaction(
                id=model.id,
                type=TransactionType(model.type),
                amount_cents=model.amount_cents,
                description=model.description,
                date=model.date,
            )

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        """
        Busca uma transação pelo ID.

        Args:
            transaction_id: ID da transação.

        Returns:
            A transação encontrada ou None se não existir.
        """
        with Session(self.engine) as session:
            model = session.get(TransactionModel, transaction_id)
            if model is None:
                return None
            return Transaction(
                id=model.id,
                type=TransactionType(model.type),
                amount_cents=model.amount_cents,
                description=model.description,
                date=model.date,
            )

    def list_by_period(self, start_date: date, end_date: date) -> list[Transaction]:
        """
        Lista transações em um período.

        Args:
            start_date: Data inicial (inclusiva).
            end_date: Data final (inclusiva).

        Returns:
            Lista de transações no período.
        """
        with Session(self.engine) as session:
            stmt = select(TransactionModel).where(
                TransactionModel.date >= start_date,
                TransactionModel.date <= end_date,
            )
            models = session.scalars(stmt).all()
            return [
                Transaction(
                    id=m.id,
                    type=TransactionType(m.type),
                    amount_cents=m.amount_cents,
                    description=m.description,
                    date=m.date,
                )
                for m in models
            ]

    def update(self, transaction_id: int, **kwargs) -> Transaction | None:
        """
        Atualiza campos de uma transação.

        Args:
            transaction_id: ID da transação.
            **kwargs: Campos a atualizar (amount_cents, description).

        Returns:
            A transação atualizada ou None se não existir.
        """
        with Session(self.engine) as session:
            model = session.get(TransactionModel, transaction_id)
            if model is None:
                return None

            if "amount_cents" in kwargs:
                model.amount_cents = kwargs["amount_cents"]
            if "description" in kwargs:
                model.description = kwargs["description"]

            session.commit()
            session.refresh(model)
            return Transaction(
                id=model.id,
                type=TransactionType(model.type),
                amount_cents=model.amount_cents,
                description=model.description,
                date=model.date,
            )

    def delete(self, transaction_id: int) -> bool:
        """
        Exclui uma transação pelo ID.

        Args:
            transaction_id: ID da transação a excluir.

        Returns:
            True se excluído, False se não existia.
        """
        with Session(self.engine) as session:
            stmt = delete(TransactionModel).where(TransactionModel.id == transaction_id)
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0

    def calculate_balance(self, start_date: date, end_date: date) -> int:
        """
        Calcula o saldo no período (receitas - despesas).

        Args:
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Saldo em centavos.
        """
        with Session(self.engine) as session:
            stmt = select(
                TransactionModel.type,
                TransactionModel.amount_cents,
            ).where(
                TransactionModel.date >= start_date,
                TransactionModel.date <= end_date,
            )
            rows = session.execute(stmt).all()

            balance = 0
            for type_, amount in rows:
                if type_ == TransactionType.RECEITA.value:
                    balance += amount
                else:
                    balance -= amount
            return balance


def create_engine_from_url(database_url: str):
    """
    Cria um engine SQLAlchemy a partir de uma URL.

    Args:
        database_url: URL de conexão (ex: sqlite:///siscaixa.db).

    Returns:
        Engine configurado.
    """
    return create_engine(database_url, echo=False)


def create_in_memory_engine() -> any:
    """
    Cria um engine SQLite em memória para testes.

    Returns:
        Engine configurado em memória.
    """
    return create_engine("sqlite:///:memory:", echo=False)
