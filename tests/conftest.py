"""Fixtures compartilhadas dos testes."""

import pytest

from siscaixa.repository.database import TransactionRepository, create_in_memory_engine


@pytest.fixture
def repository() -> TransactionRepository:
    """Cria um repositório isolado em SQLite em memória para cada teste."""
    engine = create_in_memory_engine()
    return TransactionRepository(engine)
