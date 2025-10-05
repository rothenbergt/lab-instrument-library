"""
Mock implementation of PyVISA for testing without real hardware.

This module provides mock classes that mimic the behavior of PyVISA's
ResourceManager and Resource classes, allowing tests to run without
physical instruments connected. This version is stateful and tries to
emulate common SCPI for multimeters so tests are more realistic.
"""

from typing import Dict, Any, List, Optional


def _canonical_func(token: str) -> str:
    t = (token or "").strip().upper()
    synonyms = {
        # DC Voltage
        "VOLT": "VOLT", "VOLT:DC": "VOLT", "VDC": "VOLT", "DCV": "VOLT",
        # AC Voltage
        "VOLT:AC": "VOLT:AC", "VAC": "VOLT:AC", "ACV": "VOLT:AC",
        # DC Current
        "CURR": "CURR", "CURR:DC": "CURR", "IDC": "CURR", "DCI": "CURR",
        # AC Current
        "CURR:AC": "CURR:AC", "IAC": "CURR:AC", "ACI": "CURR:AC",
        # Resistance
        "RES": "RES", "OHM": "RES", "OHMS": "RES",
        # 4-wire Resistance
        "FRES": "FRES", "4W": "FRES", "4WIRE": "FRES", "4-WIRE": "FRES",
    }
    return synonyms.get(t, t)


class MockResource:
    """Mock implementation of a PyVISA Resource with stateful SCPI."""

    def __init__(self, resource_name: str, responses: Dict[str, str] = None):
        self.resource_name = resource_name
        self.responses = responses or {}
        self.default_response = "0"
        self.timeout = 5000
        self.write_termination = "\n"
        self.read_termination = "\n"
        self.baud_rate = 9600
        self.last_command: Optional[str] = None
        self.closed = False
        self.command_log: List[str] = []

        # Instrument state
        self.idn = self.responses.get("*IDN?", "HEWLETT-PACKARD,34401A,0,1.0-5.0")
        self.current_function = "VOLT"
        self.sample_index = 0
        self.last_reading: Optional[float] = None
        self.trigger_source = "IMM"
        self.trigger_count = 1
        self.sample_count = 1
        self.armed = False
        self.display_text = ""
        self.dual_display_enabled = False
        self.beep_enabled = True
        self.ranges: Dict[str, float] = {"VOLT": 10.0, "VOLT:AC": 10.0, "CURR": 1.0, "CURR:AC": 1.0, "RES": 10000.0, "FRES": 10000.0}
        self.autorange: Dict[str, bool] = {k: True for k in self.ranges.keys()}

    def _norm(self, cmd: str) -> str:
        return (cmd or "").strip()

    def _norm_upper(self, cmd: str) -> str:
        # SCPI is case-insensitive, allow optional leading colon and flexible spaces
        c = self._norm(cmd)
        c = c.replace("\t", " ")
        while "  " in c:
            c = c.replace("  ", " ")
        return c.upper()

    def _compute_reading(self, func: str, increment: bool = True) -> float:
        func_c = _canonical_func(func)
        seeds = {
            "VOLT": 1.2345,
            "VOLT:AC": 0.12345,
            "CURR": 0.012345,
            "CURR:AC": 0.0012345,
            "RES": 123.45,
            "FRES": 123.456,
        }
        base = seeds.get(func_c, 0.0)
        if increment:
            self.sample_index += 1
        value = base + 0.0001 * self.sample_index
        self.last_reading = value
        return value

    def write(self, command: str) -> None:
        if self.closed:
            raise ValueError("Resource is closed")
        self.last_command = command
        self.command_log.append(command)

        u = self._norm_upper(command)
        # Settings-style commands (no response)
        if u.startswith(":CONF:") or u.startswith("CONF:"):
            token = u.split(":")[-1]
            self.current_function = _canonical_func(token)
            return
        if u.startswith("FUNC ") or u.startswith(":FUNC "):
            token = u.split(" ", 1)[1].strip().strip("\"")
            self.current_function = _canonical_func(token)
            return
        if ":RANG " in u:
            # e.g., VOLT:RANG 10 or :SENS:VOLT:DC:RANG 10 (we support simple form)
            try:
                func, rest = u.split(":RANG", 1)
                func = func.strip(": ")
                value_str = rest.split(" ", 1)[1].strip()
                value = float(value_str)
                self.ranges[_canonical_func(func)] = value
            except Exception:
                pass
            return
        if ":RANG:AUTO " in u:
            try:
                func, rest = u.split(":RANG:AUTO", 1)
                func = func.strip(": ")
                value_str = rest.split(" ", 1)[1].strip()
                enabled = value_str in ("1", "ON", "TRUE")
                self.autorange[_canonical_func(func)] = enabled
            except Exception:
                pass
            return
        if u.startswith(":TRIG:SOUR ") or u.startswith("TRIG:SOUR "):
            self.trigger_source = u.split(" ", 1)[1].strip()
            return
        if u.startswith(":TRIG:COUN ") or u.startswith("TRIG:COUN "):
            try:
                self.trigger_count = int(u.split(" ", 1)[1].strip())
            except Exception:
                pass
            return
        if u.startswith(":SAMP:COUN ") or u.startswith("SAMP:COUN "):
            try:
                self.sample_count = int(u.split(" ", 1)[1].strip())
            except Exception:
                pass
            return
        if u.startswith(":INIT") or u == "INIT":
            self.armed = True
            return
        if u.startswith(":DISP:TEXT ") or u.startswith("DISP:TEXT "):
            # Extract text inside quotes if present
            raw = command.split(" ", 1)[1].strip()
            self.display_text = raw.strip().strip("\"")
            return
        if u.startswith(":DISP:TEXT:CLE") or u.startswith("DISP:TEXT:CLE"):
            self.display_text = ""
            return
        if u.startswith(":DISP:WIND2:STAT ") or u.startswith("DISP:WIND2:STAT "):
            self.dual_display_enabled = u.endswith("ON")
            return
        if u.startswith(":SYST:BEEP:STAT ") or u.startswith("SYST:BEEP:STAT "):
            self.beep_enabled = u.endswith("ON")
            return
        # Other commands (e.g., *RST, *CLS) are accepted silently

    def read(self) -> str:
        if self.closed:
            raise ValueError("Resource is closed")
        if not self.last_command:
            return "ERROR: No command sent" + self.read_termination
        # Defer to query-like behavior for last command if it was a query
        if self.last_command.strip().endswith("?"):
            return self._respond_to(self.last_command) + self.read_termination
        # For write commands, there's nothing to read
        return self.default_response + self.read_termination

    def _respond_to(self, command: str) -> str:
        u = self._norm_upper(command)
        # Common queries (stateful)
        if u == "*IDN?":
            return self.idn
        if u == "*OPC?":
            return "1"
        if u == "SYST:ERR?" or u == ":SYST:ERR?":
            return "0,No error"
        if u == "FUNC?" or u == ":FUNC?":
            return f'"{self.current_function}"'
        if u.startswith("MEAS:") or u.startswith(":MEAS:"):
            token = u.split(":", 1)[1][5:]  # after 'MEAS:'
            token = token.rstrip("?")
            token = _canonical_func(token)
            self.current_function = token
            value = self._compute_reading(token, increment=True)
            return f"{value}"
        if u == "READ?" or u == ":READ?":
            token = self.current_function
            value = self._compute_reading(token, increment=True)
            return f"{value}"
        if u == "FETC?" or u == ":FETC?":
            if self.last_reading is None:
                value = self._compute_reading(self.current_function, increment=False)
            else:
                value = self.last_reading
            return f"{value}"
        # Range and autorange queries
        if ":RANG?" in u:
            func = u.split(":RANG?", 1)[0].strip(": ")
            value = self.ranges.get(_canonical_func(func), 0.0)
            return f"{value}"
        if ":RANG:AUTO?" in u:
            func = u.split(":RANG:AUTO?", 1)[0].strip(": ")
            enabled = self.autorange.get(_canonical_func(func), True)
            return "1" if enabled else "0"
        # Model-specific odds and ends that tests might poke
        if u == ":DISP:TEXT?" or u == "DISP:TEXT?":
            return f'"{self.display_text}"'
        # Finally, allow explicit canned responses for anything not modeled above
        if command in self.responses:
            return str(self.responses[command])
        return self.default_response

    def query(self, command: str, **_kwargs) -> str:
        # Accept extra kwargs (e.g., delay=...) to mimic some library calls
        self.last_command = command
        self.command_log.append(command)
        return self._respond_to(command) + self.read_termination

    def read_raw(self) -> bytes:
        response = self.read()
        return response.encode("utf-8")

    def query_binary_values(self, command: str, datatype: str = "f", is_big_endian: bool = True, container: Any = list) -> List[Any]:
        self.write(command)
        return container([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

    def query_ascii_values(self, command: str, separator: str = ",", container: Any = list) -> List[Any]:
        self.write(command)
        return container([1.1, 2.2, 3.3, 4.4, 5.5])

    def close(self) -> None:
        self.closed = True


class MockResourceManager:
    """Mock implementation of PyVISA ResourceManager."""

    def __init__(self, resources: Dict[str, MockResource] = None):
        self.resources = resources or {}

    def open_resource(self, resource_name: str, **_kwargs) -> MockResource:
        if resource_name in self.resources:
            return self.resources[resource_name]
        # Create default resource with sane defaults
        standard_responses = {
            "*IDN?": "HEWLETT-PACKARD,34401A,0,1.0-5.0",
            "*RST": "",
            "*CLS": "",
            "*OPC?": "1",
            "SYST:ERR?": "0,No error",
        }
        resource = MockResource(resource_name, standard_responses)
        self.resources[resource_name] = resource
        return resource

    def list_resources(self, query: str = "?*::INSTR") -> List[str]:
        return list(self.resources.keys())

    def close(self) -> None:
        for resource in self.resources.values():
            resource.close()
