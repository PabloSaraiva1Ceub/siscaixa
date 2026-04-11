"""Testes de integração do repositório com SQLite em memória."""

from datetime import date, timedelta
from decimal import Decimal

from siscaixa.domain.models import Transaction, TransactionType
from siscaixa.repository.database import TransactionRepository


class TestRepositoryAdd:
    """Testes para operação de adição."""

    def test_add_receita_success(self, repository: TransactionRepository) -> None:
        """Deve adicionar receita com sucesso e retornar ID."""
        transaction = Transaction.from_decimal(
            type=TransactionType.RECEITA,
            amount_decimal=100.00,
            description="Receita teste",
            date=date.today(),
        )

        saved = repository.add(transaction)

        assert saved.id is not None
        assert saved.type == TransactionType.RECEITA
        assert saved.amount_cents == 10000
        assert saved.description == "Receita teste"

    def test_add_despesa_success(self, repository: TransactionRepository) -> None:
        """Deve adicionar despesa com sucesso."""
        transaction = Transaction.from_decimal(
            type=TransactionType.DESPESA,
            amount_decimal=50.00,
            description="Despesa teste",
            date=date.today(),
        )

        saved = repository.add(transaction)

        assert saved.id is not None
        assert saved.type == TransactionType.DESPESA
        assert saved.amount_cents == 5000

    def test_add_multiple_transactions(self, repository: TransactionRepository) -> None:
        """Deve adicionar múltiplas transações com IDs únicos."""
        t1 = repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Primeira",
                date=date.today(),
            )
        )
        t2 = repository.add(
            Transaction.from_decimal(
                type=TransactionType.DESPESA,
                amount_decimal=50.00,
                description="Segunda",
                date=date.today(),
            )
        )

        assert t1.id != t2.id
        assert t1.id == 1
        assert t2.id == 2


class TestRepositoryGetById:
    """Testes para busca por ID."""

    def test_get_existing_transaction(self, repository: TransactionRepository) -> None:
        """Deve retornar transação existente pelo ID."""
        saved = repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=75.50,
                description="Para buscar",
                date=date.today(),
            )
        )

        found = repository.get_by_id(saved.id)

        assert found is not None
        assert found.id == saved.id
        assert found.amount_cents == 7550
        assert found.description == "Para buscar"

    def test_get_nonexistent_transaction(
        self, repository: TransactionRepository
    ) -> None:
        """Deve retornar None para ID inexistente."""
        result = repository.get_by_id(9999)
        assert result is None


class TestRepositoryListByPeriod:
    """Testes para listagem por período."""

    def test_list_daily_transactions(self, repository: TransactionRepository) -> None:
        """Deve listar transações de um dia específico."""
        today = date.today()

        repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Hoje 1",
                date=today,
            )
        )
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.DESPESA,
                amount_decimal=50.00,
                description="Hoje 2",
                date=today,
            )
        )
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=25.00,
                description="Ontem",
                date=today - timedelta(days=1),
            )
        )

        transactions = repository.list_by_period(today, today)

        assert len(transactions) == 2
        assert all(t.date == today for t in transactions)

    def test_list_empty_period(self, repository: TransactionRepository) -> None:
        """Deve retornar lista vazia para período sem transações."""
        transactions = repository.list_by_period(
            date.today() - timedelta(days=10),
            date.today() - timedelta(days=5),
        )
        assert len(transactions) == 0


class TestRepositoryUpdate:
    """Testes para atualização de transações."""

    def test_update_description(self, repository: TransactionRepository) -> None:
        """Deve atualizar apenas a descrição."""
        saved = repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Original",
                date=date.today(),
            )
        )

        updated = repository.update(saved.id, description="Atualizada")

        assert updated is not None
        assert updated.description == "Atualizada"
        assert updated.amount_cents == 10000

    def test_update_amount(self, repository: TransactionRepository) -> None:
        """Deve atualizar apenas o valor."""
        saved = repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Valor original",
                date=date.today(),
            )
        )

        updated = repository.update(saved.id, amount_cents=20000)

        assert updated is not None
        assert updated.amount_cents == 20000
        assert updated.description == "Valor original"

    def test_update_nonexistent_transaction(
        self, repository: TransactionRepository
    ) -> None:
        """Deve retornar None ao atualizar transação inexistente."""
        result = repository.update(9999, description="Não existe")
        assert result is None


class TestRepositoryDelete:
    """Testes para exclusão de transações."""

    def test_delete_existing_transaction(
        self, repository: TransactionRepository
    ) -> None:
        """Deve excluir transação existente e retornar True."""
        saved = repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Para deletar",
                date=date.today(),
            )
        )

        deleted = repository.delete(saved.id)

        assert deleted is True
        assert repository.get_by_id(saved.id) is None

    def test_delete_nonexistent_transaction(
        self, repository: TransactionRepository
    ) -> None:
        """Deve retornar False ao deletar ID inexistente."""
        result = repository.delete(9999)
        assert result is False


class TestRepositoryCalculateBalance:
    """Testes para cálculo de saldo."""

    def test_calculate_balance_only_receitas(
        self, repository: TransactionRepository
    ) -> None:
        """Deve calcular saldo positivo apenas com receitas."""
        today = date.today()
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Receita 1",
                date=today,
            )
        )
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=50.00,
                description="Receita 2",
                date=today,
            )
        )

        balance = repository.calculate_balance(today, today)

        assert balance == 15000

    def test_calculate_balance_only_despesas(
        self, repository: TransactionRepository
    ) -> None:
        """Deve calcular saldo negativo apenas com despesas."""
        today = date.today()
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.DESPESA,
                amount_decimal=30.00,
                description="Despesa 1",
                date=today,
            )
        )
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.DESPESA,
                amount_decimal=20.00,
                description="Despesa 2",
                date=today,
            )
        )

        balance = repository.calculate_balance(today, today)

        assert balance == -5000

    def test_calculate_balance_mixed(self, repository: TransactionRepository) -> None:
        """Deve calcular saldo com receitas e despesas."""
        today = date.today()
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.RECEITA,
                amount_decimal=100.00,
                description="Receita",
                date=today,
            )
        )
        repository.add(
            Transaction.from_decimal(
                type=TransactionType.DESPESA,
                amount_decimal=40.00,
                description="Despesa",
                date=today,
            )
        )

        balance = repository.calculate_balance(today, today)

        assert balance == 6000

    def test_calculate_balance_empty_period(
        self, repository: TransactionRepository
    ) -> None:
        """Deve retornar zero para período vazio."""
        today = date.today()
        balance = repository.calculate_balance(
            today - timedelta(days=10),
            today - timedelta(days=5),
        )
        assert balance == 0

    def test_calculate_balance_large_volume(
        self, repository: TransactionRepository
    ) -> None:
        """Deve somar milhares de centavos sem perda de precisão."""
        today = date.today()

        for _ in range(10_000):
            repository.add(
                Transaction.from_decimal(
                    type=TransactionType.RECEITA,
                    amount_decimal=Decimal("0.01"),
                    description="Microreceita",
                    date=today,
                )
            )

        assert repository.calculate_balance(today, today) == 10_000
