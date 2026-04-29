from decimal import Decimal
from uuid import uuid4

import pytest

from app.api.v1.schemas.operation import OperationType


class TestGetWallet:
    """Тесты для GET /wallets/{wallet_id} - с реальной БД"""

    @pytest.mark.asyncio
    async def test_get_wallet_success(self, async_client, test_wallet):
        """Тест успешного получения кошелька (реальная БД)"""
        response = await async_client.get(f"/api/v1/wallets/{test_wallet}")

        assert response.status_code == 200
        data = response.json()
        assert data["wallet_id"] == test_wallet
        assert Decimal(data["balance"]) == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_wallet_not_found(self, async_client):
        """Тест получения несуществующего кошелька"""
        non_existent_id = uuid4()
        response = await async_client.get(f"/api/v1/wallets/{non_existent_id}")

        assert response.status_code == 404
        assert "detail" in response.json()


class TestChangeBalance:
    """Тесты для POST /wallets/{wallet_id}/operation - с реальной БД"""

    @pytest.mark.asyncio
    async def test_deposit_success(self, async_client, test_wallet):
        """Тест успешного пополнения кошелька"""
        idempotency_key = uuid4()
        operation_data = {
            "operation_type": OperationType.DEPOSIT.value,
            "amount": "100.50",
            "idempotency_key": str(idempotency_key)
        }

        response = await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json=operation_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["wallet_id"] == test_wallet
        assert "transaction_id" in data
        assert data["operation_type"] == OperationType.DEPOSIT.value
        assert Decimal(data["amount"]) == Decimal("100.50")
        assert data["status"] == "SUCCESS"

        # Проверяем баланс
        get_response = await async_client.get(f"/api/v1/wallets/{test_wallet}")
        assert Decimal(get_response.json()["balance"]) == Decimal("100.50")

    @pytest.mark.asyncio
    async def test_withdraw_success(self, async_client, test_wallet):
        """Тест успешного снятия средств"""
        # Сначала пополняем
        deposit_key = uuid4()
        await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json={
                "operation_type": OperationType.DEPOSIT.value,
                "amount": "100.00",
                "idempotency_key": str(deposit_key)
            }
        )

        # Затем снимаем
        withdraw_key = uuid4()
        operation_data = {
            "operation_type": OperationType.WITHDRAW.value,
            "amount": "50.00",
            "idempotency_key": str(withdraw_key)
        }

        response = await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json=operation_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["wallet_id"] == test_wallet
        assert data["operation_type"] == OperationType.WITHDRAW.value
        assert Decimal(data["amount"]) == Decimal("50.00")
        assert data["status"] == "SUCCESS"

        # Проверяем баланс
        get_response = await async_client.get(f"/api/v1/wallets/{test_wallet}")
        assert Decimal(get_response.json()["balance"]) == Decimal("50.00")

    @pytest.mark.asyncio
    async def test_withdraw_insufficient_funds(self, async_client, test_wallet):
        """Тест снятия при недостаточном балансе"""
        operation_data = {
            "operation_type": OperationType.WITHDRAW.value,
            "amount": "100.00",
            "idempotency_key": str(uuid4())
        }

        response = await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json=operation_data
        )

        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_idempotency(self, async_client, test_wallet):
        """Тест идемпотентности операций"""
        idempotency_key = str(uuid4())
        operation_data = {
            "operation_type": OperationType.DEPOSIT.value,
            "amount": "100.00",
            "idempotency_key": idempotency_key
        }

        response1 = await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json=operation_data
        )
        assert response1.status_code == 200
        data1 = response1.json()
        transaction_id_1 = data1["transaction_id"]

        response2 = await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json=operation_data
        )
        assert response2.status_code == 200
        data2 = response2.json()
        transaction_id_2 = data2["transaction_id"]

        assert transaction_id_1 == transaction_id_2
        assert data1["amount"] == data2["amount"]
        assert data1["status"] == data2["status"]

        # Баланс должен увеличиться только один раз
        get_response = await async_client.get(f"/api/v1/wallets/{test_wallet}")
        assert Decimal(get_response.json()["balance"]) == Decimal("100.00")

    @pytest.mark.asyncio
    async def test_operation_response_structure(self, async_client, test_wallet):
        """Тест структуры ответа операции"""
        operation_data = {
            "operation_type": OperationType.DEPOSIT.value,
            "amount": "75.50",
            "idempotency_key": str(uuid4())
        }

        response = await async_client.post(
            f"/api/v1/wallets/{test_wallet}/operation",
            json=operation_data
        )

        assert response.status_code == 200
        data = response.json()

        assert "transaction_id" in data
        assert "wallet_id" in data
        assert "operation_type" in data
        assert "amount" in data
        assert "status" in data

        assert data["wallet_id"] == test_wallet
        assert data["operation_type"] == OperationType.DEPOSIT.value
        assert Decimal(data["amount"]) == Decimal("75.50")
        assert data["status"] == "SUCCESS"


class TestCreateWallet:
    """Тесты для POST /wallets/create-wallet"""

    @pytest.mark.asyncio
    async def test_create_wallet_success(self, async_client):
        """Тест успешного создания кошелька"""
        response = await async_client.post("/api/v1/wallets/create-wallet")

        assert response.status_code == 201
        data = response.json()
        assert "wallet_id" in data
        assert "balance" in data
        assert "created_at" in data
        assert Decimal(data["balance"]) == Decimal("0")

        wallet_id = data["wallet_id"]
        get_response = await async_client.get(f"/api/v1/wallets/{wallet_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["wallet_id"] == wallet_id
        assert Decimal(get_data["balance"]) == Decimal("0")

    @pytest.mark.asyncio
    async def test_multiple_wallets_creation(self, async_client):
        """Тест создания нескольких кошельков"""
        wallet_ids = []

        for _ in range(3):
            response = await async_client.post("/api/v1/wallets/create-wallet")
            assert response.status_code == 201
            wallet_ids.append(response.json()["wallet_id"])

        # Проверяем уникальность ID
        assert len(set(wallet_ids)) == 3


class TestIntegration:
    """Полные интеграционные тесты"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_workflow(self, async_client):
        """Полный сценарий работы с кошельком"""
        # 1. Создаем кошелек
        create_response = await async_client.post("/api/v1/wallets/create-wallet")
        wallet_id = create_response.json()["wallet_id"]

        # Проверяем начальный баланс
        get_response = await async_client.get(f"/api/v1/wallets/{wallet_id}")
        assert Decimal(get_response.json()["balance"]) == Decimal("0")

        # 2. Серия операций
        operations = [
            ("DEPOSIT", "100.00", True),
            ("DEPOSIT", "50.00", True),
            ("WITHDRAW", "30.00", True),
            ("DEPOSIT", "20.00", True),
            ("WITHDRAW", "150.00", False),  # Должно отклониться (недостаточно средств)
        ]

        for op_type, amount, should_succeed in operations:
            response = await async_client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "operation_type": op_type,
                    "amount": amount,
                    "idempotency_key": str(uuid4())
                }
            )

            if should_succeed:
                assert response.status_code == 200
                data = response.json()
                assert data["wallet_id"] == wallet_id
                assert data["status"] == "SUCCESS"
            else:
                assert response.status_code == 400
                assert "detail" in response.json()

        # 3. Проверяем итоговый баланс
        get_response = await async_client.get(f"/api/v1/wallets/{wallet_id}")
        # 100 + 50 - 30 + 20 = 140
        assert Decimal(get_response.json()["balance"]) == Decimal("140.00")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_idempotency_with_multiple_requests(self, async_client):
        """Тест идемпотентности с несколькими последовательными запросами"""
        # Создаем кошелек
        create_response = await async_client.post("/api/v1/wallets/create-wallet")
        wallet_id = create_response.json()["wallet_id"]

        # Уникальный ключ для всей серии
        idempotency_key = str(uuid4())

        # Делаем несколько одинаковых запросов
        responses = []
        for _ in range(5):
            response = await async_client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={
                    "operation_type": OperationType.DEPOSIT.value,
                    "amount": "50.00",
                    "idempotency_key": idempotency_key
                }
            )
            responses.append(response)

        # Все запросы должны быть успешными
        for response in responses:
            assert response.status_code == 200

        # ID транзакции должен быть одинаковым для всех запросов
        transaction_ids = [r.json()["transaction_id"] for r in responses]
        assert len(set(transaction_ids)) == 1

        # Баланс должен увеличиться только один раз
        get_response = await async_client.get(f"/api/v1/wallets/{wallet_id}")
        assert Decimal(get_response.json()["balance"]) == Decimal("50.00")