from typing import Any

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ADDRESS, CONF_ID

CONF_START_ADDRESS = "start_address"
CONF_DEFAULT = "default"
CONF_NUMBER = "number"
CONF_ON_READ = "on_read"
CONF_ON_WRITE = "on_write"

modbus_server_ns = cg.esphome_ns.namespace("modbus_server")
ModbusDeviceComponent = modbus_server_ns.class_("ModbusServer", cg.Component)

DEPENDENCIES = ["uart"]

_REGISTER_RANGE_SCHEMA = cv.ensure_list(cv.Schema({
    cv.Required(CONF_START_ADDRESS): cv.positive_int,
    cv.Optional(CONF_DEFAULT, 0): cv.positive_int,
    cv.Optional(CONF_NUMBER, 1): cv.positive_int,
    cv.Optional(CONF_ON_READ): cv.returning_lambda,
    cv.Optional(CONF_ON_WRITE): cv.returning_lambda,
}))

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(ModbusDeviceComponent),
            cv.Required(CONF_ADDRESS): cv.positive_int,
            cv.Optional("holding_registers"): _REGISTER_RANGE_SCHEMA,
            cv.Optional("input_registers"): _REGISTER_RANGE_SCHEMA,
        }
    )
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)

MULTI_CONF = True
CODEOWNERS = ["@jpeletier"]

async def _register_range_to_code(register_config: list[dict[str, Any]], server, *, kind: str) -> None:
    for reg in register_config:
        cg.add(
            getattr(server, f"add_{kind}_register")(
                reg[CONF_START_ADDRESS], reg[CONF_DEFAULT], reg[CONF_NUMBER]
            )
        )
        if CONF_ON_READ in reg:
            template_ = await cg.process_lambda(
                reg[CONF_ON_READ],
                [
                    (cg.uint16, "address"),
                    (cg.uint16, "value"),
                ],
                return_type=cg.uint16,
            )
            cg.add(
                getattr(server, f"on_read_{kind}_register")(
                    reg[CONF_START_ADDRESS], template_, reg[CONF_NUMBER]
                )
            )
        if CONF_ON_WRITE in reg:
            template_ = await cg.process_lambda(
                reg[CONF_ON_WRITE],
                [
                    (cg.uint16, "address"),
                    (cg.uint16, "value"),
                ],
                return_type=cg.uint16,
            )
            cg.add(
                getattr(server, f"on_write_{kind}_register")(
                    reg[CONF_START_ADDRESS], template_, reg[CONF_NUMBER]
                )
            )

async def to_code(config):
    cg.add_library("emelianov/modbus-esp8266", "4.1.1")
    id = config[CONF_ID]
    uart = await cg.get_variable(config["uart_id"])
    server = cg.new_Pvariable(id)
    cg.add(server.set_uart_parent(uart))
    cg.add(server.set_address(config[CONF_ADDRESS]))
    if regs := config.get("holding_registers"):
        await _register_range_to_code(regs, server, kind="holding")
    if regs := config.get("input_registers"):
        await _register_range_to_code(regs, server, kind="input")
    await cg.register_component(server, config)
