"""Repairs for Dreame Vacuum."""

from __future__ import annotations

from homeassistant import data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER
from .dreame import DeviceException
from .vacuum import CONSUMABLE_RESET_ACTION


class ConsumableResetRepairFlow(RepairsFlow):
    """Reset a consumable's counter after the user has replaced or cleaned it."""

    def __init__(self, data: dict[str, str]) -> None:
        self._entry_id = data["entry_id"]
        self._consumable = data["consumable"]
        self._placeholders = {"title": data["title"], "message": data["message"]}

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> data_entry_flow.FlowResult:
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, str] | None = None) -> data_entry_flow.FlowResult:
        if user_input is not None:
            coordinator = self.hass.data.get(DOMAIN, {}).get(self._entry_id)
            action = CONSUMABLE_RESET_ACTION.get(self._consumable)
            if coordinator is None or coordinator.device is None or action is None:
                return self.async_abort(reason="not_available")
            try:
                await self.hass.async_add_executor_job(coordinator.device.call_action, action)
            except DeviceException as ex:
                LOGGER.warning("Unable to reset consumable %s: %s", self._consumable, ex)
                return self.async_abort(reason="reset_failed")
            return self.async_create_entry(data={})

        return self.async_show_form(step_id="confirm", description_placeholders=self._placeholders)


async def async_create_fix_flow(
    hass: HomeAssistant, issue_id: str, data: dict[str, str] | None
) -> RepairsFlow:
    """Create a fix flow for a consumable issue."""
    return ConsumableResetRepairFlow(data)
