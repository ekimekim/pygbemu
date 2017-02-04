

class Display(object):
	# This is just a stub for now
	def __init__(self):
		self.tile_data = [0] * 0x1800
		self.tile_maps = [0] * 0x800
		self.sprite_data = [0] * 4 * 40
		self.scroll_x = 0
		self.scroll_y = 0
		self.status = 0
