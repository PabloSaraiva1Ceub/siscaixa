"""Testes da camada CLI e validações de entrada."""

from typer.testing import CliRunner

from siscaixa.cli.main import app, format_currency

runner = CliRunner()


class TestFormatCurrency:
    """Testes para formatação de moeda."""

    def test_format_positive(self) -> None:
        """Deve formatar valor positivo corretamente."""
        assert format_currency(5000) == "R$ 50,00"

    def test_format_with_cents(self) -> None:
        """Deve formatar valor com centavos."""
        assert format_currency(5099) == "R$ 50,99"

    def test_format_negative(self) -> None:
        """Deve formatar valor negativo com sinal."""
        assert format_currency(-5000) == "-R$ 50,00"

    def test_format_zero(self) -> None:
        """Deve formatar zero."""
        assert format_currency(0) == "R$ 0,00"

    def test_format_large_amount(self) -> None:
        """Deve formatar valores grandes com separadores."""
        assert format_currency(1000000) == "R$ 10.000,00"


class TestCLIAddValidation:
    """Testes de validação do comando add."""

    def test_add_invalid_type(self) -> None:
        """Deve rejeitar tipo inválido."""
        result = runner.invoke(
            app,
            ["add", "invalido", "50.00", "Teste"],
        )
        assert result.exit_code == 1
        assert "Erro: Tipo deve ser 'receita' ou 'despesa'" in result.output

    def test_add_negative_value(self) -> None:
        """Deve rejeitar valor negativo."""
        result = runner.invoke(
            app,
            ["add", "receita", "-50.00", "Teste"],
        )
        assert result.exit_code == 1
        assert "Erro: Valor não pode ser negativo" in result.output

    def test_add_value_with_too_many_decimals(self) -> None:
        """Deve rejeitar valores com mais de duas casas decimais."""
        result = runner.invoke(
            app,
            ["add", "receita", "15.999", "Teste"],
        )
        assert result.exit_code == 1
        assert "Erro: Valor deve ter no máximo 2 casas decimais" in result.output

    def test_add_invalid_date_format(self) -> None:
        """Deve rejeitar data em formato inválido."""
        result = runner.invoke(
            app,
            ["add", "receita", "50.00", "Teste", "-d", "15/01/2024"],
        )
        assert result.exit_code == 1
        assert "Erro: Data inválida" in result.output


class TestCLIExtratoValidation:
    """Testes de validação do comando extrato."""

    def test_extrato_invalid_period(self) -> None:
        """Deve rejeitar período inválido."""
        result = runner.invoke(app, ["extrato", "-p", "invalido"])
        assert result.exit_code == 1
        assert "Erro: Período deve ser 'diario' ou 'mensal'" in result.output

    def test_extrato_invalid_date_format(self) -> None:
        """Deve rejeitar data em formato inválido."""
        result = runner.invoke(app, ["extrato", "-d", "15/01/2024"])
        assert result.exit_code == 1
        assert "Erro: Data inválida" in result.output


class TestCLIMissingTransaction:
    """Testes de retorno semântico para IDs inexistentes."""

    def test_update_nonexistent_transaction(self, tmp_path) -> None:
        result = runner.invoke(
            app,
            ["update", "9999", "-d", "Nova descrição"],
            env={"SISCAIXA_DB": str(tmp_path / "cli.db")},
        )

        assert result.exit_code == 1
        assert "não encontrada" in result.output

    def test_remove_nonexistent_transaction(self, tmp_path) -> None:
        result = runner.invoke(
            app,
            ["remove", "9999"],
            env={"SISCAIXA_DB": str(tmp_path / "cli.db")},
        )

        assert result.exit_code == 1
        assert "não encontrada" in result.output
