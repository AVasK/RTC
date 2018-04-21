# PyTrace: Prototyping iterative raytracing
from math import sqrt

class vec3:
    '3d vector class'
    
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        return 'vec3 @ ({0}, {1}, {2})'.format(self.x, self.y, self.z)
    
    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, num):
        return vec3(self.x * num, self.y * num, self.z * num)
    
    def __truediv__(self, num):
        return vec3(self.x / num, self.y / num, self.z / num)
    
    def dot(self, other):
        return (self.x * other.x + self.y * other.y + self.z * other.z)
    
    
def normalized(vec):
    norm = sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)
    return vec3(vec.x / norm, vec.y / norm, vec.z / norm)


    
    
v1 = vec3(1,0,0)
v2 = vec3(1,2,2)
v3 = vec3(1,0,1)


v4 = (((v1 + v2 - v3) / 5))
print(normalized(v4))