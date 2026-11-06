#--------------------------------------------------------------------------
#     This file is part of BKChem - a chemical drawing program
#     Copyright (C) 2002-2009 Beda Kosata <beda@zirael.org>

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

oasa_available = 1
try:
  from . import oasa
except ImportError:
  oasa_available = 0

from functools import reduce
from . import molecule
from . import bond
from . import atom

import math
import operator

from .singleton_store import Screen
from .oasa import transform3d


def read_smiles( text, paper):
  mol = oasa.smiles.text_to_mol( text)
  oasa.coords_generator.calculate_coords( mol, bond_length=1.0, force=1)
  m = oasa_mol_to_bkchem_mol( mol, paper)
  _apply_tetrahedral_stereochemistry( mol, m, _smiles_chiral_orders( text))
  return m

def mol_to_smiles( mol):
  m = bkchem_mol_to_oasa_mol( mol)
  m.remove_unimportant_hydrogens()
  _add_tetrahedral_stereochemistry_from_bonds( m)
  c = oasa.smiles.converter()
  text = c.mols_to_text([m])
  return text


# ==================================================
# wedge / hatch bonds -> tetrahedral stereochemistry
# (the reverse of _apply_tetrahedral_stereochemistry)
#
# The SMILES writer in oasa only emits '@' / '@@' from
# tetrahedral_stereochemistry objects on the molecule; it never
# looks at bond types, and detect_stereochemistry_from_coords()
# only detects cis/trans double bonds. A BKChem drawing therefore
# lost every wedge/hatch on Generate SMILES even though the same
# information survives a molfile export (which maps the bond type
# directly). The code below rebuilds the stereochemistry objects
# from the drawn bonds, using the same geometry the reader uses:
# a wedge lifts its wide end towards the viewer, a hatch pushes
# it away, and the rotation of the other three references as seen
# from the first one decides CLOCKWISE / ANTICLOCKWISE. A bond
# only speaks for the centre at its narrow end: a wedge shared
# with a neighbouring stereocentre is that centre's bond, not
# this one's (the molfile/RDKit reading of the same drawing
# agrees). The references are ordered the way oasa's own SMILES parser orders
# them (neighbours by atom index, an implicit hydrogen slotted in
# by the centre's index), so the writer's parity correction works
# exactly as it does for a parsed SMILES string. The value,
# however, is the rotation sign in Daylight (SMILES) neighbour
# order - the atom written before the centre, a bracket hydrogen,
# ring-closure partners, then the rest - which is what '@' /
# '@@' mean and what the reader's _smiles_chiral_orders recovers.
# The two orders agree except for ring centres, where the parser
# sorts a ring partner by atom index instead of counting it where
# its digit stands on the chiral atom; using the parser order for
# the sign would flip exactly those centres.

def _add_tetrahedral_stereochemistry_from_bonds( oasa_mol):
  from .oasa import stereochemistry
  index_of = {}
  for i, a in enumerate( oasa_mol.vertices):
    index_of[ id( a)] = i
  for v in list( oasa_mol.vertices):
    if v.symbol not in ('C', 'Si'):
      continue
    pairs = [(n, e) for e, n in v.get_neighbor_edge_pairs()]
    if len( pairs) not in (3, 4):
      continue
    if any( e.order != 1 or e.aromatic for _n, e in pairs):
      continue
    if not any( e.type in ('w', 'h') for _n, e in pairs):
      continue # a plain drawing specifies no configuration
    if oasa_mol.get_stereochemistry_by_center( v) is not None:
      continue
    implicit = False
    if len( pairs) == 3:
      if v.valency - v.occupied_valency < 1:
        continue # e.g. a charged centre with no free valency
      implicit = True
    elif v.valency != 4:
      continue
    # z of each neighbour: a wedge lifts its wide end (the bond's
    # second vertex) towards the viewer, a hatch pushes it away -
    # but only for the centre at the bond's narrow end (its first
    # vertex). A bond shared with another stereocentre belongs to
    # that centre: RDKit reads the same drawing from a molfile as
    # the original configuration, and counting the shared bond for
    # the wide-end centre as well flips that centre.
    lengths = []
    zs = {}
    for n, e in pairs:
      lengths.append( math.hypot( n.x - v.x, n.y - v.y))
      if e.type in ('w', 'h') and e.vertices[0] is v:
        zs[ id( n)] = 1.0 if e.type == 'w' else -1.0
      else:
        zs[ id( n)] = 0.0
    mean_length = sum( lengths) / len( lengths) or 1.0
    if not any( zs.values()):
      continue # the centre owns no wedge/hatch: a stereo bond
      # whose narrow end is the neighbour belongs to that
      # neighbour, and a flat drawing specifies no configuration
    if implicit:
      v.explicit_hydrogens = 1
    centre_idx = index_of[ id( v)]
    # references in the parser's order: neighbours by atom index,
    # an implicit hydrogen slotted in by the centre's index
    order_p = sorted( pairs, key=lambda p: index_of[ id( p[0])])
    refs = []
    inserted = False
    for n, _e in order_p:
      if implicit and not inserted \
         and index_of[ id( n)] > centre_idx:
        refs.append( stereochemistry.explicit_hydrogen())
        inserted = True
      refs.append( n)
    if implicit and not inserted:
      refs.append( stereochemistry.explicit_hydrogen())
    # the same references in Daylight (SMILES) order, for the sign:
    # the neighbour written before the centre, a bracket hydrogen,
    # ring-closure partners, then the rest in atom-index order. A
    # ring-closure partner is a ring-bond neighbour joined to the
    # centre by the ring's closure edge: in a SMILES string the
    # digit is opened at the first-written ring atom and closed at
    # the last-written one, so the closure edge joins the lowest-
    # and highest-index atoms of its ring (found here as the
    # shortest cycle through the bond). The other ring bonds of
    # the centre are ordinary traversal bonds and stay in the
    # rest, in index order.
    def _is_closure_edge( a, b, edge):
      if oasa_mol.is_edge_a_bridge( edge):
        return False
      # shortest path from a to b not using this edge
      seen = { id( a): None}
      queue = [a]
      while queue:
        cur = queue.pop( 0)
        if cur is b:
          break
        for e, n in cur.get_neighbor_edge_pairs():
          if e is edge or id( n) in seen:
            continue
          seen[ id( n)] = cur
          queue.append( n)
      if id( b) not in seen:
        return False
      idxs = [index_of[ id( b)]]
      cur = b
      while cur is not a:
        idxs.append( index_of[ id( cur)])
        cur = seen[ id( cur)]
      idxs.append( index_of[ id( a)])
      return set( (min( idxs), max( idxs))) == set(
        (index_of[ id( a)], index_of[ id( b)]))
    by_idx = dict( (index_of[ id( n)], (n, e)) for n, e in pairs)
    before = [i for i in by_idx if i < centre_idx]
    prev = by_idx[ max( before)][0] if before else None
    partners = []
    rest = []
    for i in sorted( by_idx):
      n, e = by_idx[i]
      if n is prev:
        continue
      try:
        if _is_closure_edge( v, n, e):
          partners.append( n)
          continue
      except Exception:
        pass
      rest.append( n)
    order_d = []
    if prev is not None:
      order_d.append( prev)
    if implicit:
      order_d.append( stereochemistry.explicit_hydrogen())
    order_d.extend( partners)
    order_d.extend( rest)
    points = []
    real = []
    for r in order_d:
      if isinstance( r, stereochemistry.explicit_hydrogen):
        points.append( None)
      else:
        points.append( (r.x - v.x, -(r.y - v.y)))
        real.append( len( points) - 1)
    zlist = [0.0, 0.0, 0.0, 0.0]
    for i, r in enumerate( order_d):
      if not isinstance( r, stereochemistry.explicit_hydrogen):
        zlist[i] = zs[ id( r)] * mean_length
    implicit_idx = [i for i in range( 4) if points[i] is None]
    if len( implicit_idx) > 1 or len( order_d) != 4:
      continue
    sign = _seen_rotation_sign(
      _complete_points( points, real, implicit_idx, zlist,
                         mean_length))
    if sign == 0.0:
      continue # degenerate layout, cannot decide
    value = stereochemistry.tetrahedral_stereochemistry.ANTICLOCKWISE \
      if sign > 0 else stereochemistry.tetrahedral_stereochemistry.CLOCKWISE
    st = stereochemistry.tetrahedral_stereochemistry(
      center=v, value=value, references=refs)
    oasa_mol.add_stereochemistry( st)


def read_inchi( text, paper):
  mol = oasa.inchi.text_to_mol( text, calc_coords=1, include_hydrogens=False)
  #oasa.coords_generator.calculate_coords( mol, bond_length=1.0, force=1)
  m = oasa_mol_to_bkchem_mol( mol, paper)
  return m
  
def mol_to_inchi( mol, program):
  m = bkchem_mol_to_oasa_mol( mol)
  # we do not use mol_to_text because generate_inchi_and_inchikey returns extra warning messages
  _inchi, _key, _warnings = oasa.inchi.generate_inchi_and_inchikey( m, program=program, fixed_hs=False)
  return (_inchi, _key, _warnings)


def read_molfile( file, paper):
  mol = oasa.molfile.file_to_mol( file)
  if not mol.is_connected():
    mols = mol.get_disconnected_subgraphs()
    return [oasa_mol_to_bkchem_mol( mol, paper) for mol in mols]
  else:
    return [oasa_mol_to_bkchem_mol( mol, paper)]


def write_molfile( mol, file):
  m = bkchem_mol_to_oasa_mol( mol)
  oasa.molfile.mol_to_file( m, file)

  

# ==================================================
# OASA -> BKCHEM

def oasa_mol_to_bkchem_mol( mol, paper):
  m = molecule.molecule( paper)
  if None in reduce( operator.add, [[a.x, a.y] for a in mol.atoms], []):
    calc_position = 0
  else:
    calc_position = 1
    
  minx = None
  maxx = None
  miny = None
  maxy = None
  # atoms
  for a in mol.vertices:
    a2 = oasa_atom_to_bkchem_atom( a, paper, m)
    m.insert_atom( a2)
    if calc_position:
      # data for rescaling
      if not maxx or a2.x > maxx:
        maxx = a2.x
      if not minx or a2.x < minx:
        minx = a2.x
      if not miny or a2.y < miny:
        miny = a2.y
      if not maxy or a2.y > maxy:
        maxy = a2.y
  # bonds
  bond_lengths = []
  for b in mol.edges:
    b2 = oasa_bond_to_bkchem_bond( b, paper)
    aa1, aa2 = b.vertices
    atom1 = m.atoms[ mol.vertices.index( aa1)]
    atom2 = m.atoms[ mol.vertices.index( aa2)]
    m.add_edge( atom1, atom2, b2)
    b2.molecule = m
    if calc_position:
      bond_lengths.append( math.sqrt( (b2.atom1.x-b2.atom2.x)**2 + (b2.atom1.y-b2.atom2.y)**2))
  # rescale (a single atom has no bonds, so there is nothing to
  # rescale - without this guard Read SMILES of "C" or "O" crashed
  # with ZeroDivisionError)
  if calc_position and bond_lengths:
    bl = sum( bond_lengths) / len( bond_lengths)
    scale = Screen.any_to_px( paper.standard.bond_length) / bl
    movex = (maxx+minx)/2
    movey = (maxy+miny)/2
    trans = transform3d.transform3d()
    trans.set_move( -movex, -movey, 0)
    trans.set_scaling( scale)
    trans.set_move( 320, 240, 0)
    for a in m.atoms:
      a.x, a.y, a.z = trans.transform_xyz( a.x, a.y, a.z)
  return m


def _smiles_chiral_orders( text):
  """Neighbour order of every bracketed chiral atom in a SMILES
  string, as {atom index: [neighbour atom indices, with 'H' for a
  hydrogen written inside the bracket]}.

  The order follows the SMILES text: the atom the chiral atom is
  attached to, then a bracket hydrogen, then ring-closure partners
  in the order their digits appear on the chiral atom itself, then
  the atoms that follow (branches, then the continuation). The
  ring-closure position matters: the Daylight definition (and
  RDKit) count a ring partner where its digit stands on the chiral
  atom, not where the partner itself is written, so the plain atom
  order that oasa's stereochemistry objects use is wrong for ring
  stereocentres. Returns {} when the string cannot be scanned."""
  neighbours = {}
  had_parent = {}
  chiral = set()
  bracket_h = set()
  ring_open = {}
  stack = []
  prev = None
  current = None
  try:
    i = 0
    n = len( text)
    while i < n:
      ch = text[i]
      if ch == '[':
        j = text.index( ']', i)
        spec = text[i+1:j]
        idx = len( neighbours)
        neighbours[idx] = []
        k = 0
        while k < len( spec) and spec[k].isdigit():
          k += 1
        if k + 1 < len( spec) and spec[k+1].islower() \
           and not spec[k].islower():
          k += 2
        elif k < len( spec):
          k += 1
        rest = spec[k:]
        if '@' in rest:
          chiral.add( idx)
        # a hydrogen written in the bracket (H, H2, ...)
        hpos = rest.find( 'H')
        if hpos != -1 and (hpos == 0 or not rest[hpos-1].isalpha()):
          bracket_h.add( idx)
        had_parent[idx] = prev is not None
        if prev is not None:
          neighbours[idx].append( prev)
          neighbours[prev].append( idx)
        prev = current = idx
        i = j + 1
      elif ch == '(':
        stack.append( prev)
        i += 1
      elif ch == ')':
        prev = stack.pop()
        current = prev
        i += 1
      elif ch == '.':
        prev = current = None
        i += 1
      elif ch.isdigit() or ch == '%':
        if ch == '%':
          digit = text[i+1:i+3]
          i += 3
        else:
          digit = ch
          i += 1
        if current is None:
          continue
        if digit in ring_open:
          partner = ring_open.pop( digit)
          neighbours[current].append( partner)
          lst = neighbours[partner]
          lst[lst.index( ('ring', digit))] = current
        else:
          ring_open[digit] = current
          neighbours[current].append( ('ring', digit))
      elif ch.isupper() or ch in 'bcnops' or ch == '*':
        if text[i:i+2] in ('Cl', 'Br', 'se'):
          i += 2
        else:
          i += 1
        idx = len( neighbours)
        neighbours[idx] = []
        had_parent[idx] = prev is not None
        if prev is not None:
          neighbours[idx].append( prev)
          neighbours[prev].append( idx)
        prev = current = idx
      else:
        i += 1
  except Exception:
    return {}
  orders = {}
  for idx in chiral:
    if idx >= len( neighbours):
      continue
    entries = [e for e in neighbours[idx] if not isinstance( e, tuple)]
    if len( entries) != len( neighbours[idx]):
      continue # an unclosed ring digit - should not happen
    if idx in bracket_h:
      entries.insert( 1 if had_parent.get( idx) else 0, 'H')
    orders[idx] = entries
  return orders


def _ring_edge_ids( mol):
  """ids of the bonds that belong to a ring: a bond is in a ring
  when its two atoms stay connected after removing it (it is not a
  bridge). Deliberately not based on the cycle lists oasa returns,
  whose atom order varies between runs."""
  ids = set()
  for e in mol.bonds:
    u, v = e.atom1, e.atom2
    seen = set([id( u)])
    stack = [u]
    found = False
    while stack and not found:
      a = stack.pop()
      for e2 in a.neighbor_edges:
        if e2 is e:
          continue
        for w in e2.vertices:
          if w is None or w is a:
            continue
          if w is v:
            found = True
            break
          if id( w) not in seen:
            seen.add( id( w))
            stack.append( w)
        if found:
          break
    if found:
      ids.add( id( e))
  return ids


# ==================================================
# SMILES tetrahedral stereochemistry -> wedge / hatch bonds
#
# oasa keeps the @ / @@ information from a SMILES string as
# tetrahedral_stereochemistry objects on the parsed molecule (center,
# four references in SMILES order, value CLOCKWISE / ANTICLOCKWISE as
# seen looking from the first reference towards the center), but
# nothing turned it into bond types, so it was silently dropped by the
# conversion above and every bond came out plain. The code below
# picks, for each stereocenter, one bond to draw as a wedge ('w',
# neighbour in front of the paper) or hatch ('h', neighbour behind
# it) so that the drawing encodes the same configuration. Every
# candidate is checked geometrically, so the result does not depend
# on how the coordinate generator happened to lay the atoms out.

def _apply_tetrahedral_stereochemistry( oasa_mol, bkchem_mol,
                                        chiral_orders=None):
  index_of = {}
  for i, a in enumerate( oasa_mol.vertices):
    index_of[ id( a)] = i
  # for the depiction choice below: which bonds belong to a ring
  # (they should stay plain whenever an outside bond can carry the
  # wedge instead, so rings keep their flat, forced-planar look) and
  # which atoms are stereocenters themselves (a wedge on a bond
  # between two centers is the least readable choice)
  ring_edges = _ring_edge_ids( bkchem_mol)
  center_atoms = set()
  for st in oasa_mol.stereochemistry:
    if st.__class__.__name__ == "tetrahedral_stereochemistry" \
       and id( st.center) in index_of:
      center_atoms.add( bkchem_mol.atoms[ index_of[ id( st.center)]])
  for st in oasa_mol.stereochemistry:
    if st.__class__.__name__ != "tetrahedral_stereochemistry":
      continue
    if st.value not in (1, 2): # CLOCKWISE / ANTICLOCKWISE
      continue
    if id( st.center) not in index_of or len( st.references) != 4:
      continue
    center_idx = index_of[ id( st.center)]
    center = bkchem_mol.atoms[ center_idx]
    # the four references in SMILES order; oasa orders them by atom
    # index, which misplaces ring-closure partners (see
    # _smiles_chiral_orders), so prefer the scanned order when it
    # names the same neighbours
    ref_atoms = None
    if chiral_orders and center_idx in chiral_orders:
      entries = chiral_orders[ center_idx]
      oasa_refs = set( index_of[ id( r)] for r in st.references
                       if id( r) in index_of)
      if len( entries) == 4 \
         and set( e for e in entries if e != 'H') == oasa_refs:
        ref_atoms = [ bkchem_mol.atoms[e] if e != 'H' else None
                      for e in entries]
    if ref_atoms is None:
      ref_atoms = [ bkchem_mol.atoms[ index_of[ id( r)]]
                    if id( r) in index_of else None
                    for r in st.references]
    # positions of the four references relative to the center; canvas
    # y grows downwards, so negate it to work in the frame a reader
    # of the drawing sees
    refs = []   # bkchem atoms; None for an implicit hydrogen
    points = [] # (x, y) relative to the center; None until placed
    real = []
    for a in ref_atoms:
      refs.append( a)
      if a is not None:
        points.append( (a.x - center.x, -(a.y - center.y)))
        real.append( len( refs) - 1)
      else:
        points.append( None)
    if len( real) < 3:
      continue
    implicit = [i for i in range( 4) if refs[i] is None]
    if len( implicit) > 1:
      continue
    lengths = [ math.hypot( points[i][0], points[i][1]) for i in real]
    mean_length = sum( lengths) / len( lengths) or 1.0
    # CLOCKWISE as seen from references[0] means a negative rotation
    target = -1.0 if st.value == 1 else 1.0
    # a bond shared with an already processed stereocenter may
    # already be a wedge or hatch; relative to this center that lifts
    # the shared neighbour out of the plane and has to be taken into
    # account (the wide end of the bond is the lifted end)
    base_z = [0.0, 0.0, 0.0, 0.0]
    plain = []
    edge_of = {}
    for j in real:
      neighbour = refs[j]
      for e in center.neighbor_edges:
        if neighbour in e.vertices:
          edge_of[j] = e
          if e.type == 'n':
            plain.append( j)
          elif e.type in ('w', 'h'):
            lift = mean_length if e.type == 'w' else -mean_length
            if e.vertices[0] is center:
              base_z[j] = lift    # neighbour is the wide end
            else:
              base_z[j] = -lift   # the center is the wide end
          break
    # depiction preference: outside (non-ring) bonds first, then
    # bonds to ordinary neighbours, then ring bonds and bonds to
    # another stereocenter; SMILES order within each class
    plain.sort( key=lambda j: (id( edge_of[j]) in ring_edges,
                               refs[j] in center_atoms, j))
    def rotation_for( zs):
      return _seen_rotation_sign(
        _complete_points( points, real, implicit, zs, mean_length))
    if any( base_z) and rotation_for( base_z) == target:
      continue # the shared wedge already encodes this center
    chosen = None
    for j in plain:
      for kind, z in (('w', mean_length), ('h', -mean_length)):
        trial = list( base_z)
        trial[j] = z
        if rotation_for( trial) == target:
          chosen = (j, kind)
          break
      if chosen:
        break
    if not chosen:
      continue
    j, kind = chosen
    neighbour = refs[j]
    for e in center.neighbor_edges:
      if neighbour in e.vertices:
        if e.type == 'n':
          e.type = kind
          # the wedge point belongs at the stereocenter
          if e.vertices[0] is not center:
            e.vertices = (center, neighbour)
        break


def _complete_points( points, real, implicit, zs, mean_length):
  """3D positions of the four references: the real ones from the
  drawing, lifted out of the plane by zs, and an implicit hydrogen
  placed opposite the 3D resultant of its real neighbours - the
  tetrahedral completion a reader of the drawing assumes."""
  p = [None, None, None, None]
  sx = sy = sz = 0.0
  for i in real:
    x, y = points[i]
    z = zs[i]
    p[i] = (x, y, z)
    n = math.sqrt( x*x + y*y + z*z)
    if n:
      sx += x / n
      sy += y / n
      sz += z / n
  for i in implicit:
    n = math.sqrt( sx*sx + sy*sy + sz*sz)
    if n > 1e-6:
      p[i] = (-mean_length * sx / n, -mean_length * sy / n,
              -mean_length * sz / n)
    else:
      p[i] = (0.0, 0.0, -mean_length)
  return p


def _seen_rotation_sign( p):
  """Sign of the rotation references[1] -> [2] -> [3] as seen when
  looking from references[0] towards the stereocenter (at the
  origin), given the references' 3D positions p:
  +1 anticlockwise, -1 clockwise, 0 degenerate."""
  # view axis: from the first reference towards the center
  ax, ay, az = -p[0][0], -p[0][1], -p[0][2]
  alen = math.sqrt( ax*ax + ay*ay + az*az)
  if alen < 1e-9:
    return 0.0
  ax, ay, az = ax / alen, ay / alen, az / alen
  # screen basis: w back to the viewer, u right, v up (u x v = w)
  wx, wy, wz = -ax, -ay, -az
  ux, uy, uz = wz, 0.0, -wx
  unorm = math.sqrt( ux*ux + uy*uy + uz*uz)
  if unorm < 1e-9:
    ux, uy, uz = 1.0, 0.0, 0.0
  else:
    ux, uy, uz = ux / unorm, uy / unorm, uz / unorm
  vx, vy, vz = wy*uz - wz*uy, wz*ux - wx*uz, wx*uy - wy*ux
  # screen positions of the other references as seen from the first
  # one: directions from references[0], projected on the screen basis
  s = []
  for i in (1, 2, 3):
    dx, dy, dz = p[i][0] - p[0][0], p[i][1] - p[0][1], p[i][2] - p[0][2]
    s.append( (dx*ux + dy*uy + dz*uz, dx*vx + dy*vy + dz*vz))
  # rotational direction of 1 -> 2 -> 3 around the center (which sits
  # at the screen origin in this view): compare the azimuths of the
  # other two references relative to the first one - if 2 comes
  # before 3 in anticlockwise order around the center, the rotation
  # is anticlockwise
  if any( math.hypot( x, y) < 1e-9 for x, y in s):
    return 0.0 # a reference (nearly) hidden behind the first one
  angles = [ math.atan2( y, x) for x, y in s]
  b2 = (angles[1] - angles[0]) % (2 * math.pi)
  b3 = (angles[2] - angles[0]) % (2 * math.pi)
  if abs( b2 - b3) < 1e-9:
    return 0.0
  return 1.0 if b2 < b3 else -1.0


def oasa_atom_to_bkchem_atom( a, paper, m):
  at = atom.atom( standard=paper.standard, molecule=m)
  at.x = a.x
  at.y = a.y
  at.z = a.z
  at.set_name( a.symbol, interpret=1)
  at.charge = a.charge
  at.number = a.properties_.get( 'inchi_number', None)
  at.show_number = False
  at.isotope = a.isotope
  at.valency = a.valency
  at.multiplicity = at.multiplicity
  return at

def oasa_bond_to_bkchem_bond( b, paper):
  bo = bond.bond( standard=paper.standard)
  bo.type = b.type
  bo.order = b.order
  return bo


# ==================================================
# BKCHEM -> OASA

def bkchem_mol_to_oasa_mol( mol):
  m = oasa.molecule()
  for a in mol.atoms:
    m.add_vertex( bkchem_atom_to_oasa_atom( a))
  for b in mol.bonds:
    b2 = bkchem_bond_to_oasa_bond( b)
    aa1, aa2 = b.atoms
    v1 = m.vertices[ mol.atoms.index( aa1)]
    v2 = m.vertices[ mol.atoms.index( aa2)]
    b2.vertices = (v1, v2)
    m.add_edge( v1, v2, b2)
  return m




def bkchem_atom_to_oasa_atom( a):
  s = a.symbol
  ret = oasa.atom( symbol=s)
  x, y, z = a.get_xyz()
  ret.x = x
  ret.y = y
  ret.z = z
  ret.charge = a.charge
  ret.multiplicity = a.multiplicity
  ret.valency = a.valency
  if hasattr(a,'isotope'):
    ret.isotope = a.isotope
  return ret

def bkchem_bond_to_oasa_bond( b):
  ret = oasa.bond( order=b.order, type=b.type)
  return ret



### TODO

# coordinates transformations
