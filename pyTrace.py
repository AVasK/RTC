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

def s1(x):
    return Sphere(x, vec3(W//2, 400, H//2), 300)

def s2(x):
    return Sphere(x, vec3(W//2 - 40, 50, H//2 + 40), 20)

def clamp(clr):
    if clr.x > 255:
        clr.x = 255
    if clr.x < 0:
        clr.x = 0
    if clr.y > 255:
        clr.y = 255
    if clr.y < 0:
        clr.y = 0
    if clr.z > 255:
        clr.z = 255
    if clr.z < 0:
        clr.z = 0
    
    return clr



H, W = 200, 200


camera = vec3(W//2, 0, H//2)
light = camera - vec3(20, 0, -20)

object_functions = [s1, s2]

img = [[0 for w in range (0, W)] for h in range(0, H)]
console = [['.' for w in range (0, W)] for h in range(0, H)]
out = open('out.ppm', 'w')
out.write('P3\n{0} {1} 255\n'.format(W, H))

def DistanceEval(p): # DistEval(func, point)
    f = object_functions[0]
    for func in object_functions[1:]:
        if func(p) < f(p):
            f = func
    return f(p)

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

def RayIntersectLinear(ray):
    step = 1
    for i in range(0, 200):
        dot = ray.org() + ray.sdir * i * step
        for f in object_functions:
            if f(dot) <= 0:
                return [dist(ray.org(), dot), dot]
    return False

# If i'm right, this should be a Distance-Aided render
def RayIntersect(ray):
    dot = ray.org()
    dist_min = object_functions[0](dot)
    min_dist = 4
    max_len = 400
    while dist_min >= min_dist and dist(ray.org(), dot) <= max_len:
        dist_min = object_functions[0](dot)
        for f in object_functions[1:]:
            dst = f(dot)
            if dst < dist_min:
                dist_min = dst
                
        dot += ray.sdir * dist_min
    #print("Out of cycle!\n")
    return RayIntersectLinear(Ray(dot, dot + ray.sdir))
           

def RayTrace(ray):
    color = vec3(0,0,0)
    
    hit = RayIntersect(ray) # either a [dist, hit_point] or False.
    if not hit:
        return color
    
    hit_point = hit[1]
    L = light - hit_point
    N = EstNormal(hit_point, 0.001)
    dL = normalized(N).dot(normalized(L))
    
    color = clamp(vec3(255,255,255) * dL)
    #shading:

    #for ls in scene.lights:
        #if visible(hit_point, ls):
            #color += shade(hit_point, hit.normal)

    return color


def RTC():
    for h in range(0, H):
        percent = h*100/H
        if percent % 10 == 0: print(percent, '% complete\n') # % complete
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
