"""
hardware_monitor.py — Reports RAM and disk usage via psutil.
"""

import psutil


class HardwareMonitor:
    @staticmethod
    def _gb(bytes_: int) -> float:
        return round(bytes_ / (1024 ** 3), 2)

    def get_ram_info(self) -> tuple[float, float]:
        """Returns (total_gb, available_gb)."""
        mem = psutil.virtual_memory()
        return self._gb(mem.total), self._gb(mem.available)

    def get_disk_info(self) -> tuple[float, float]:
        """Returns (total_gb, free_gb)."""
        disk = psutil.disk_usage("/")
        return self._gb(disk.total), self._gb(disk.free)

    def report(self) -> str:
        total_ram, avail_ram = self.get_ram_info()
        total_disk, free_disk = self.get_disk_info()
        return (
            f"Total RAM is {total_ram} gigabytes, "
            f"with {avail_ram} gigabytes available. "
            f"Total disk storage is {total_disk} gigabytes, "
            f"with {free_disk} gigabytes free."
        )


if __name__ == "__main__":
    print(HardwareMonitor().report())
