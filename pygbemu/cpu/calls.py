
from .instructions import instruction
from .stack import push
from .jumps import jump


def call(cpu, mem, target):
	high, low = divmod(target, 256)
	push(cpu, mem, high)
	push(cpu, mem, low)
	jump(cpu, mem, target)


@instruction(0xCD)
def call_nn(code, cpu, mem):
	low = cpu.fetch()
	high = cpu.fetch()
	addr = (high << 8) & low
	call(cpu, mem, addr)
	return 12
