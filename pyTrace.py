# PyTrace: Prototyping iterative raytracing
from math import sqrt

import time

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
    
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        return False
    
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
    
    def norm(self):
        return Ray(self.start, self.start + self.dir())
    
    
class Light:
    def __init__(self, position, color):
        self.pos = position
        self.color = color

class Material:
    def __init__(self, diffuse = 1, reflection = 0, refraction = 0, refract_coeff = 1, color = vec3(255,255,255), refl_fading = 0.8):
        self.color = color
        self.diffuse = diffuse
        self.reflection = reflection
        self.refraction = refraction
        self.refraction_coeff = refract_coeff
        self.refl_fading = refl_fading
    
    def set_color(self, new_color):
        self.color = new_color
    
def f(p):
    if dist(p, vec3(0,150,0)) < 50:
        return 0
    else:
        return 10
    
def Sphere(x, center, radius):
    return dist(x, center) - radius

def s1(x):
    return Sphere(x, vec3(W//2, 300, H//2 + 80), 150)

def s2(x):
    return Sphere(x, vec3(W//2 + 200, 200, H//2 + 80), 100)

def plane(p):
    return p.x - 3

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


###
### CONSTANTS & OTHER DATA:
###

H, W = 400, 400
MAX_RAY_LENGTH = 600
NUM_OF_REFLECTIONS = 4
BOX = vec3(4*W, 500, 4*H) 

camera = vec3(W//2, -200, H//2)

object_functions = [s1, s2, plane]

light1 = Light(vec3(W//2, 0, H//2) + vec3(30, 0, 10), vec3(255,255,255)/2)
lights = [light1, Light(vec3(-20, 10, H//2 + 80), vec3(12, 14, 12))]
soft_lights = [] 
materials = {}

default_mat = Material()
for f in object_functions:
    materials[f] = default_mat
materials[s2] = Material(diffuse = 0.6, reflection = 0.7, color = vec3(212, 212, 250))
materials[s1] = Material(reflection = 0.6, color = vec3(200, 120, 10))



img = [[0 for w in range (0, W)] for h in range(0, H)]
console = [['.' for w in range (0, W)] for h in range(0, H)]
out = open('out.ppm', 'w')
out.write('P3\n{0} {1} 255\n'.format(W, H))


###
### RAY-TRACING:
###

def DistanceEval(f, p): # DistEval(func, point)
    return f(p)

def EstNormal(z, obj, eps = 0.001):
    z1 = z + vec3(eps, 0, 0)
    z2 = z - vec3(eps, 0, 0)
    z3 = z + vec3(0, eps, 0)
    z4 = z - vec3(0, eps, 0)
    z5 = z + vec3(0, 0, eps)
    z6 = z - vec3(0, 0, eps)
    
    dx = DistanceEval(obj, z1) - DistanceEval(obj, z2)
    dy = DistanceEval(obj, z3) - DistanceEval(obj, z4)
    dz = DistanceEval(obj, z5) - DistanceEval(obj, z6)
    
    return normalized(vec3(dx,dy,dz) / (2.0 * eps))


def RayIntersectLinear(ray, step = 4, ignore_mesh = []):
    ' returns False if no intersection is found, or [dist, point]'
    i = 1
    while i <= MAX_RAY_LENGTH:
        dot = ray.org() + ray.sdir * i * step ### ray.sdir <-> ray.dir()
        if abs(dot.y) >= BOX.y or abs(dot.x) >= BOX.x or abs(dot.z) >= BOX.z: ### BOX added
            return False
        for f in object_functions:
            if f not in ignore_mesh:
                if f(dot) <= 0:
                    if step > 2:
                        i -= 1
                        step /= 2
                    else:
                        return [dist(ray.org(), dot), dot]
        i += 1
    return False


'''
def RayIntersect(ray):
    step = 1
    for i in range(0, MAX_RAY_LENGTH):
        dot = ray.org() + ray.sdir * i * step
        for f in object_functions:
            if f(dot) <= 0:
                return [dist(ray.org(), dot), dot]
    return False
'''

# If i'm right, this should be a Distance-Aided implementation
def RayIntersect(ray, max_len = MAX_RAY_LENGTH, ignore_mesh = []):
    dot = ray.org()
    dist_min = object_functions[0](dot)
    min_dist = 4
    #max_len = MAX_RAY_LENGTH
    while dist_min >= min_dist and dist(ray.org(), dot) <= max_len:
        dist_min = object_functions[0](dot)
        for f in set(object_functions[1:]).difference(set(ignore_mesh)):
            dst = f(dot)
            if dst < dist_min:
                dist_min = dst
                
        dot += ray.sdir * dist_min ### ray.sdir <-> ray.dir()
    #print("Out of cycle!\n")
    return RayIntersectLinear(Ray(dot, dot + ray.sdir))  ### using ray.sdir instead of ray.dir(). sdir caches dir() at ray creation
           

def RayTrace(ray, refl_depth = NUM_OF_REFLECTIONS, ignore_mesh_rt = []):
    color = vec3(0,0,0)
    black = vec3(0,0,0)
    
    hit = RayIntersect(ray, ignore_mesh = ignore_mesh_rt) # either a [dist, hit_point] or False.
    if not hit:
        return color
    
    hit_point = hit[1]
    
    ## Memorizing the surface of the hit:
    f = object_functions[0]
    for func in object_functions[1:]:
        if func(hit_point) < f(hit_point):
            f = func
            
    #color = clamp(vec3(255,255,255) * dL)
    
    #shading:
    mat = materials[f] # <- current material
    
    Normal = EstNormal(hit_point, f, 0.001)
    dI = normalized(Normal).dot(normalized(ray.sdir))
    if dI < 0:
        dI = -dI
    color = mat.color * dI
    
    for ls in lights:
        color += shade(ls, hit_point, f) * mat.diffuse
    
    
    # hard shadows
    #for ls in lights:
        #if visible(hit_point, ls.pos):
            #print("visible")
            #color += shade(ls, hit_point, f) * mat.diffuse
    
        
    
    if materials[f].reflection > 0 and refl_depth > 0: # relfection > 0
        reflected = reflect(f, ray, hit_point)
        #color += RayTrace(reflected, refl_depth - 1) * materials[f].reflection
        refl_color_temp = RayTrace(reflected, refl_depth - 1, ignore_mesh_rt = [f]) 
        try:
            refl_color = refl_color_temp * (mat.refl_fading ** (NUM_OF_REFLECTIONS - refl_depth))  * materials[f].reflection
        except NameError:
            refl_color += refl_color_temp * (mat.refl_fading ** (NUM_OF_REFLECTIONS - refl_depth))  * materials[f].reflection
            
    if materials[f].reflection <= 0:
        refl_color = vec3(0,0,0)
        
    try:
        color = refl_color * mat.reflection + color * (1 - mat.reflection)
    except NameError:
        pass
        
    return clamp(color)

def reflect(f, ray, hit_point):
    normal = EstNormal(hit_point, f)
    temp = normal * ray.dir().dot(normal) * -2
    return Ray(hit_point, hit_point + ray.sdir + temp)

def shade(light, hit_point, f):
    Light_dir = light.pos - hit_point
    Normal = EstNormal(hit_point, f, 0.001)
    dI = normalized(Normal).dot(normalized(Light_dir))
    return clamp(light.color * dI)
    

def visible(point, obj):
    ray = Ray(point, obj)#.norm()
    ray = ray.norm()
    #print(point, obj, ray, '\n')
    intersect = RayIntersect(ray, max_len = dist(point, obj) - 3, ignore_mesh = [f])
    if intersect == False:
        return True
    return False
        
    

def RTC():
    for h in range(0, H):
        percent = h*100/H
        if percent % 10 == 0: print(percent, '% complete') # % complete
        for w in range(0, W):
            ray = Ray(camera, vec3(h, 0, w))
            ray.start += ray.sdir * dist(ray.start, vec3(h,0,w)) * 0.8
            color = RayTrace(ray)
            
            img[h][w] = color
            out.write('{0} {1} {2}\n'.format(int(color.x), int(color.y), int(color.z)))

t1 = time.clock()
RTC()
t2 = time.clock()
print(t2 - t1)

#for row in console:
    #print(''.join(row))
    
