import clr
import os
from serial import Serial
import time

PORT="COM3"
BAUD = 9600
MAX_LEN = 14

clr.AddReference(os.path.abspath('C:/Users/Joshua/Desktop/LibreHardwareMonitor-net472/LibreHardwareMonitorLib.dll'))


from LibreHardwareMonitor.Hardware import Computer

def create_output_str(prefix: str, data: str, suffix: str) -> str:
    # CPU:   26.00 C
    # CPU:   6.00 C
    str_len = len(prefix) + len(data) + len(suffix)
    padding = pad_spaces(str_len)
    output_str = prefix + padding + data + suffix + "\n"
    return output_str.encode("utf-8")

def pad_spaces(str_len: int) -> str:
    pad_str = ""
    for i in range(MAX_LEN - str_len):
        pad_str += " "
    return pad_str

def connect_to_uno() -> Serial:
    s = Serial(PORT, BAUD)
    while True:
        data = s.read()
        if data:
            print("Arduino Setup Complete")
            break
    return s

def get_data(computer: Computer) -> dict:
    # cpu is /amdcpu/0/temperature/2
    # gpu is /gpu-nvidia/0/temperature/0
    # ram is /ram/load/0
    data_dict = {"cpu": "", "ram": "", "gpu": ""}

    for i in range(len(computer.Hardware)):
        for j in range(len(computer.Hardware[i].Sensors)):
            if "/amdcpu/0/temperature/2" in str(computer.Hardware[i].Sensors[j].Identifier):
                data_dict["cpu"] = "%.02f" % computer.Hardware[i].Sensors[j].get_Value()
            if "/gpu-nvidia/0/temperature/0" in str(computer.Hardware[i].Sensors[j].Identifier):
                data_dict["gpu"] = "%.02f" % computer.Hardware[i].Sensors[j].get_Value()
            if "/ram/load/0" in str(c.Hardware[i].Sensors[j].Identifier):
                data_dict["ram"] = "%.02f" % computer.Hardware[i].Sensors[j].get_Value()
            computer.Hardware[i].Update()
    
    return data_dict

def data_loop(computer: Computer, display: Serial) -> None:
    while True:
        try:
            data = get_data(computer)
            cpu_str = create_output_str("CPU:", data["cpu"], " C")
            gpu_str = create_output_str("GPU:", data["gpu"], " C")
            ram_str = create_output_str("RAM:", data["ram"], " %")
            display.write(ram_str)
            display.write(gpu_str)
            display.write(cpu_str)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopping data loop.")
            break


if __name__ == "__main__":
    c = Computer()
    c.IsCpuEnabled = True
    c.IsGpuEnabled = True
    c.IsMemoryEnabled = True
    c.Open()
    uno = connect_to_uno()
    data_loop(c, uno)
    uno.close()
