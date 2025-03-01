class rand48:
    def __init__(self, seed):
        self.a = 0x5DEECE66D
        self.b = 0xB
        self.x_1 = bin(0x330E)[2:].zfill(16)
        self.x_2 = bin(seed)[2:].zfill(32)
        self.x = int(self.x_1+self.x_2, 2)
        self.y = 2**48

    def get_next(self):
        self.x = (self.a*self.x + self.b) & (self.y - 1)
        return self.x
    
    def drand48(self):
        return self.get_next()/self.y
