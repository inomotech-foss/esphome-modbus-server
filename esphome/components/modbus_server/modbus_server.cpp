// This ESPHome component wraps around the modbus-esp8266 by @emelianov:
// https://github.com/emelianov/modbus-esp8266
//
// by @jpeletier - Epic Labs, 2022

#include "modbus_server.h"

#define TAG "ModbusServer"

namespace esphome {
namespace modbus_server {
ModbusServer::ModbusServer() {}

uint32_t ModbusServer::baudRate() { return this->parent_->get_baud_rate(); }

float ModbusServer::get_setup_priority() const {
  // After UART bus
  return setup_priority::BUS - 1.0f;
}

void ModbusServer::setup() { mb.begin(this); }

void ModbusServer::set_address(uint8_t address) { mb.slave(address); }

bool ModbusServer::add_holding_register(uint16_t start_address, uint16_t value, uint16_t numregs) {
  return mb.addHreg(start_address, value, numregs);
}

bool ModbusServer::write_holding_register(uint16_t address, uint16_t value) { return mb.Hreg(address, value); }

uint16_t ModbusServer::read_holding_register(uint16_t address) { return mb.Hreg(address); }

void ModbusServer::on_read_holding_register(uint16_t address, cbOnReadWrite cb, uint16_t numregs) {
  mb.onGet(
      HREG(address), [cb](TRegister *reg, uint16_t val) -> uint16_t { return cb(reg->address.address, val); }, numregs);
}

void ModbusServer::on_write_holding_register(uint16_t address, cbOnReadWrite cb, uint16_t numregs) {
  mb.onSet(
      HREG(address), [cb](TRegister *reg, uint16_t val) -> uint16_t { return cb(reg->address.address, val); }, numregs);
}

bool ModbusServer::add_input_register(uint16_t start_address, uint16_t value, uint16_t numregs) {
  return mb.addIreg(start_address, value, numregs);
}

void ModbusServer::on_read_input_register(uint16_t address, cbOnReadWrite cb, uint16_t numregs) {
  mb.onGet(
      IREG(address), [cb](TRegister *reg, uint16_t val) -> uint16_t { return cb(reg->address.address, val); }, numregs);
}

void ModbusServer::on_write_input_register(uint16_t address, cbOnReadWrite cb, uint16_t numregs) {
  mb.onSet(
      IREG(address), [cb](TRegister *reg, uint16_t val) -> uint16_t { return cb(reg->address.address, val); }, numregs);
}

// Stream class implementation:
size_t ModbusServer::write(uint8_t data) { return uart::UARTDevice::write(data); }
int ModbusServer::available() { return uart::UARTDevice::available(); }
int ModbusServer::read() { return uart::UARTDevice::read(); }
int ModbusServer::peek() { return uart::UARTDevice::peek(); }
void ModbusServer::flush() { uart::UARTDevice::flush(); }

void ModbusServer::loop() { mb.task(); };
}  // namespace modbus_server

}  // namespace esphome
