"""Class for Enedis Gateway (http://enedisgateway.tech)."""
from __future__ import annotations

import logging
import re
import datetime
from datetime import datetime as dt
from .auth import EnedisAuth

_LOGGER = logging.getLogger(__name__)


class EnedisGateway:
    """Class for Enedis Gateway API."""

    def __init__(self, pdl, token, session=None):
        """Init."""
        self.auth = EnedisAuth(token, session)
        self.pdl = str(pdl)

    async def async_close(self):
        """Close session."""
        await self.auth.async_close()

    async def async_get_contracts(self):
        """Get contracts."""
        payload = {"type": "contracts", "usage_point_id": self.pdl}
        return await self.auth.request(json=payload)

    async def async_get_identity(self):
        """Get identity."""
        payload = {"type": "identity", "usage_point_id": self.pdl}
        return await self.auth.request(json=payload)

    async def async_get_addresses(self):
        """Get addresses."""
        payload = {"type": "addresses", "usage_point_id": self.pdl}
        return await self.auth.request(json=payload)


class EnedisByPDL(EnedisGateway):
    """Get data of pdl."""
    def __init__(self, pdl, token, session=None):
        """Initialize."""
        super().__init__(pdl, token)
        self.offpeaks = None

    async def async_fetch_datas(self, service, start, end):
        """Get datas."""
        payload = {
            "type": service, "usage_point_id": self.pdl, "start": start, "end": end
        }
        return await self.auth.request(json=payload)

    async def async_get_max_power(self, start, end):
        """Get consumption max power."""
        payload = {
            "type": "daily_consumption_max_power",
            "usage_point_id": self.pdl,
            "start": start,
            "end": end,
        }
        return await self.auth.request(json=payload)

    async def async_get_contract(self):
        """Return all."""
        contract = {}
        contracts = await self.async_get_contracts()
        usage_points = contracts.get("customer", {}).get("usage_points", "")
        for usage_point in usage_points:
            if usage_point.get("usage_point", {}).get("usage_point_id") == self.pdl:
                contract = usage_point.get("contracts", {})
                if offpeak_hours := contract.get("offpeak_hours"):
                    contract["offpeaks"] = re.findall("(?:(\\w+)-(\\w+))+", offpeak_hours)
        return contract

    async def async_get_address(self):
        """Return all."""
        address = {}
        addresses = await self.async_get_addresses()
        usage_points = addresses.get("customer", {}).get("usage_points", "")
        for usage_point in usage_points:
            if usage_point.get("usage_point", {}).get("usage_point_id") == self.pdl:
                address = usage_point.get("usage_point")
        return address

    async def async_has_offpeak(self):
        """Has offpeak hours."""
        if self.offpeaks is None:
            await self.async_get_contract()
        return len(self.offpeaks) > 0

    async def async_check_offpeak(self, start: datetime):
        """Return offpeak status."""
        if await self.async_has_offpeak() is True:
            start_time = start.time()
            for range_time in self.offpeaks:
                starting = dt.strptime(range_time[0], "%HH%M").time()
                ending = dt.strptime(range_time[1], "%HH%M").time()
                if start_time > starting and start_time <= ending:
                    return True
        return False
