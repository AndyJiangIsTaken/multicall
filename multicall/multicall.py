from typing import List

from web3.auto import w3

from multicall import Call
from multicall.constants import MULTICALL_ADDRESS


class Multicall:
    def __init__(self, calls: List[Call], _w3=None, block_id=None, require_success: bool = True):
        self.calls = calls
        self.block_id = block_id
        self.require_success = require_success

        if _w3 is None:
            self.w3 = w3
        else:
            self.w3 = _w3

    def __call__(self):
        if self.require_success is True:
            multicall_sig = 'aggregate((address,bytes)[])(uint256,bytes[])'
        else:
            multicall_sig = 'tryBlockAndAggregate(bool,(address,bytes)[])(uint256,uint256,(bool,bytes)[])'

        aggregate = Call(
            MULTICALL_ADDRESS,
            multicall_sig,
            returns=None,
            _w3=self.w3,
            block_id=self.block_id
        )

        if self.require_success is True:
            args = [[[call.target, call.data] for call in self.calls]]
            _, outputs = aggregate(args)
            outputs = ((None, output) for output in outputs)
        else:
            args = [self.require_success, [[call.target, call.data] for call in self.calls]]
            _, _, outputs = aggregate(args)

        result = []
        for call, (success, output) in zip(self.calls, outputs):
            result.append(call.decode_output(output, success))

        return result
