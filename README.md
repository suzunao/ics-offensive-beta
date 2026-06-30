# ICS Offensive MCP

MCP (Model Context Protocol) server for OT/ICS/SCADA offensive security tools.

## Requisitos

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip
- tmux (para mantener el servidor en background)
- OpencCode CLI

## Instalación

```bash
# Clonar / 
git clone 

#situarse en el proyecto
cd ~/ICS-Scada/ics-offensive-mcp

# Opción A — uv (recomendado)
uv sync

# Opción B — pip
pip install -r requirements.txt
```

## Dominios

| Dominio | Tools | Protocolos |
|---------|-------|-----------|
| PLC | 15 | S7comm, CIP, Modbus |
| RTU | 6 | DNP3, IEC 104 |
| SCADA | 8 | OPC DA, DDE, SQL |
| MITM | 5 | ARP, Modbus, S7, DNP3 |
| Grid | 5 | IEC 61850, MMS, GOOSE |
| Firmware | 10 | JTAG, SPI, UART |
| Supply Chain | 9 | Step7, ACD, STU |
| Persistence | 10 | WMI, covert channels |
| C2 | 8 | DNS, ICMP, Modbus |
| Full Operation | 2 | Campaign planning |
