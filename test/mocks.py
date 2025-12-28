from unittest.mock import MagicMock
from .testconstants import EXCEPTION_REASON

class MockStreamReader:
    def __init__(self, output_data):
        lines_list = output_data.splitlines()
        self.output_lines = lines_list[::-1]

    async def readline(self):
        if self.output_lines:
            line = self.output_lines.pop()
            return line.encode('utf-8') + b'\n'
        return b'' 

class MockAsyncProcess(MagicMock):
    def __init__(self, input=None, *args, **kwargs):
        super().__init__()
        self.stdout = MockStreamReader(input or "")
        self.stderr = MockStreamReader("")
        self.returncode = 0

    async def wait(self):
        return self.returncode

    async def communicate(self, inp: bytes = None):
        return (b"", None)

class FaultyCache:
    def get_counts(self):
        raise Exception(EXCEPTION_REASON)
    def get_metadata_for_size(self, n: int):
        raise Exception(EXCEPTION_REASON)
    def get_fullerene(self, n:int, id:int):
        raise Exception(EXCEPTION_REASON)