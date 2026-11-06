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


"""home for group - a vertex of a molecular graph"""


from warnings import warn
from . import dom_extensions
from .oasa import periodic_table as PT
try:
  from .oasa.oasa.known_groups import name_to_smiles
except ImportError:
  from .oasa.known_groups import name_to_smiles
from . import groups_table as GT
from .special_parents import drawable_chem_vertex
from . import data
import math
import re
from . import debug
from . import marks

from . import oasa

from .singleton_store import Store, Screen


### NOTE: now that all classes are children of meta_enabled, so the read_standard_values method
### is called during their __init__ (in fact meta_enabled.__init__), therefor these values are
### not set in __init__ itself


### Class GROUP --------------------------------------------------
class group( drawable_chem_vertex):
  # note that all children of simple_parent have default meta infos set
  # therefor it is not necessary to provide them for all new classes if they
  # don't differ

  object_type = 'atom'

  meta__undo_properties = drawable_chem_vertex.meta__undo_properties

  # only number marks are allowed for groups
  meta__allowed_marks = ("atom_number",)


  def __init__( self, standard=None, xy=(), package=None, molecule=None):
    drawable_chem_vertex.__init__( self, standard=standard, xy=xy, molecule=molecule)

    self.group_graph = None
    self.connecting_atom = None
    self.group_type = None
    self.symbol = ''

    if package:
      self.read_package( package)


  ## -------------------------------------- CLASS METHODS ------------------------------

  @classmethod
  def is_known_group( cls, text):
    if (text in name_to_smiles): # or (text.capitalize() in name_to_smiles):
      return True
    return False

  ## ---------------------------------------- PROPERTIES ------------------------------
      

  # symbol
  def _get_symbol( self):
    return self._symbol

  def _set_symbol( self, symbol):
    # in Python 3 the symbol must stay a str - storing it encoded as
    # bytes (a Python 2 leftover) breaks everything that uses it as
    # text later on (re.sub in _get_xml_ftext, groups_table lookups,
    # XML attributes, ...)
    if isinstance( symbol, bytes):
      t = symbol.decode( 'utf-8')
    else:
      t = str( symbol)
    self._symbol = t
    self.dirty = 1

  symbol = property( _get_symbol, _set_symbol)



  #valency (overrides chem_vertex.valency)
  def _get_valency( self):
    # is always equal to the currently occupied_valency so that free_valency is always == 0
    return self.occupied_valency

  def _set_valency( self, val):
    pass

  valency = property( _get_valency, _set_valency, None, "atoms (maximum) valency, used for hydrogen counting")




  # xml_ftext (override drawable_chem_vertex.xml_ftext)
  def _get_xml_ftext( self):
    if self.group_type == "builtin":
      if self.pos == 'center-first':
        return GT.groups_table[ self.symbol.lower()]['textf']
      else:
        return GT.groups_table[ self.symbol.lower()]['textb']
    elif self.group_type in ("implicit","chain"):
      x = re.sub( r"\d+", r'<sub>\g<0></sub>', self.symbol)
      x = re.sub( r"[+-]", r'<sup>\g<0></sup>', x)
      if self.paper.get_paper_property('use_real_minus'):
        x = re.sub("-", chr(8722), x)
      return x


  xml_ftext = property( _get_xml_ftext, None, None, "the text used for rendering using the ftext class")




  ## JUST TO MIMICK ATOM
  # show
  def _get_show( self):
    return 1

  def _set_show( self, show):
    pass

  show = property( _get_show, _set_show, None,
                   "should the atom symbol be displayed? accepts both 0|1 and yes|no")


  # show_hydrogens
  def _get_show_hydrogens( self):
    return 1

  def _set_show_hydrogens( self, show_hydrogens):
    pass

  show_hydrogens = property( _get_show_hydrogens, _set_show_hydrogens)

  ## //


  #group_type
  def _get_group_type( self):
    return self.__group_type

  def _set_group_type( self, group_type):
    allowed_types = (None,"builtin","explicit","implicit","chain","general")
    if group_type not in allowed_types:
      raise ValueError("group_type must be one of "+ str( allowed_types) + "got %s" % group_type)
    self.__group_type = group_type

  group_type = property( _get_group_type, _set_group_type)




  ## // -------------------- END OF PROPERTIES --------------------------



  def set_name( self, name, interpret=1, occupied_valency=None):
    if occupied_valency == None:
      occupied_valency = self.occupied_valency
    if occupied_valency == 1 and (name.lower() in GT.groups_table):
      # name is a known group
      self.symbol = GT.groups_table[ name.lower()]['name']
      self.group_type = "builtin"
      return True
    # try interpret the formula - but only when the atom this group
    # should replace has at most one bond.  A group attaches through a
    # single bond of its connecting atom (the builtin and chain groups
    # below are likewise restricted to occupied_valency == 1), and
    # oasa's linear_formula parser cannot be trusted with a higher
    # start/end valency: instead of failing it silently adapts the
    # internal bond orders of the formula - e.g. "COOH" with a start
    # valency of 3 "parses", but the carbonyl carbon ends up with only
    # one internal bond, so the result is no longer COOH at all.
    lf = None
    if occupied_valency <= 1:
      lf = oasa.linear_formula.linear_formula( name, start_valency=occupied_valency)
      if not lf.molecule:
        # it is possible the text goes the other way
        lf = oasa.linear_formula.linear_formula( name, end_valency=occupied_valency)
    if lf and lf.molecule:
      self.group_graph = lf.molecule
      if lf.first_atom:
        self.connecting_atom = lf.first_atom
      elif lf.last_atom:
        self.connecting_atom = lf.last_atom
      else:
        self.connecting_atom = lf.molecule.vertices[0]
      self.symbol = name
      self.group_type = "implicit"
      self.group_graph.paper = self.paper
      return True
    # try chain
    if re.compile( "^[cC][0-9]*[hH][0-9]*$").match( name):
      form = PT.formula_dict( name.upper())
      if occupied_valency == 1 and form.is_saturated_alkyl_chain():
        self.symbol = str( form)
        self.group_type = "chain"
        return True
    return False


  def interpret_name( self, name):
    lf = oasa.linear_formula.linear_formula( name, start_valency=self.valency)
    return lf.molecule
      




  def read_package( self, package):
    """reads the dom element package and sets internal state according to it"""
    a = ['no','yes']
    on_off = ['off','on']
    self.id = package.getAttribute( 'id')
    self.pos = package.getAttribute( 'pos')
    position = package.getElementsByTagName( 'point')[0]
    # reading of coords regardless of their unit
    x, y, z = Screen.read_xml_point( position)
    if z != None:
      self.z = z* self.paper.real_to_screen_ratio()
    # needed to support transparent handling of molecular size
    x, y = self.paper.real_to_screen_coords( (x, y))
    self.x = x
    self.y = y
    self.group_type = package.getAttribute( "group-type")
    if self.group_type in ("implicit","explicit"):
      #read the graph once
      pass
    self.symbol = package.getAttribute( "name")

    # font and fill color
    fnt = package.getElementsByTagName('font')
    if fnt:
      fnt = fnt[0]
      self.font_size = int( fnt.getAttribute( 'size'))
      self.font_family = fnt.getAttribute( 'family')
      if fnt.getAttribute( 'color'):
        self.line_color = fnt.getAttribute( 'color')
    # background color
    if package.getAttributeNode( 'background-color'):
      self.area_color = package.getAttribute( 'background-color')

    # marks
    for m in package.getElementsByTagName( 'mark'):
      mrk = marks.mark.read_package( m, self)
      self.marks.add( mrk)
    # number
    if package.getAttribute( 'show_number'):
      self.show_number = bool( data.booleans.index( package.getAttribute( 'show_number')))
    if package.getAttribute( 'number'):
      self.number = package.getAttribute( 'number')



  def get_package( self, doc):
    """returns a DOM element describing the object in CDML,
    doc is the parent document which is used for element creation
    (the returned element is not inserted into the document)"""
    y = ['no','yes']
    on_off = ['off','on']
    a = doc.createElement('group')
    a.setAttribute( 'id', str( self.id))
    a.setAttribute( 'pos', self.pos)
    # group type
    if self.group_type:
      a.setAttribute( 'group-type', self.group_type)
    else:
      raise ValueError("trying to save group without set group-type")

    if self.font_size != self.paper.standard.font_size \
       or self.font_family != self.paper.standard.font_family \
       or self.line_color != self.paper.standard.line_color:
      font = dom_extensions.elementUnder( a, 'font', attributes=(('size', str( self.font_size)), ('family', self.font_family)))
      if self.line_color != self.paper.standard.line_color:
        font.setAttribute( 'color', self.line_color)

    a.setAttribute( 'name', self.symbol)

    if self.area_color != self.paper.standard.area_color:
      a.setAttribute( 'background-color', self.area_color)
    # needed to support transparent handling of molecular size
    x, y, z = map( Screen.px_to_text_with_unit, self.get_xyz( real=1))
    if self.z:
      dom_extensions.elementUnder( a, 'point', attributes=(('x', x), ('y', y), ('z', z)))
    else: 
      dom_extensions.elementUnder( a, 'point', attributes=(('x', x), ('y', y)))
    # marks
    for o in self.marks:
      a.appendChild( o.get_package( doc))
    # number
    if self.number:
      a.setAttribute( 'number', self.number)
      a.setAttribute( 'show_number', data.booleans[ int( self.show_number)])

    return a




  def get_formula_dict( self):
    """returns formula as dictionary that can
    be passed to functions in periodic_table"""
    if self.group_type == "builtin":
      return PT.formula_dict( GT.groups_table[ self.symbol.lower()]['composition'])
    elif self.group_graph:
      form = self.group_graph.get_formula_dict()
      if 'H' in form:
        if form['H'] > self.occupied_valency:
          form['H'] -= self.occupied_valency
        else:
          del form['H']
      return form
    else:
      return PT.formula_dict( self.symbol)
      


  def __str__( self):
    return self.id




  def expand( self):
    """expands the group and returns list of atoms that new drawing afterwords"""
    if self.group_type == "builtin":
      names = Store.gm.get_template_names()
      if self.symbol in names:
        a2 = self.neighbors[0]
        x1, y1 = a2.get_xy()
        x2, y2 = self.get_xy()
        self.group_graph = Store.gm.get_transformed_template( names.index( self.symbol), (x1,y1,x2,y2), type='atom1')
        replacement = self.group_graph.next_to_t_atom
      else:
        print("unknown group %s" % a.symbol)
        return None

    elif self.group_type == "chain":
      self.group_graph = self.molecule.create_graph()
      p = PT.formula_dict( self.symbol)
      n = p['C']
      last = None
      for i in range( n):
        v = self.group_graph.add_vertex()
        v.x, v.y = None, None
        if last:
          self.group_graph.add_edge( last, v)
        last = v
      replacement = self.group_graph.vertices[0]
      replacement.x = self.x
      replacement.y = self.y

    elif self.group_type == "implicit":
      if not self.group_graph:
        self.set_name( self.symbol, occupied_valency=self.occupied_valency)
      for v in self.group_graph.vertices:
        v.x, v.y = None, None
        v.show = v.symbol != 'C'
      assert self.connecting_atom != None
      replacement = self.connecting_atom
      replacement.x = self.x
      replacement.y = self.y
      
    self.molecule.eat_molecule( self.group_graph)
    self.molecule.move_bonds_between_atoms( self, replacement)
    self.molecule.delete_vertex( self)
    if self.occupied_valency:
      oasa.coords_generator.calculate_coords( self.molecule, bond_length=-1)
      self._relieve_expansion_clash( replacement)
    else:
      # if the group is the only vertex of the molecule we must set the bond_length explicitly
      # and the move the whole molecule
      replacement.x = None
      replacement.y = None
      x, y = self.x, self.y
      oasa.coords_generator.calculate_coords( self.molecule, bond_length=Screen.any_to_px( self.paper.standard.bond_length))
      dx = x - replacement.x
      dy = y - replacement.y
      [a.move( dx, dy) for a in self.group_graph.vertices]
    return self.group_graph.vertices



  def _relieve_expansion_clash( self, replacement):
    """swing a freshly expanded group away from the rest of the molecule
    when it was placed on top of it.

    Expansion fits the group into the position and direction of the atom
    it replaced, with ideal angles and no regard for the rest of the
    molecule, so e.g. a phenyl replacing the peri hydroxyl of troxerutin
    ends up with its edge carbons ~0.5 bond lengths from the neighbouring
    ring. When (and only when) some atom of the new fragment comes closer
    than 0.6 bond lengths to an atom outside the fragment, try rotating
    the whole fragment rigidly around the atom it hangs on and keep the
    first placement that is strictly better (fewest clashes, then fewest
    bond crossings, then the largest remaining clearance). Two centres
    are tried: the atom it hangs on (which swings the attachment bond
    to a new direction) and the fragment's own attachment atom (which
    keeps the attachment bond and only turns the fragment around it).
    The second centre matters - on the troxerutin example no swing
    around the hanging atom helps (best 0.53), while a 5 degree turn
    around the attachment atom clears the clash (0.61). Rotation in
    the plane is a proper rigid motion, so the fragment's own geometry
    and stereochemistry are preserved; placements without a clash are
    never touched, and small angles are tried first so the winning
    placement distorts the ideal angles as little as possible."""
    frag = list( self.group_graph.vertices)
    frag_set = set( frag)
    if replacement not in frag_set:
      return
    # the fragment must hang on exactly one atom of the original molecule
    pivots = set()
    for v in frag:
      for n in v.get_neighbors():
        if n not in frag_set:
          pivots.add( n)
    if len( pivots) != 1:
      return
    pivot = pivots.pop()
    rest = [v for v in self.molecule.vertices if v not in frag_set]
    if not rest or None in [v.x for v in frag] + [v.y for v in frag]:
      return
    lengths = []
    for e in self.molecule.edges:
      a1, a2 = e.atoms
      lengths.append( math.hypot( a1.x - a2.x, a1.y - a2.y))
    if not lengths:
      return
    lengths.sort()
    bond_length = lengths[len( lengths) // 2] or 1.0
    frag_bonds = [(e.atoms[0], e.atoms[1]) for e in self.molecule.edges
                  if e.atoms[0] in frag_set and e.atoms[1] in frag_set]
    frag_bonds.append( (pivot, replacement))
    rest_bonds = [(e.atoms[0], e.atoms[1]) for e in self.molecule.edges
                  if e.atoms[0] not in frag_set and e.atoms[1] not in frag_set]

    def score( coords):
      severe = 0
      mind = None
      for v in frag:
        x, y = coords[v]
        for u in rest:
          if u is pivot and v is replacement:
            continue # the attachment bond itself
          d = math.hypot( x - u.x, y - u.y) / bond_length
          if mind is None or d < mind:
            mind = d
          if d < 0.6:
            severe += 1
      cross = 0
      for a1, a2 in frag_bonds:
        p1 = coords[a1] if a1 in coords else (a1.x, a1.y)
        p2 = coords[a2] if a2 in coords else (a2.x, a2.y)
        for b1, b2 in rest_bonds:
          if _segments_cross( p1, p2, (b1.x, b1.y), (b2.x, b2.y)):
            cross += 1
      return (severe, cross, -(mind or 0.0))

    original = dict( [(v, (v.x, v.y)) for v in frag])
    best = score( original)
    if best[0] == 0:
      return # nothing is clashing - leave the placement alone
    best_coords = None
    for angle in (5, -5, 10, -10, 15, -15, 30, -30, 45, -45, 60, -60,
                  90, -90, 120, -120, 150, -150, 180):
      for cx, cy in ((replacement.x, replacement.y), (pivot.x, pivot.y)):
        rad = math.radians( angle)
        cosr, sinr = math.cos( rad), math.sin( rad)
        rotated = {}
        for v in frag:
          dx, dy = v.x - cx, v.y - cy
          rotated[v] = (cx + dx * cosr - dy * sinr,
                        cy + dx * sinr + dy * cosr)
        s = score( rotated)
        if s < best:
          best = s
          best_coords = rotated
    if best_coords is not None:
      for v in frag:
        v.x, v.y = best_coords[v]



def _segments_cross( p1, p2, p3, p4):
  """True when the segments p1p2 and p3p4 cross in their interiors"""
  def orient( a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
  d1 = orient( p3, p4, p1)
  d2 = orient( p3, p4, p2)
  d3 = orient( p1, p2, p3)
  d4 = orient( p1, p2, p4)
  return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))
