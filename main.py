#! /usr/bin/env python
# coding=cp1251



import sys
import pygame
import math
import numpy as np

# Как-то сильно заморочно
# Почему не просто константа?
# NUM_OF_DIMS = 4
def num_of_dims(draft = 0):
  num_of_dims.N = num_of_dims.N + draft
  return num_of_dims.N
num_of_dims.N = 4

def colorizer(N):
  N = N + 1
  R = N % 2
  G = (N//2) % 2
  B = (N//4) % 2
  if (R+G+B)==0:
    R = G = B = 0.5
  return(R * 255, G * 255, B * 255)

def binarize(N, L):
  r = (x + (b,) for x in L for b in (0, 1))
  N = N - 1
  if N < 1:
    return r
  return binarize(N, r)

def generate_vertices(N):
  return binarize(N, ((),))

def mark_vertices(V):
  """Accept list from generate_vertices """
  return tuple((x, sum(x)) for x in V)

def generate_edges(M):
  """Accept list from mark_vertices"""
  for (i, v1) in enumerate(M):
    for v2 in M[i+1:]:
      d = sum(abs(x-y) for x,y in zip(v1[0], v2[0]))
      if d == 1:
        yield (v1, v2, min(v1[1], v2[1]))

def get_eges(N):
  return tuple(generate_edges(mark_vertices(generate_vertices(N))))

def create_rotate_matrix(rotate_dimensions, angle):
  rotate_matrix = np.eye(num_of_dims())
  rotate_matrix[rotate_dimensions[0], rotate_dimensions[0]] = math.cos(angle)
  rotate_matrix[rotate_dimensions[1], rotate_dimensions[1]] = math.cos(angle)
  rotate_matrix[rotate_dimensions[1], rotate_dimensions[0]] = -1 * math.sin(angle)
  rotate_matrix[rotate_dimensions[0], rotate_dimensions[1]] = math.sin(angle)
  return rotate_matrix

def apply_rotate_matrix(PE, rotate_matrix):
  r = list()
  for (v1, v2, vc) in PE:
    v1p, v1c = v1
    v1pn = np.array(v1p) - np.ones(num_of_dims())*0.5
    v1p = list(np.dot(v1pn, rotate_matrix))
    rv1 = (v1p, v1c)
    v2p, v2c = v2
    v2pn = np.array(v2p) - np.ones(num_of_dims())*0.5
    v2p = list(np.dot(v2pn, rotate_matrix))
    rv2 = (v2p, v2c)
    r.append((rv1, rv2, vc))
  return r

def project_point(P):
  """Проецируем оставляем только первые 2 координаты"""
  r = list()
  for (v1, v2, vc) in P:
    r.append((v1[0][:2], v2[0][:2], vc))
  return r

def distance(v, f = 10):
  S = sum([x*x for x in v] - v[2]*v[2] +(v[2] - 1 - f)*(v[2] - 1 - f))
  return math.sqrt(S)

def project_point_perspective(P, f = 1):
  """Проецируем с перспективой"""
  r = list()
  for (v1, v2, vc) in P:
    v1p = v1[0]
    v2p = v2[0]
    d1 = distance(v1p, f)
    d2 = distance(v2p, f)
    v1p[0] = v1p[0]/(1 + f + d1)
    v1p[1] = v1p[1]/(1 + f + d1)
    v2p[0] = v2p[0]/(1 + f + d2)
    v2p[1] = v2p[1]/(1 + f + d2)
    r.append((v1p[:2], v2p[:2], vc))
  return r

def scaler(PE, window, margin = 10):
  r = list()
  for (v1, v2, vc) in PE:
    r.append(v1)
    r.append(v2)

  x0 = min([x[0] for x in r])
  x1 = max([x[0] for x in r])
  y0 = min([x[1] for x in r])
  y1 = max([x[1] for x in r])
  xsc = (window[0] - margin*2)/(x1-x0)
  ysc = (window[1] - margin*2)/(y1-y0)
  sc = min(xsc, ysc)
  xsh = (window[0] - (x1-x0) * sc)/2 - x0*sc
  ysh = (window[1] - (y1-y0) * sc)/2 - y0*sc
  res = list()
  for (v1, v2, vc) in PE:
    res.append(([v1[0]*sc + xsh, v1[1]*sc + ysh], [v2[0]*sc + xsh, v2[1]*sc + ysh], vc))

  return(res)

def paint(angles, E, window, winsize):
  n = 0
  rotate_matrix = np.eye(num_of_dims())
  for i in range(0, num_of_dims()):
    for j in range(2):
      if i > j:
        print(i, j, n, angles[n])
        rotate_matrix = np.dot(rotate_matrix, create_rotate_matrix((i,j), angles[n]))
        n +=1

  E = apply_rotate_matrix(E, rotate_matrix)
  #PE = project_point(E)
  PE = project_point_perspective(E)
  PS = scaler(PE, winsize)
  #draw a line - see http://www.pygame.org/docs/ref/draw.html for more
  color = (255, 255, 255)
  window.fill(0)
  for e in PS:
    pygame.draw.line(window, colorizer(e[2]), tuple(e[0]), tuple(e[1]))
  pygame.display.flip()

def random_angles():
  angles = np.random.rand(num_of_dims() * (num_of_dims() - 1)/2)
  return angles * math.pi/4

def reset_angles():
  angles = np.zeros(num_of_dims() * (num_of_dims()-1)/2)
  #angles[0] = math.pi/4
  #angles[1] = -math.acos(1/math.sqrt(3))
  #angles[2] = 0
  #angles[3] = 0
  #angles[4] = 0.38759668665518054
  #angles[4] = 0.8187562376025612
  #angles[4] = -math.acos(1/math.sqrt(3))
  return angles

def main():
  angles = reset_angles()
  E = get_eges(num_of_dims())
  winsize = (640, 480)
  pygame.init()
  window = pygame.display.set_mode(winsize)
  paint(angles, E, window, winsize)

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit(0)
      if event.type == pygame.KEYDOWN:
        key = pygame.key.get_pressed()
        if any([key[x] for x in range(48,58)]):
          index = [key[x] for x in range(48,58)].index(1)
          angles[index] += 0.1
          paint(angles, E, window, winsize)
        if key[pygame.K_r]:
          angles = reset_angles()
          paint(angles, E, window, winsize)
        if key[pygame.K_x]:
          angles = random_angles()
          paint(angles, E, window, winsize)
        if key[pygame.K_PLUS]:
          pass
        if key[pygame.K_MINUS]:
          pass
        if key[pygame.K_ESCAPE]:
          sys.exit(0)

#    angles = angles + math.pi/180
#    paint(angles, E, window, winsize)
#    pygame.time.delay(100)

if __name__ == "__main__":
  main()
