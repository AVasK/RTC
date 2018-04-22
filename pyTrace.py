# PyTrace: Prototyping iterative raytracing
from math import sqrt

class vec3:
    '3d vector class'
    
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
        
    # settting new coordinates to vector
    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    # representation for printing it out
    def __str__(self):
        return 'vec3 @ ({0}, {1}, {2})'.format(self.x, self.y, self.z)
    
    # vec operations:
    
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
    
    
# does not affect parameter
def normalized(vec):
    norm = sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)
    if norm == 0:
        norm = 1
    return vec3(vec.x / norm, vec.y / norm, vec.z / norm)

def sq_norm(vec):
    norm = sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)
    return norm


def dist(vec1, vec2):
    v = vec2 - vec1
    return sqrt(v.x * v.x + v.y * v.y + v.z * v.z)

    
""" 
v1 = vec3(1,0,0)
v2 = vec3(1,2,2)
v3 = vec3(1,0,1)

v4 = (((v1 + v2 - v3) / 5))
print(normalized(v4))
"""

class Ray:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        
    def dir(self):
        return self.end - self.start
    
    def pos(self):
        return self.start
        
    def __str__(self):
        return "Vector: {0} -> {1}".format(self.start, self.end)
    
    def length(self):
        return dist(self.end, self.start)

def f(p):
    if dist(p, vec3(0,150,0)) < 50:
        return 0
    else:
        return 10
    
def Sphere(x, center, radius):
    #return abs(dist(x, center)) + radius
    return f(x)

'''
def RayTrace(ray) -> vec3:
    color = vec3(0,0,0)
    
    hit = RayIntersect(ray) # either a vec3 or False.
    if not hit:
        return color
    
    hit_point = ray.pos() + ray.dir() * hit

    #shading:
    for ls in scene.lights:
        if visible(hit_point, ls):
            color += shade(hit_point, hit.normal)


'''

camera_pos = vec3(0,-50,0)
camera_dir = vec3(0,1,0)
d = 50
screen_center = camera_pos + normalized(camera_dir) * d



W, H = 100, 100

img = [[' ' for w in range (0, H)] for h in range(0, W)]

out = open('out.ppm', 'w')
out.write('P3\n{0} {1} 255\n'.format(W, H))

for x in range(-W//2, W - W//2 + 1):
    for z in range(-H//2, H - H//2 + 1):
        color = vec3(0,0,0)
        
        offset = vec3(x, 0, z)
        on_screen_pos = screen_center + offset

        ray = Ray(camera_pos, on_screen_pos)
        #ray = Ray(on_screen_pos, on_screen_pos + camera_dir)

        step = 10
        while ray.length() <= 500:
            color.set(0,0,0)
            if Sphere(ray.end, vec3(0,150,0), 100) <= 0:
                color = vec3(255,255,255)
                break
            ray.end += normalized(ray.dir()) * step
        
        if color.x == 255: img[x][z] = '*'
        out.write("{0} {1} {2}\n".format(color.x, color.y, color.z))
        
out.close()
for row in img:
    print(''.join(row))


