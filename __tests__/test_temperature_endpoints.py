"""Test temperature endpoints from Node-RED."""
import pytest
import aiohttp
from datetime import datetime
import logfire

# Configure logfire
logfire.configure()
logger = logfire.Logfire()

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_list_temperatures():
    """Test the /list/temperatures endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:1880/list/temperatures') as response:
            assert response.status == 200
            data = await response.json()
            logger.info("List temperatures response", data=data)
            assert "measurements" in data
            assert isinstance(data["measurements"], list)

@pytest.mark.asyncio
async def test_temperature_by_date():
    """Test the /query/temperature endpoint."""
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:1880/query/temperature?date={today}') as response:
            assert response.status == 200
            data = await response.json()
            logger.info("Query temperature response", data=data)
            assert "temperature" in data
