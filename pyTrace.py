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
    
    def length(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
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
        self.sdir = normalized(end - start)
        
    def dir(self):
        return normalized(self.end - self.start)
    
    def org(self):
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
    return dist(x, center) - radius

light = vec3(10, 0, 20)

H, W = 100, 100

img = [[0 for w in range (0, W)] for h in range(0, H)]
console = [['.' for w in range (0, W)] for h in range(0, H)]
out = open('out.ppm', 'w')
out.write('P3\n{0} {1} 255\n'.format(W, H))

def DistanceEval(p): # DistEval(func, point)
    return Sphere(p, vec3(W//2, 120, H//2), 80)

def EstNormal(z, eps):
    z1 = z + vec3(eps, 0, 0)
    z2 = z - vec3(eps, 0, 0)
    z3 = z + vec3(0, eps, 0)
    z4 = z - vec3(0, eps, 0)
    z5 = z + vec3(0, 0, eps)
    z6 = z - vec3(0, 0, eps)
    
    dx = DistanceEval(z1) - DistanceEval(z2)
    dy = DistanceEval(z3) - DistanceEval(z4)
    dz = DistanceEval(z5) - DistanceEval(z6)
    
    return normalized(vec3(dx,dy,dz) / (2.0 * eps))

def RayIntersect(ray):
    for i in range(0, 400):
        dot = ray.org() + ray.sdir * i
        if Sphere(dot, vec3(W//2, 120, H//2), 80) <= 0:
            return [dist(ray.org(), dot), dot]
    return False

def RayTrace(ray):
    color = vec3(0,0,0)
    
    hit = RayIntersect(ray) # either a [dist, hit_point] or False.
    if not hit:
        return color
    
    hit_point = hit[1]
    L = light - hit_point
    N = EstNormal(hit_point, 0.001)
    dL = normalized(N).dot(normalized(L))
    
    color = vec3(255,255,255) * dL
    #shading:

    #for ls in scene.lights:
        #if visible(hit_point, ls):
            #color += shade(hit_point, hit.normal)

    return color


def RTC():
    camera = vec3(W//2, 0, H//2)
    for h in range(0, H):
        if h % 10 == 0: print(h*100/H, '% complete\n') # % complete
        for w in range(0, W):
            ray = Ray(camera, vec3(h, 20, w))
            color = RayTrace(ray)
            
            img[h][w] = color
            out.write('{0} {1} {2}\n'.format(int(color.x), int(color.y), int(color.z)))

        
RTC()

#for row in console:
    #print(''.join(row))

'''

camera_pos = vec3(0,-50,0)
camera_dir = vec3(0,1,0)
d = 50
screen_center = camera_pos + normalized(camera_dir) * d



W, H = 100, 100

img = [[' ' for w in range (0, H)] for h in range(0, W)]

out = open('out.ppm', 'w')
out.write('P3\n{0} {1} 255\n'.format(W, H))

out.close()

for row in img:
    print(''.join(row))

'''
