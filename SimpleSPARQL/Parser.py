# -*- coding: utf-8 -*-
import Namespaces
from Triple import Triple
from Utils import p, is_lit_var, is_any_var, split_string, merge_string
from Utils import Var, LitVar, MetaVar, var_type_name

import re

re_lhs_rhs = re.compile('(.+)\s*=\s*(.+)')
re_obj_prop = re.compile('(\w+)\[(\w+)\.(\w+)\]')

re_equals = re.compile('(\||)\s*(.+)\s*=\s*(.+)')
re_prop = re.compile('(.+)\[(.+)\]')
re_dict = re.compile('(.+){(.+)}')
re_dict_pair = re.compile('\s*([^,:\.]*[:\.]*[^,:\.]*)\s*:\s*([^,:\.]*[:\.]*[^,:\.]*)\s*,')
re_call = re.compile('(.+?)\((.*)\)')
re_call_params = re.compile('([^,]+),')
re_uri = re.compile('(\D\w*|)[\.:]([\w/]+)')
re_var = re.compile('^[a-zA-Z_]\w*$')
re_meta_var = re.compile('^\?[a-zA-Z_]\w*$')
re_lit_var = re.compile('^_[a-zA-Z_]\w*$')
re_comment = re.compile('(#.*)$')

python_keywords = ['True', 'False']

from pyparsing import Forward, nestedExpr, Word
import string

enclosed = Forward()
nestedParens = nestedExpr('(', ')', content=enclosed)
anything_but_parens = Word(
    string.printable
    .replace('(','')
    .replace(')','')
    .replace(',','')
)
enclosed << (anything_but_parens | nestedParens | ',')

def flatten(l) :
    ret = '('
    for i in l :
	if isinstance(i, list) :
            ret += flatten(i)
	else :
            ret += i
    return ret + ')'

def parse_arglist(str) :
    """ given the string inside of a function call, return comma
    seperated expressions.  More of the parser should probably be
    written with pyparsing ..."""
    par = enclosed.parseString('('+str+')').asList()[0]
    ret = []
    for w in par :
	if isinstance(w, list) :
            if not ret : ret = ['']

            ret[-1] += flatten(w)
	elif w == ',' :
            pass
	else :
            ret.append(w)
    return ret

class Expression():
  def __init__(self, exp, missing = None, optional = False) :
    self.exp = exp
    # a list of indicies into exp where the missing value is
    self.missing = missing
    self.optional = optional
  
  def put(self, value) :
    #print 'self.exp',self.exp
    #print 'self.missing',self.missing
    #print 'value',value
    ele = self.exp
    for i in self.missing[:-1] :
      ele = ele[i]
    ele[self.missing[-1]] = value
    self.missing = None
  
  def triplelist(self, check_for_missing=False) :
    if check_for_missing and self.missing :
      pass
      #p('missing',self.missing)
    if isinstance(self.exp, list) and not isinstance(self.exp[0], list) :
      return [self.exp]
    else :
      return self.exp
  
  def merge(self, other) :
    #self.exp = self.triplelist()
    #self.exp.extend(other.triplelist())
    self.exp = self.triplelist()
    other.exp = other.triplelist()
    if self.missing :
      if other.missing :
        raise Exception('cant merge two Expressions with missing values')
    else :
      # correct for the case where other was just a triple to start
      if other.missing :
        if len(other.missing) == 1 :
          other.missing = [0] + other.missing
        self.missing = [len(self.exp) + other.missing[0], other.missing[1]]
    self.exp.extend(other.exp)
  
  def __str__(self) :
    return '<Expression %s>' % str((self.exp, self.missing))
  
  def __repr__(self) :
    return str(self.exp)

class Parser() :
  def __init__(self, n = None) :
    if not n:
      n = Namespaces.Namespaces()
    
    #n.bind('meta_var', '<http://dwiel.net/express/meta_var/0.1/>')
    #n.bind('lit_var', '<http://dwiel.net/express/lit_var/0.1/>')
    
    self.n = n
    self.var = 0
  
  def parse_expression(self, expression) :
    #try :
    expression, str_bindings = self.convert_strings_to_vars(expression)
    exp = self.parse_expression_new(expression)
    #except :
      #raise Exception('error parsing %s' % expression)
    #p('exp',exp)
    if exp is None :
      raise Exception('Could not parse %s' % expression)
    code = '[\n%s\n]' % ',\n'.join([
      'Triple([%s], %s)' % (', '.join(triple), isinstance(triple, Triple) and triple.optional)
      for triple in exp.triplelist(True)
    ])
    triples = eval(code, {'n' : self.n, 'Triple' : Triple, 'Var' : Var, 'LitVar' : LitVar, 'MetaVar' : MetaVar}, {})
    
    if str_bindings :
      for triple in triples :
        for i, value in enumerate(triple) :
          if is_lit_var(value) and value.name[:4] == '_str' :
            triple[i] = str_bindings[value.name[4:]]
    
    # run some sanity checks
    self.check_for_inconsistent_var_litvar(triples) 
    
    return triples
  
  def check_for_inconsistent_var_litvar(self, triples) :
    """ check to see if a var is a Var in one place and a LitVar in another """
    # var_types := {var_name : var}
    #   is populated as we iterate over all of the values.  any vars we find are
    #   added to var_types so we can make sure that other vars of the same name
    #   have the same type
    var_types = {}
    for triple in triples :
      for v in triple :
        if is_any_var(v) :
          if v.name in var_types :
            if var_types[v.name] != type(v) :
              t1 = str(type(v))
              raise Exception("inconsistent var type. %s and %s" % (
                var_type_name(v), var_type_name(var_types[v.name])
              ))
          else :
            var_types[v.name] = type(v)
  
  def flatten(self, seq):
    """
    flatten seq one level, not recursively
    """
    res = []
    for item in seq:
      res.extend(item)
    return res
  
  def break_multiline_string(self, string) :
    """
    given a string with multiple lines, split it up, remove any leading or 
    trailing space, and remove any blank lines
    """
    prepend_to_next_line = ''
    for line in string.strip().split('\n') :
      line = line.strip()
      
      if line is '' :
        continue
      
      line = prepend_to_next_line + line
      
      # look for a pipe character at the end of the line
      g = re.search("\|\s*$", line)
      if g :
        prepend_to_next_line = line
        continue
      else :
        prepend_to_next_line = ''
      
      yield line
    
    # if there was a pipe at the end of the last line, it is an error
    if prepend_to_next_line :
      raise Exception('the last line of a query cant have a | at the end')
  
  def convert_strings_to_vars(self, expression) :
    """
    given an expression, find all strings and replace them with token variables.
    This make parsing later easier.
    @returns a new expression and a set of bindings from new variable to string
    """
    str_bindings = {}
    str_num = 0
    new_expression = ""
    i = 0
    pipe = False
    # loop through each character, if it is either of the quotes, start quoting
    # if its a triple quote though, start a long triple quote.
    while i < len(expression) :
      letter = expression[i]
      if letter in "'\"" :
        # check for triple quote
        if expression[i+1:i+3] == letter * 2 :
          letter *= 3
        
        # extract out the string
        g = re.search("(.*?[^\\\\])"+letter, expression[i+len(letter):])
        if g is None :
          raise Exception("Parse Error: unclosed quote (%s): %s" % (letter, expression))
        string = g.group(1)
        
        # if this is an or list (> 1 string seperated by |) bind to the list of strings
        if pipe :
          existing = str_bindings[str(str_num-1)]
          if isinstance(existing, basestring) :
            str_bindings[str(str_num-1)] = [existing, string]
          else :
            str_bindings[str(str_num)].append(string)
        else :
          new_expression += '__str' + str(str_num)
          str_bindings[str(str_num)] = string
          str_num += 1
        # move on to the rest of the expression
        i += len(string) + (len(letter) * 2) - 1
        
        # look for a | connector
        g = re.search("""(\s*\|\s*)['"]""", expression[i:])
        if g :
          i += len(g.group(1))
          pipe = True
        else :
          pipe = False
      else :
        new_expression += letter
      i += 1
    return new_expression, str_bindings
  
  def strip_comments(self, query) :
    for line in query :
      new_line = re_comment.sub('', line).strip()
      if new_line :
        yield new_line
  
  def parse(self, query, reset_bnodes = True) :
    return self.parse_query(query, reset_bnodes)
  
  def parse_query(self, query, reset_bnodes = True) :
    """
    parse a string query into a list of triples
    @arg query the string or list of strings to parse
    @arg reset_bnode when True, will reset the bnode counter.  Change to false
      if you want to parse multiple queries which will all act as one query (you
      want to be able to use the results from one in the other, without bnode 
      name conflicts
    """
    if isinstance(query, basestring) :
      query = self.break_multiline_string(query)
      query = self.strip_comments(query)
    if reset_bnodes :
      self._reset_bnode()
    return self.flatten([isinstance(expression, basestring) and self.parse_expression(expression) or [expression] for expression in query])
  
  def _reset_bnode(self) :
    self.var = 0
  
  def next_bnode(self) :
    self.var += 1
    #return 'n.var.bnode%s' % self.var
    return 'Var.bnode%s' % self.var
  
  def parse_expression_new(self, expression) :
    expression = expression.replace('\n', '')
    expression = expression.strip()

    g = re_equals.match(expression)
    if g is not None :
      #p('re_equals', g.group(0))
      if expression.count('=') > 1 :
        # this is a harder case ...
        print g.group(0)
      
      lhs = self.parse_expression_new(g.group(2))
      rhs = self.parse_expression_new(g.group(3))
      
      if g.group(1) :
        optional = True
      
      if isinstance(lhs, Expression) :
        if isinstance(rhs, Expression) :
          bnode = self.next_bnode()
          lhs.put(bnode)
          rhs.put(bnode)
          lhs.merge(rhs)
          lhs.optional = True
          return lhs
        else :
          lhs.put(rhs)
          lhs.optional = True
          return lhs
      else :
        if isinstance(rhs, Expression) :
          rhs.put(lhs)
          rhs.optional = True
          return rhs
        else :
          return None
    
    g = re_prop.match(expression)
    if g is not None :
      #p('re_prop', g.group(0))
      obj = self.parse_expression_new(g.group(1))
      prop = self.parse_expression_new(g.group(2))
      
      if isinstance(obj, Expression) :
        if isinstance(prop, Expression) :
          return None
        else :
          bnode = self.next_bnode()
          obj.put(bnode)
          obj.merge(Expression([bnode, prop, None], [2]))
          return obj
      else :
        if isinstance(prop, Expression) :
          return None
        else :
          return Expression([obj, prop, None], [2])
    
    g = re_dict.match(expression)
    if g is not None :
      #p('re_dict', g.group(0))
      obj = g.group(1).strip()
      inside = g.group(2).strip() + ','
      
      obj = self.parse_expression_new(obj)  
      
      pairs = re_dict_pair.findall(inside)
      if pairs is not [] :
        # if we are here, this is a valid dict
        bnode = self.next_bnode()
        triples = []
        for pair in pairs :
          l = self.parse_expression_new(pair[0])
          r = self.parse_expression_new(pair[1])
          triples.append([bnode, l, r])
        triples.append([bnode, obj, None])
        return Expression(triples, [len(triples)-1, 2])
      else :
        raise Exception('bad dictionary %s' % expression)
    
    g = re_call.match(expression)
    if g is not None :
      #p('re_call', g.group(0))
      obj = self.parse_expression_new(g.group(1))
      params = g.group(2) + ','

      params = parse_arglist(params)

      params = [self.parse_expression_new(param) for param in params]

      triples = []
      new_params = []
      for param in params :
        # this happens when an argument into the call is the return value of
        # another call
        if isinstance(param, Expression) :
          bnode = self.next_bnode()
          param.put(bnode)
          triples.extend(param.triplelist())
          param = bnode
        new_params.append(param)
      
      triples.append([obj] + new_params + [None])
      return Expression(triples, [len(triples)-1, -1])
    
    g = re_uri.match(expression)
    if g is not None :
      #p('re_uri', g.group(0))
      namespace = g.group(1).strip()
      value = g.group(2).strip()
      if len(namespace) == 0 :
        return 'n[""]["%s"]' % value
      else :
        return 'n.%s["%s"]' % (namespace, value)
    
    if expression in python_keywords :
      #p('keyword', expression)
      return expression
    
    g = re_lit_var.match(expression)
    if g is not None :
      #p('re_lit_var', expression[1:])
      return 'LitVar("%s")' % expression[1:]
    
    if re_meta_var.match(expression) :
      #p('re_meta_var', expression[1:])
      return 'MetaVar("%s")' % expression[1:]
    
    if re_var.match(expression) :
      #p('re_var', expression)
      return 'Var("%s")' % expression
    
    # number (or other python expressions?)
    #p('just expression', expression)
    return expression
    



"""
value : var | literal | var[prop] | prop(value)
expression : value = value

'var[prop] = ?' := [var, prop, ?]
'? = var[prop]' := [var, prop, ?]
'prop(var) = ?' := [var, prop, ?]
'var1[prop1] = var2[prop2]' := [[var1, prop1, x], [var2, prop2, x]]
'fn{prop1 : val1, prop2 : val2} = ?' := [
  [x, prop1, val1],
  [x, prop2, val2],
  [x, fn, ?]
]

value:
  string, int, bool, var, etc
  'value[value]' := [value, value, ?]
expressions:
'value1[value2] = value3' := [value1, value2, value3]
'value1(value2) = value3' := [value2, value1, value3]

"""
