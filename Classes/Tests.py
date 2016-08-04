from Classes import cachestoreS

if __name__ == '__main__':
	columns = [["ID","INT"],["COUNT","INT"],["NOMBRE","TEXT"]]
	c = cachestoresqlite("~/cacheful",columns)
	print (type(c))