import pointfree

@pointfree.pointfree
def first(iterable):
	for item in iterable:
		return item

	return None