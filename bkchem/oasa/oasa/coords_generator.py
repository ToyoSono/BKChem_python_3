#--------------------------------------------------------------------------
#     This file is part of OASA - a free chemical python library
#     Copyright (C) 2003-2008 Beda Kosata <beda@zirael.org>

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     Complete text of GNU GPL can be found in the file gpl.txt in the
#     main directory of the program

#--------------------------------------------------------------------------


from math import pi, sqrt, sin, cos
from . import geometry
from . import misc

import warnings

class coords_generator:

  def __init__( self, bond_length=1):
    self.bond_length = bond_length


  # -- collision-aware placement helpers ------------------------------
  # The generator grows the drawing atom by atom and historically never
  # looked at the atoms placed already, so a chain could be drawn
  # exactly back over an earlier part of the molecule (atoms landing
  # at distance 0.0 from each other, looking fused in the drawing) and
  # a ring could be placed on top of another fragment. The helpers
  # below score a candidate placement by the crossings it would create
  # and by its clearance from the placed atoms; the placement code
  # uses them to take the mirrored alternative when that is clearly
  # better. The original choice is kept unless the alternative wins
  # by a margin, so layouts that were already good do not change.

  def _clearance( self, x, y, exclude):
    """distance from (x, y) to the closest placed atom not in exclude"""
    best = None
    for a in self.mol.vertices:
      if a.x is None or a.y is None or a in exclude:
        continue
      d = sqrt( (a.x - x) ** 2 + (a.y - y) ** 2)
      if best is None or d < best:
        best = d
    return best if best is not None else 9e9


  def _count_crossings( self, x1, y1, x2, y2, exclude):
    """how many placed bonds the segment (x1,y1)-(x2,y2) would cross;
    bonds touching an atom in exclude do not count"""
    def side( ax, ay, bx, by, px, py):
      v = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
      if v > 0:
        return 1
      if v < 0:
        return -1
      return 0
    count = 0
    for e in self.mol.edges:
      a1, a2 = e.vertices
      if a1.x is None or a2.x is None or a1 in exclude or a2 in exclude:
        continue
      s1 = side( x1, y1, x2, y2, a1.x, a1.y)
      s2 = side( x1, y1, x2, y2, a2.x, a2.y)
      if s1 == 0 or s2 == 0 or s1 == s2:
        continue
      s3 = side( a1.x, a1.y, a2.x, a2.y, x1, y1)
      s4 = side( a1.x, a1.y, a2.x, a2.y, x2, y2)
      if s3 != 0 and s4 != 0 and s3 != s4:
        count += 1
    return count


  def _better_placement( self, score_a, score_b):
    """scores are (crossings, clearance); the alternative (b) wins
    with fewer crossings, or with equal crossings and clearly more
    clearance - but never when it would itself end in a close
    approach to a placed atom"""
    if score_b[0] != score_a[0]:
      return (score_b[0] < score_a[0]
              and score_b[1] >= 0.45 * self.bond_length
              and score_b[1] >= score_a[1] - 0.3 * self.bond_length)
    return score_b[1] > score_a[1] + 0.25 * self.bond_length


  def _walk_positions( self, gen, start, count):
    """the positions apply_gen_to_atoms() would produce, as a list"""
    x, y = start.x, start.y
    out = []
    for i in range( count):
      a = next( gen)
      x += self.bond_length * cos( a)
      y += self.bond_length * sin( a)
      out.append( (x, y))
    return out


  def _walk_score( self, walk, start, ring):
    """(crossings, clearance) of a ring walk starting at start"""
    crossings = 0
    clearance = None
    px, py = start.x, start.y
    prev = start
    exclude = [start] + list( ring)
    for (x, y), a in zip( walk, ring):
      crossings += self._count_crossings( px, py, x, y, (prev, a))
      c = self._clearance( x, y, exclude)
      if clearance is None or c < clearance:
        clearance = c
      px, py = x, y
      prev = a
    # the bond closing the ring back to start
    crossings += self._count_crossings( px, py, start.x, start.y, (prev, start))
    return (crossings, clearance if clearance is not None else 9e9)

  def calculate_coords( self, mol, bond_length=0, force=0):
    """the bond_length (when given) sets the self.bond_length,
    if bond_length == -1 we suppose that there is already part of the molecule containing
    coords and we calculate the bond_length from it;
    force says if we should recalc all coords"""
    processed = []
    self.mol = mol
    # stereochemistry info
    self.stereo = {}
    for st in self.mol.stereochemistry:
      if st.__class__.__name__ == "cis_trans_stereochemistry":
        for a in (st.references[0],st.references[-1]):
          self.stereo[a] = self.stereo.get( a, []) + [st]
    # at first we have a look if there is already something with coords
    atms = set( [a for a in mol.vertices if a.x != None and a.y != None])
    # then we check if they are in a continuos block but not the whole molecule
    # (in this case we regenerate all the coords if force, otherwise exit)
    if len( atms) == len( mol.vertices) and not force:
      return 
    elif not force and atms and not len( atms) == len( mol.vertices):
      # this is here just to setup the molecule well
      self.rings = mol.get_smallest_independent_cycles()
      # it is - we can use it as backbone
      sub = mol.get_new_induced_subgraph( atms, mol.vertex_subgraph_to_edge_subgraph( atms))
      subs = [comp for comp in sub.get_connected_components()]
      if len( subs) == 1:
        backbone = atms
      else:
        # we should not be here, but when yes than we have to solve it
        maxlength = max( map( len, subs))
        backbone = [su for su in subs if len( su) == maxlength][0]
        # we have to set the coords to None (for sure)
        for sub in subs:
          if sub != backbone:
            for a in sub:
              a.x = None
              a.y = None
      # now we check if we have to calculate bond_length from the backbone
      if bond_length < 0:
        bls = []
        for b in mol.vertex_subgraph_to_edge_subgraph( backbone):
          a1, a2 = b.vertices
          bls.append( sqrt( (a1.x-a2.x)**2 + (a1.y-a2.y)**2))
        self.bond_length = sum( bls) / len( bls)
      elif bond_length == 0:
        pass
      else:
        self.bond_length = bond_length
      # at last we have to remove rings that have coords from the self.rings
      for ring in self.rings[:]:
        if backbone >= ring:
          self.rings.remove( ring)
    else:
      if force:
        for a in self.mol.vertices:
          a.x = None
          a.y = None
      if bond_length > 0:
        # here we must have bond_length > 0
        self.bond_length = bond_length
      # we create a backbone, it is either one of the rings or
      # the longest chain in case of acyclic molecule
      if mol.contains_cycle():
        # ring
        self.rings = mol.get_smallest_independent_cycles()
        # find the most crowded ring
        jmax = 0
        imax = 0
        for i, ring in enumerate( self.rings):
          j = 0
          for r in self.rings:
            if r != ring and r & ring:
              j += 1
          if j > jmax:
            jmax = j
            imax = i
        #
        backbone = self.rings.pop(imax)
        gcoords = gen_ring_coords( len( backbone), side_length=self.bond_length)
        for v in mol.sort_vertices_in_path( backbone):
          v.x, v.y = next(gcoords)
        processed += backbone
        processed += self.process_all_anelated_rings( backbone)
      elif len( mol.vertices) == 1:
        a = mol.vertices[0]
        a.x, a.y, a.z = 0, 0, 0
        backbone = [a]
      else:
        # chain - we process 2 atoms as backbone and leave the rest for the code
        a1 = self.mol.vertices[0]
        a2 = a1.neighbors[0]
        a1.x, a1.y = 0, 0
        a2.x, a2.y = self.bond_length, 0
        backbone = [a1,a2]
        self.rings = []
    processed += backbone
    self._continue_with_the_coords( mol, processed=processed)
    for v in mol.vertices:
      if v.z == None:
        v.z = 0

  def _continue_with_the_coords( self, mol, processed=[]):
    """processes the atoms in circles around the backbone (processed) until all is done"""
    while processed:
      new_processed = []
      for v in processed:
        if len( [o for o in self.mol.vertices if o.x == None]) == 0:
          # its all done
          return
        # look if v is part of a ring
        ring = None
        for r in self.rings:
          if v in r:
            ring = r
            break
        if not ring:
          # v is not in a ring - we can continue
          new_processed += self.process_atom_neigbors( v)
        else:
          # v is in ring so we process the ring
          if len( processed) > 1 and mol.defines_connected_subgraph_v( processed) and set( processed) <= ring:
            new_processed += self.process_all_anelated_rings( processed)
          else:
            self.rings.remove( ring)
            ring = mol.sort_vertices_in_path( ring, start_from=v)
            ring.remove( v)
            d = [a for a in v.get_neighbors() if a.x != None and a.y != None][0] # should always work
            ca = geometry.clockwise_angle_from_east( v.x-d.x, v.y-d.y)
            size = len( ring)+1
            da = deg_to_rad( 180 -180*(size-2)/size)
            gcoords = gen_angle_stream( da, start_from=ca-pi/2+da/2)
            # the ring can equally well be drawn mirrored to the other
            # side of the bond it grows from; take the mirror when it
            # is clearly freer instead of placing the ring on top of
            # an already drawn fragment
            walk = self._walk_positions( gcoords, v, len( ring))
            gcoords = gen_angle_stream( -da, start_from=ca+pi/2-da/2)
            walk2 = self._walk_positions( gcoords, v, len( ring))
            if self._better_placement( self._walk_score( walk, v, ring),
                                       self._walk_score( walk2, v, ring)):
              walk = walk2
            for a, (x, y) in zip( ring, walk):
              a.x, a.y = x, y
            ring.append( v)
            new_processed += ring
            new_processed += self.process_all_anelated_rings( ring)
      processed = new_processed

  def process_all_anelated_rings( self, base):
    out = []
    to_go = []
    b = set( base)
    for r in self.rings:
      if r & b:
        to_go.append( r)
    for r in to_go:
      out += self.process_one_anelated_ring( base)
    if out:
      for b in to_go:
        out += self.process_all_anelated_rings( b)
    return out
      

  def process_one_anelated_ring( self, base):
    mol = self.mol
    out = []
    ring = None
    b = set( base)
    for r in self.rings:
      if r & b:
        ring = r
        break
    if ring:
      self.rings.remove( ring)
      inter = b & ring
      to_go = [a for a in ring if a.x == None or a.y == None]
      if len( ring) - len( to_go) == len( inter):
        out += self._process_simply_anelated_ring( ring, base)
      else:
        out += self._process_multi_anelated_ring( ring)
    return out


  def process_atom_neigbors( self, v):
    def get_angle_at_side( v, d, d2, relation, attach_angle):
      if attach_angle == 180:
        # shortcut
        return attach_angle
      side = geometry.on_which_side_is_point( (d.x,d.y,v.x,v.y), (d2.x,d2.y))
      an = angle + deg_to_rad( attach_angle)
      x = v.x + self.bond_length*cos( an)
      y = v.y + self.bond_length*sin( an)
      if relation*side == geometry.on_which_side_is_point( (d.x,d.y,v.x,v.y), (x,y)):
        return attach_angle
      else:
        return -attach_angle
      
    to_go = [a for a in v.get_neighbors() if a.x == None or a.y == None]
    done = [a for a in v.get_neighbors() if a not in to_go]
    if len( done) == 1 and (len( to_go) == 1 or len( to_go) == 2 and [1 for _t in to_go if _t in self.stereo]):
      # only simple non-branched chain or branched with stereo
      d = done[0]
      if len( to_go) == 1:
        t = to_go[0]
      else:
        t = [_t for _t in to_go if _t in self.stereo][0]
      # decide angle
      angle_to_add = 120
      bond = v.get_edge_leading_to( t)
      # triple bonds
      if 3 in [_e.order for _e in v.get_neighbor_edges()]:
        angle_to_add = 180
      # cumulated double bonds
      if bond.order == 2:
        _b = v.get_edge_leading_to( d)
        if _b.order == 2:
          angle_to_add = 180
      angle = geometry.clockwise_angle_from_east( d.x-v.x, d.y-v.y)
      dns = d.get_neighbors()
      placed = False
      # stereochemistry (E/Z)
      if t in self.stereo:
        ss = [st for st in self.stereo[t] if not None in st.get_other_end( t).coords[:2]]
        if ss:
          st = ss[0] # we choose the first one if more are present
          d2 = st.get_other_end( t)
          # other is processed, we need to adapt
          relation = st.value == st.OPPOSITE_SIDE and -1 or 1
          angle_to_add = get_angle_at_side( v, d, d2, relation, angle_to_add)
          placed = True
      if not placed and len( dns) == 2:
        # to support the all trans of simple chains without stereochemistry
        d2 = (dns[0] == v) and dns[1] or dns[0]
        if d2.x != None and d2.y != None:
          angle_to_add = get_angle_at_side( v, d, d2, -1, angle_to_add)
      an = angle + deg_to_rad( angle_to_add)
      t.x = v.x + self.bond_length*cos( an)
      t.y = v.y + self.bond_length*sin( an)
      if not placed and len( [a for a in t.get_neighbors() if a.x is not None]) == 1:
        # the side was not dictated (no stereochemistry involved) and
        # the atom hangs on this one bond only: if the mirrored
        # direction is clearly freer, take it instead of drawing the
        # chain back over the part that is already placed
        an2 = 2 * angle - an
        x2 = v.x + self.bond_length * cos( an2)
        y2 = v.y + self.bond_length * sin( an2)
        score_a = (self._count_crossings( v.x, v.y, t.x, t.y, (v, t)),
                   self._clearance( t.x, t.y, (v, t)))
        score_b = (self._count_crossings( v.x, v.y, x2, y2, (v, t)),
                   self._clearance( x2, y2, (v, t)))
        if self._better_placement( score_a, score_b):
          t.x, t.y = x2, y2
      if len( to_go) > 1:
        self.process_atom_neigbors( v)
    else:
      # branched chain
      angles = [geometry.clockwise_angle_from_east( at.x-v.x, at.y-v.y) for at in done]
      angles.append( 2*pi + min( angles))
      angles.sort()
      angles.reverse()
      diffs = misc.list_difference( angles)
      i = diffs.index( max( diffs))
      angle = (angles[i] -angles[i+1]) / (len( to_go)+1)
      gcoords = gen_coords_from_stream( gen_angle_stream( angle, start_from=angles[i+1]+angle),
                                        length = self.bond_length)
      offsets = [next( gcoords) for a in to_go]
      if len( to_go) > 1:
        # the fan of directions inside the gap is the same whichever
        # end we start from, but which atom gets which direction is
        # not: prefer the assignment whose closest approach to the
        # placed atoms is clearly larger
        def fan_clearance( offs):
          worst = None
          for dx, dy in offs:
            c = self._clearance( v.x + dx, v.y + dy, [v] + list( to_go))
            if worst is None or c < worst:
              worst = c
          return worst if worst is not None else 9e9
        if fan_clearance( offsets[::-1]) > fan_clearance( offsets) + 0.25 * self.bond_length:
          offsets.reverse()
      for a, (dx, dy) in zip( to_go, offsets):
        a.x = v.x + dx
        a.y = v.y + dy
    return to_go


  def apply_gen_to_atoms( self, gen, atoms, start, bond_length=None):
    bl = bond_length or self.bond_length
    x, y = start.x, start.y
    for v in atoms:
      a = next(gen)
      x += bl*cos( a)
      y += bl*sin( a)
      v.x, v.y = x, y


  def _process_simply_anelated_ring( self, ring, base):
    out = []
    inter = [v for v in ring if v.x != None and v.y != None]
    if len( inter) == 1:
      # rings are connected via one atom
      v = inter.pop() # the atom of concatenation
      ring = self.mol.sort_vertices_in_path( ring, start_from=v)
      base_neighs = [a for a in v.get_neighbors() if a in base]
      if len( base_neighs) < 2:
        raise Exception("this should not happen")
      d1 = base_neighs[0] 
      d2 = base_neighs[1]
      ca1 = geometry.clockwise_angle_from_east( v.x-d1.x, v.y-d1.y)
      ca2 = geometry.clockwise_angle_from_east( v.x-d2.x, v.y-d2.y)
      ca = (ca1+ca2)/2
      if abs( ca1-ca2) < pi:
        ca += -pi/2
      else:
        ca += pi/2
      size = len( ring)
      da = deg_to_rad(180 -180.0*(size-2)/size)
      gcoords = gen_angle_stream( da, start_from=ca + da/2)
      ring.remove( v)
      # here we generate the coords
      self.apply_gen_to_atoms( gcoords, ring, v)
      ring.append( v)
      out += ring
    elif len( inter) == 2:
      # there are two atoms common to the rings
      v1, v2 = inter # the atoms of concatenation
      ring = self.mol.sort_vertices_in_path( ring, start_from=v1)
      ring.remove( v1)
      ring.remove( v2)
      if not v1 in ring[0].get_neighbors():
        v1, v2 = v2, v1
      side = sum( [geometry.on_which_side_is_point((v1.x,v1.y,v2.x,v2.y),(v.x,v.y)) for v in base])
      if not side:
        warnings.warn( "this should not happen")
      ca = geometry.clockwise_angle_from_east( v1.x-v2.x, v1.y-v2.y)
      size = len( ring)+2
      da = deg_to_rad(180 -180.0*(size-2)/size)
      if side > 0:
        da = -da
      gcoords = gen_angle_stream( da, start_from=ca+da)
      self.apply_gen_to_atoms( gcoords, ring, v1)
      ring.append( v1)
      ring.append( v2)
      out += ring
    else:
      # there are more than 2 atoms common
      if len( ring) == len( base):
        out += self._process_multi_anelated_ring( ring, angle_shift=15)
        #raise( "i don't how to handle this yet")
      else:
        out += self._process_multi_anelated_ring( ring)
    return out

  def _process_multi_anelated_ring( self, ring, angle_shift=0):
    out = []
    to_go = [v for v in ring if v.x == None or v.y == None]
    if not to_go:
      # it was all already done
      return []
    back = [v for v in ring if v.x != None and v.y != None]
    sorted_back = self.mol.sort_vertices_in_path( back)
    if not sorted_back:
      # the already set atoms are not in one path - we have to process it "per partes"
      # it should not happen with the construction method we use
      raise Exception("I am not able to handle this, it should normaly not "
		      "happen. Please send me the input.")
    else:
      v1 = sorted_back[0]
      v2 = sorted_back[-1]
      v3 = sorted_back[1]
      to_go = self.mol.sort_vertices_in_path( to_go)
      if v1 not in to_go[0].get_neighbors():
        v1, v2 = v2, v1
      blocked_angle = sum_of_ring_internal_angles( len( back))
      overall_angle = sum_of_ring_internal_angles( len( ring))
      da = optimal_ring_iternal_angle( len( ring))  # internal angle
      # if there are 2 rings of same size inside each other, we need to use the angle_shift
      if angle_shift:
        da += 2*angle_shift/(len( to_go))
      ca = deg_to_rad( 180-(overall_angle - blocked_angle - len( to_go) * da + angle_shift)/2)  # connection angle
      side = sum( [geometry.on_which_side_is_point( (v1.x,v1.y,v2.x,v2.y),(v.x,v.y)) for v in back if v != v1 and v != v2])
      # we need to make sure that the ring is drawn on the right side
      if side > 0:
        ca = -ca
      ca += geometry.clockwise_angle_from_east( v1.x-v2.x, v1.y-v2.y)
      da = 180-da  # for drawing we use external angle
      # we must ensure that the ring will progress towards the second end
      if geometry.on_which_side_is_point( (v1.x,v1.y,v3.x,v3.y),(v2.x,v2.y)) < 0:
        da = -da
      # dry run to see where we get
      gcoords = gen_angle_stream( deg_to_rad( da), start_from= ca)
      x, y = v1.x, v1.y
      for i in range( len( to_go) +1):
        a = next(gcoords)
        x += self.bond_length*cos( a)
        y += self.bond_length*sin( a)
      # end of dry run, we can scale the bond_length now
      length = geometry.line_length( (v1.x,v1.y,v2.x,v2.y))
      real_length = geometry.line_length( (v1.x,v1.y,x,y))
      bl = self.bond_length * length / real_length
      gcoords = gen_angle_stream( deg_to_rad( da), start_from= ca)
      # and here we go
      self.apply_gen_to_atoms( gcoords, to_go, v1, bond_length=bl)
      out += to_go
    return out

def sum_of_ring_internal_angles( size):
  return (size-2)*180

def optimal_ring_iternal_angle( size, angle_shift=0):
  return sum_of_ring_internal_angles( size)/size

def gen_ring_coords( size, side_length=1):
  coords = gen_coords_from_deg_stream( gen_angle_stream( 180 -180.0*(size-2)/size),
                                       length=side_length)
  x , y = 0, 0
  for i in range( size):
    dx, dy = next(coords)
    x += dx
    y += dy
    yield x,y


def gen_angle_stream( angle, start_from=0, alternate=0):
  yield start_from
  if alternate:
    while 1:
      yield angle
      yield -angle
  else:
    a = start_from
    while 1:
      a += angle
      yield a

def gen_coords_from_deg_stream( stream, length=1):
  for a in stream:
    ang = deg_to_rad( a)
    yield ( length*cos( ang), length*sin( ang))

def gen_coords_from_stream( stream, length=1):
  for a in stream:
    yield ( length*cos( a), length*sin( a))
    
def deg_to_rad( deg):
  return pi*deg/180

def rad_to_deg( rad):
  return 180*rad/pi




def show_mol( mol):
  from Tkinter import Tk, Canvas, Frame

  app = Tk()
  app.title( "oasa")

  mainFrame = Frame( app)
  mainFrame.pack( fill='both', expand=1)

  paper = Canvas( mainFrame, width=640, height=480, background="white", closeenough=5)
  paper.pack()

  xmin, xmax, ymin, ymax = None,None,None,None
  for a in mol.vertices:
    if xmin == None or a.x < xmin:
      xmin = a.x
    if xmax == None or a.x > xmax:
      xmax = a.x
    if ymin == None or a.y < ymin:
      ymin = a.y
    if ymax == None or a.y > ymax:
      ymax = a.y

  dx = xmax-xmin
  dy = ymax-ymin
  #print "dx", dy, ymax, ymin
  range = min( (600.0/dx, 450.0/dy))/2
  xp = 640-range*dx
  yp = 480-range*dy
  xtrans = lambda xx: range*(xx - xmin)+xp/2
  ytrans = lambda xx: range*(xx - ymin)+yp/2

  for b in mol.edges:
    a1, a2 = b.vertices
    x1 = xtrans( a1.x)
    x2 = xtrans( a2.x)
    y1 = ytrans( a1.y)
    y2 = ytrans( a2.y)
    paper.create_line( x1, y1, x2, y2, fill='black')
    paper.create_text( (x1+x2)/2, (y1+y2)/2, text=str( b.order), fill="#F00")
  for v in mol.vertices: 
    x = xtrans( v.x)
    y = ytrans( v.y)
    #paper.create_oval( x-5, y-5, x+5, y+5, fill="#0F0")
    paper.create_text( x, y, text=v.symbol, fill="#0F0")
  app.mainloop()


def calculate_coords( mol, bond_length=0, force=0):
  g = coords_generator()
  g.calculate_coords( mol, bond_length=bond_length, force=force)



##################################################
# DEMO

if __name__ == '__main__':

  from . import smiles
  from .molecule import molecule

  #sm = "CP(c1ccccc1)(c2ccccc2)c3ccccc3"
  #sm = 'C1CC2C1CCCC3C2CC(CCC4)C4C3'
  #sm = "C\C=C/CC#CCCCC\C=C=C=C/CC"
  sm = "C/C(Cl)=C(\O)C"
  #sm = "C1CCC1C/C=C\CCCCC"
  #sm = "C25C1C3C5C4C2C1C34"
  #sm = 'C1CC2CCC1CC2'
  #sm = 'C1CC5(CC(C)CC5)CC(C)C12CC(CC(C(C)(C)CCCC)CCC)CC23C(CC)CC3'
  #sm = 'CCCC(C)(CCC)CCC(Cl)C(CCCCC)CCC(C)CCC'

  print("oasa::coords_generator DEMO")
  print("generating coords for following smiles")
  print("  %s" % sm)
 
  mol = smiles.text_to_mol( sm, calc_coords=False)

  import time
  #cg = coords_generator()
  t = time.time()
  calculate_coords( mol, force=1)
  print("generation time: %.3f ms" % ((time.time()-t)*1000))

  show_mol( mol)



##################################################
# TODO

# when an atom with degree 4 is created not as part of the backbone the neighbors are
#   organized in a square instead of the usual 120 deg between 2 and the rest on the other side

# triple bond should be linear

##################################################
