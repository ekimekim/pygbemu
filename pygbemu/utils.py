

def iterable(x):
	try:
		iter(x)
	except TypeError:
		return False
	return True


def get_all_subclasses(cls):
	"""Recursive method to find all decendents of cls, ie.
	it's subclasses, subclasses of those classes, etc.
	Returns a set.
	"""
	subs = set(cls.__subclasses__())
	subs_of_subs = [get_all_subclasses(subcls) for subcls in subs]
	return subs.union(*subs_of_subs)


class Blank(object):
	"""Dummy object that accepts setitem and getitem but doesn't take writes and only reads zeroes"""
	def __getitem__(self, index):
		return 0

	def __setitem__(self, index, value):
		pass


class Offset(object):
	"""Object that presents a view into a larger list at a given offset"""
	def __init__(self, base, offset):
		self.base = base
		self.offset = offset

	def __getitem__(self, index):
		return self.base[index - self.offset]

	def __setitem__(self, index, value):
		self.base[index - self.offset] = value
