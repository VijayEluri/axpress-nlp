#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import time, urllib
from rdflib import *
from SimpleSPARQL import *

# for easy basic stupid matching type instance
class X():pass
type_instance = type(X())

axpress = Axpress()

class AxpressTestCase(unittest.TestCase):
  def testGlob(self):
    rets = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      image[file.filename] = _filename
    """)
    assert len(rets) == 2
    assert all('filename' in ret for ret in rets)
    assert all(len(ret) == 1 for ret in rets)
    assert 'pictures/111.jpg'    in [ret['filename'] for ret in rets]
    assert 'pictures/foobar.jpg' in [ret['filename'] for ret in rets]
  
  def testTranslationReturnsMultipleValues(self):
    ret = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      thumb = image.thumbnail(image, 4, 4)
      thumb[pil.image] = _thumb_image
    """, reqd_bound_vars = ['thumb_image'])
    for i, bindings in enumerate(ret) :
      ret[i]['thumb_image'] = type(bindings['thumb_image'])
    assert ret == [
      {
        'thumb_image' : type_instance,
      }, {
        'thumb_image' : type_instance,
      }
    ]
  
  def testQueryLimitLessThanAvailable(self):
    ret = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      thumb = image.thumbnail(image, 4, 4)
      thumb[pil.image] = _thumb_image
      query.query[query.limit] = 1
    """, reqd_bound_vars = ['thumb_image'])
    #print 'ret test2_1',prettyquery(ret)
    ret = [{'thumb_image' : type(bindings['thumb_image'])} for bindings in ret]
    assert ret == [
      {
        'thumb_image' : type_instance,
      }
    ]
  
  def testQueryLimitSameAsAvailable(self):
    ret = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      thumb = image.thumbnail(image, 4, 4)
      thumb[pil.image] = _thumb_image
      query.query[query.limit] = 2
    """, reqd_bound_vars = ['thumb_image'])
    #print 'ret2_2',prettyquery(ret)
    ret = [{'thumb_image' : type(bindings['thumb_image'])} for bindings in ret]
    assert ret == [
      {
        'thumb_image' : type_instance,
      }, {
        'thumb_image' : type_instance,
      }
    ]
  
  def testQueryLimitMoreThanAvailable(self):
    ret = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      thumb = image.thumbnail(image, 4, 4)
      thumb[pil.image] = _thumb_image
      query.query[query.limit] = 3
    """, reqd_bound_vars = ['thumb_image'])
    #print 'ret2_3',prettyquery(ret)
    ret = [{'thumb_image' : type(bindings['thumb_image'])} for bindings in ret]
    assert ret == [
      {
        'thumb_image' : type_instance,
      }, {
        'thumb_image' : type_instance,
      }
    ]
  
  # warning this test requires the internet and will ping flickr.  Don't do alot
  #def test3(self) :
    #ret = axpress.read_translate("""
      #image[flickr.tag] = 'floor'
      #image[file.url] = _url
    #""", reqd_bound_vars = ['url'])
    #print 'ret',prettyquery(ret)
  
  # warning this test requires the internet and will ping flickr.  Don't do alot
  #def test4(self) :
    #ret = axpress.read_translate("""
      #image[flickr.tag] = 'wall'
      #thumb = image.thumbnail(image, 4, 4)
      #thumb[pil.image] = _thumb_image
      #query.query[query.limit] = 1
    #""", reqd_bound_vars = ['thumb_image'])
    #print 'ret',prettyquery(ret)
  
  def test5(self):
    ret = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      image[file.filename] = _filename
      thumb = image.thumbnail(image, 4, 4)
      pixel = image.pixel(thumb, 0, 0)
      pixel[pil.color] = _thumb_pixel_color
    """)
    assert ret == [
      {
        'filename' : 'pictures/111.jpg',
        'thumb_pixel_color' : (26, 24, 24),
      }, {
        'filename' : 'pictures/foobar.jpg',
        'thumb_pixel_color' : (69, 68, 73),
      },
    ]
  
  def test6(self):
    ret = axpress.read_translate("""
      image[glob.glob] = "pictures/*.jpg"
      image[file.filename] = _filename
      thumb = image.thumbnail(image, 4, 4)
      pixel = image.pixel(thumb, 0, 0)
      dist[type.number] = color.distance(color.red, pixel)
      dist[type.number] = _distance
    """, reqd_bound_vars = ['filename','distance'])
    #print 'ret6',prettyquery(ret)
    #print ret
    assert ret == [
      {
        'distance' : 53593,
        'filename' : 'pictures/111.jpg',
      }, {
        'distance' : 44549,
        'filename' : 'pictures/foobar.jpg',
      },
    ]

  #def test7(self):
    #ret = axpress.read_translate("""
      #image[glob.glob] = "/home/dwiel/AMOSvid/*.jpg"
      #thumb = image.thumbnail(image, 1, 1)
      #pix = image.pixel(thumb, 0, 0)
      #pix[pil.color] = _color
      #image[file.filename] = _filename
    #""")
    ##print 'ret7',prettyquery(ret)
    #assert len(ret) == 2
    #assert ret == [
      #{
        #'color' : ( 71, 43, 85, ),
        #'filename' : '/home/dwiel/AMOSvid/20080804_080127.jpg',
      #}, {
        #'color' : ( 58, 25, 47, ),
        #'filename' : '/home/dwiel/AMOSvid/20080804_083127.jpg',
      #},
    #]

  
  def testBasicExample(self):
    ret = axpress.read_translate("""
      foo[test.x] = 1
      foo[test.y] = 10
      foo[test.sum] = _sum
    """)
    #p('ret8',ret)
    assert ret == [{'sum' : 11}]

  #def testMultipleNonDependentPaths(self):
    #ret = axpress.read_translate("""
      #image[file.filename] = "/home/dwiel/AMOSvid/20080804_080127.jpg"
      #pix = image.pixel(image, 0, 0)
      #pix[pil.color] = _color
      #image[html.height] = 200
      #image[html.width] = 300
      #image[html.html] = _html
    #""")
    #p('testMultipleNonDependentPaths',ret)
    #assert ret ==  [
      #{
        #'color' : ( 249, 255, 237, ),
        #'html' : '<img src="/home/AMOSvid/20080804_080127.jpg" width="300" height="200"/>',
      #},
    #]

  #def testOptionInputs(self):
    #ret = axpress.read_translate("""
      #image[file.filename] = "/home/dwiel/AMOSvid/20080804_080127.jpg"
      #image[html.width] = 300
      #image[html.html] = _html
    #""")
    #p('testOptionInputs',ret)
    #assert ret ==  [
      #{
        #'html' : '<img src="/home/AMOSvid/20080804_080127.jpg" width="300"/>',
      #},
    #]

  #def testOptionInputs2(self):
    #ret = axpress.read_translate("""
      #image[file.filename] = "/home/dwiel/AMOSvid/20080804_080127.jpg"
      #image[html.html] = _html
    #""")
    #p('testOptionInputs2',ret)
    #assert ret ==  [
      #{
        #'html' : '<img src="/home/AMOSvid/20080804_080127.jpg" />',
      #},
    #]
  
  ## only works when amarok is playing music
  #def testAmarok(self):
    #ret = axpress.read_translate("""
      #amarok.amarok[amarok.artist] = artist
      #artist[music.artist_name] = _name
    #""")
    ##p('ret10',ret)
    #assert len(ret) == 1 and len(ret[0]) == 1 and 'name' in ret[0] and isinstance(ret[0]['name'], basestring)

  def testTranslationReturnsListOfBindings(self):
    ret = axpress.read_translate("""
      qartist[music.artist_name] = 'Neil Young'
      qartist[lastfm.similar_to] = qsimilar_artist
      qsimilar_artist[lastfm.artist_name] = _name
    """)
    #p('ret11',ret)
    assert len(ret) == 10
    for bindings in ret :
      assert len(bindings) == 1
      assert 'name' in bindings
      assert isinstance(bindings['name'], basestring)

  ## only works when amarok is playing music
  #def testTranslationReturnsListOfBindings2(self):
    #ret = axpress.read_translate("""
      #amarok.amarok[amarok.artist] = artist
      #artist[lastfm.similar_to] = similar_artist
      #similar_artist[lastfm.name] = _name
    #""")
    ##p('ret12',ret)
    #assert len(ret) == 10
    #for bindings in ret :
      #assert len(bindings) == 1
      #assert 'name' in bindings
      #assert isinstance(bindings['name'], basestring)
  
  def testNoBindingsFromTranslation(self):
    ret = axpress.read_translate("""
      image[glob.glob] = '/no/files/here/*.jpg'
      image[file.filename] = _filename
    """)
    assert len(ret) == 0

  def testNoBindingsFromTranslation2(self):
    ret = axpress.read_translate("""
      foo[test.no_bindings_input] = "input string"
      foo[test.no_bindings_output] = _output
    """)
    assert len(ret) == 0
  
  def testGeneral(self):
    ret = axpress.read_translate("""
      image[glob.glob] = '/home/dwiel/AMOSvid/1065/*.nothing'
      image[file.filename] = _filename
    """)
    assert ret == []

  def testIncomingOutgoingBindings(self):
    ret = axpress.read_translate("""
      foo[test.x] = x
      foo[test.y] = y
      foo[test.sum] = _sum
    """, bindings_set = [{'x' : 1, 'y' : 2}], reqd_bound_vars=['x', 'sum'])
    #p('ret',ret)
    assert ret == [
      {
        'x' : 1,
        'sum' : 3,
      },
    ]
  
  def testIncomingOutgoingBindings2(self):
    ret = axpress.read_translate("""
      foo[test.x] = _x
      foo[test.y] = y
      foo[test.sum] = _sum
    """, bindings_set = [{'x' : 1, 'y' : 2}])
    #p('ret',ret)
    assert ret == [
      {
        'x' : 1,
        'sum' : 3,
      },
    ]
  
  #def testMultipleInputObjects(self) :
    #ret = axpress.read_translate("""
      #user[lastfm.user_name] = 'dwiel'
      #user[lastfm.recent_track] = track
      #track[lastfm.album] = album
      #track[lastfm.artist] = artist
      #artist[lastfm.artist_name] = _name
    #""")
    #p('ret',ret)
    
  ##depends on Joseki
  #def testLongCount(self) :
  #	ret = axpress.read_sparql("""
  #		x[y] = z
  #		query.query[query.count] = _count		
  #	""")
  #	assert ret == [{'count' : 0}]
  
  ## test a translation which requires a relatively complex unification
  def testUnification(self):
    ret = axpress.read_translate("""
      image[file.pattern] = "pictures/*.jpg"
      image[image.average_color] = _color
    """)
    #p('testUnification', ret)
    assert ret == [
      {
        'color' : ( 16, 15, 15, ),
      }, {
        'color' : ( 139, 137, 145, ),
      },
    ]
  
  def testSpecialUnification(self):
    ret = axpress.read_translate("""
      i[file.pattern] = "pictures/*.jpg"
      image.thumbnail(i, 1, 1) = t
      image.pixel(t, 0, 0) = p
      p[pil.color] = _c
    """)
    #p('testSpecialUnification', ret)
    assert ret == [
      {
        'c' : ( 16, 15, 15, ),
      }, {
        'c' : ( 139, 137, 145, ),
      },
    ]

  
  def testSimplestUnification(self):
    ret = axpress.read_translate("""
      x[test.p][test.p] = 1
      x[test.q][test.q] = _one
    """)
    #p('ret', ret)
    assert ret == [
      {
        'one' : 1
      }
    ]
  
  def testSimpleQuery(self):
    ret = axpress.read_translate("""
      image[file.pattern] = "pictures/*.jpg"
      image.pixel(image, 1, 1) = pixel
      pixel[html.color] = _color
    """)
    assert ret == [
      {
        'color' : '000'
      }, {
        'color' : '302'
      }
    ]
    
  def testSimpleUnification(self):
    ret = axpress.read_translate("""
      color[axpress.is] = "red"
      color[html.color] = _c
    """)
    #p('testSimpleUnification', ret)
    assert ret == [
      {
        'c' : "FF0000"
      }
    ]
  
  def testInverseFunction(self):
    """ this would go into an infinite loop if it weren't for inverse functions
        being explicitly defined."""
    ret = axpress.read_translate("""
      color[html.color] = "00FFFF"
      color[color.invert] = icolor
      icolor[html.color] = _ic
    """)
    #p('testInverseFunction', ret)
    assert ret == [
      {
        'ic' : "FF0000"
      }
    ]
  
  
  def testStringQuery(self):
    ret = axpress.read_translate("""
      x[axpress.is] = "files matching pictures/*.jpg"
      x[file.filename] = _filename
    """)
    assert ret == [
      {
        'filename' : 'pictures/111.jpg',
      }, {
        'filename' : 'pictures/foobar.jpg',
      },
    ]
    
  def testSimpleFreebaseStringQuery(self):
    ret = axpress.read_translate("""
      x[axpress.is] = "Gaviotas"
      x[freebase.guid] = _guid
    """)
    assert ret == [
      {
        'guid' : '9202a8c04000641f800000000c770bee'
      },
    ]

  '''
  MQL is down :(
  def testSimpleFreebaseStringQuery2(self):
    ret = axpress.read_translate("""
      x[axpress.is] = "Nirvana"
      x[freebase.type] = '/music/album'
      x[freebase.mid] = _mid
    """)
    self.assertEquals(ret, [
      {
        'mid' : '/m/0122_j'
      },
    ])
  '''
  
  '''
  MQL is down :(
  def testSimpleFreebaseStringQuery3(self):
    ret = axpress.read_translate("""
      x[axpress.is] = "albums by nirvana"
      x[freebase.mid] = _mid
      x[freebase.name] = _name
    """)
    ##p('ret', ret)
  '''

  '''
  MQL is down :(
  def testSimpleFreebaseStringQuery4(self):
    ret = axpress.read_translate("""
      x[axpress.is] = "band members in Phish"
      x[freebase.mid] = _mid
      x[freebase.name] = _name
    """)
    #p('ret', ret)
  '''
  
  #def testSimpleFreebaseStringQuery5(self):
    #ret = axpress.read_translate("""
      #_x[axpress.is] = "The Queen's birthday"
    #""")
    #p('ret', ret)

  '''
  MQL is down :(
  def testSimpleFreebaseStringQuery6(self):
    ret = axpress.read_translate("""
      x[axpress.is] = "The Queen birthplace"
      x[freebase.mid] = _mid
      x[freebase.name] = _name
    """)
    #p('ret', ret)
  '''

  '''
  # freebase MQL is down :(
  def testSimpleFreebaseStringQuery7(self):
    # looks like somehow the lat and lon are coming in as a lit vars
    # into the weather lookup instead of floats
    ret = axpress.read_translate("""
      weather[axpress.is] = "current weather in bloomington, indiana"
      weather[wunderground.current_temperature] = _current_temperature
    """)
    #p('ret', ret)
  '''
  
  def testStringQuery2(self):
    ret = axpress.read_translate("""
        x[axpress.is] = "add library to todo list"
        x[simple_display.text] = _out
    """)
    
    assert 'library' in ret[0]['out']
    
  #def testStringQuery3(self):
    #ret = axpress.read_translate("""
      #x[axpress.is] = "dew point in bloomington, in today"
      #x[simple_display] = _out
    #""")
    #p('ret', ret)
  
  def testComplexOutputUnification(self):
    try :
      ret = axpress.read_translate("""
          x[test.a] = "hello"
          x[test.d] = _out
      """)
      #p('ret', ret)
      assert False
    except :
      pass

  #def testStringQuery(self):
    #ret = axpress.read_translate("""
      #x[axpress.is] = "files matching pictures/*.jpg"
      #x[display.html] = _html
    #""")
    #p('testStringQuery', ret)
    #assert ret == [
      #{
        #'_html' : "<ul><li>xxx.jpg<li>yyy.jpg</ul>"
      #}
    #]
  
  def testStringQuerySuperSimple(self):
    ret = axpress.read_translate("""
      color[axpress.is] = "red"
      color[html.color] = _c
    """)
    #p('testStringQuerySuperSimple', ret)
    assert ret == [
      {
        'c' : "FF0000"
      }
    ]
  
  def testStringQuerySuperSimple2(self):
    try :
      ret = axpress.read_translate("""
        color[axpress.is] = "red"
        color[html.color] = _c
      """)
      assert False # should not get here
    except :
      pass
    
  def testMultiBranchJoin(self):
    axpress = Axpress()
    
    def make_rule(name, i, o, fn = None):
      axpress.register_translation({
        'name' : name,
        'input' : i,
        'output' : o,
        'function' : fn,
      })
    
    def simple_rule(x, y) :
      make_rule("%s->%s" % (x, y), """
        o[test.%s] = _x
      """ % x, """
        o[test.%s] = _x
      """ % y)
    simple_rule('root', 'b1s1')
    simple_rule('b1s1', 'b1s2')
    simple_rule('root', 'b2s1')
    simple_rule('b2s1', 'b2s2')
    
    def fn(vars) :
      vars['result'] = vars['x'] + vars['y']
    make_rule('result', """
      o[test.b1s2] = _x
      o[test.b2s2] = _y
    """, """
      o[test.result] = _result
    """, fn)
    
    axpress.compiler.compile_translations()
    
    ret = axpress.read_translate("""
      foo[test.root] = 1
      foo[test.result] = _out
    """)
    #p('ret', ret)
  
  def testDayOfWeek(self):
    ret = axpress.read_translate("""
      d[dt.day_of_week_string] = "mon"
      d[dt.day_of_week] = _out
    """)
    #p('testDayOfWeek', ret)
    assert ret == [
      {
        'out' : "monday"
      }
    ]
  
  def testDayOfFridayAt7(self):
    # NOTE: which is this?  7am or 7pm ?
    ret = axpress.read_translate("""
      foo[a.is] = "friday at 7"
      foo[simple_display.text] = _out
    """)
    p('ret', ret)
    assert len(ret) == 1

  def testDayOfTodayAtNoon(self):
    ret = axpress.read_translate("""
      foo[a.is] = "today at noon"
      foo[simple_display.text] = _out
    """)
    assert len(ret) == 1

  def testDayOfTodayAt3(self):
    ret = axpress.read_translate("""
      foo[a.is] = "today at 3"
      foo[simple_display.text] = _out
    """)
    assert len(ret) == 1

  def testLimitedTranslationMatrix(self):
    ret = axpress.read_translate("""
      t[test.xx] = 1
      t[test.yy] = _out
    """)
    assert len(ret) == 1
  
  def testAfter(self):
    # this one doesn't work yet.  See explore_unification.py
    return
    ret = axpress.read_translate("""
      t[test.p1] = 2
      t[test.p2] = p2
      o = axpress.after(p2, p2)
      o[axpress.val] = _out
    """)
    print ret
    assert len(ret) == 1
  
  def testExplode(self):
    # at one point, 3 translation all of which increased the number of result
    # sets was failing
    ret = axpress.read_translate("""
      t[test.t1] = 1
      t[test.t4] = _t4
    """)
    assert len(ret) == 27

  def testNefariousTranslation(self):
    axpress = Axpress()
    
    def ok_fn(vars) :
      vars['nef_in'] = 10 * vars['in']
    axpress.register_translation({
      'name' : 'ok',
      'input' : """
        o[test.in] = _in
      """,
      'output' : """
        o[test.nef_in] = _nef_in
      """,
      'function' : ok_fn,
    })

    def nef_fn(vars) :
      for k in vars.keys() :
        del vars[k]
      vars['nef_out'] = 'nothing to see here'
    axpress.register_translation({
      'name' : 'nef',
      'input' : """
        o[test.nef_in] = _nef_in
      """,
      'output' : """
        o[test.nef_out] = _nef_out
      """,
      'function' : nef_fn,
    })

    axpress.compiler.compile_translations()

    ret = axpress.read_translate("""
      x[test.in] = 1
      x[test.nef_in] = _in
      x[test.nef_out] = _out
    """)
    assert ret == [{
      'in' : 10,
      'out' : 'nothing to see here'
    }]

  def testMissingOut(self) :
    axpress = Axpress()
    
    axpress.register_translation({
      'name' : 'ok',
      'input' : """
        o[test.in] = _in
      """,
      'output' : """
        o[test.out] = _out
      """,
      'function' : lambda x:x,
    })

    axpress.compiler.compile_translations()

    try :
      ret = axpress.read_translate("""
        x[test.in] = 1
        x[test.out] = _out
      """)
      raise Exception('should have erred by now')
    except ValueError, e:
      assert str(e) == "variable 'out' didn't get bound by translation 'ok'"

  def testMultiFunction(self) :
    axpress = Axpress()

    def range_fn(vars) :
      vars['i'] = list(range(vars['from'], vars['to']))
    axpress.register_translation({
      'name' : 'range',
      'input' : """
        x = test.range(_from, _to)
      """,
      'output' : """
        x[a.int] = _i
      """,
      'function' : range_fn,
    })

    def fn(all_vars) :
      for vars in all_vars :
        vars['out'] = vars['in'] * 2
      return [vars for vars in all_vars if vars['out'] % 6 == 0]
    axpress.register_translation({
      'name' : 'multi_fn_test',
      'input' : """
        o[a.int] = _in
      """,
      'output' : """
        o[test.out] = _out
      """,
      'multi_function' : fn,
    })

    axpress.compiler.compile_translations()
    ret = axpress.read_translate("""
      x = test.range(1, 10)
      x[test.out] = _out
    """)
    for row in ret :
      print row

  def testGreedySearch(self) :
    # this query didn't work when I bumped the initial search depth to
    # 6 deep rather than the correct 1 deep.
    # turns out its a different, unrelated bug - might get to keep 6 deep
    # search :)
    ret = axpress.read_translate("""
      x[a.is] = '1 foot in yards'
      x[speech.out] = _out
    """)
    self.assertEquals(ret, [{'out' : '0.333 yards'}])

  def testCloseUnification(self) :
    ret = axpress.read_translate("""
      x[u.feet] = a.float('1')
      x[u.inches] = _out
    """)
    print ret

  def testDiverge(self) :
    ret = axpress.read_translate("""
        f[test.a1] = 1
        f[test.b1] = 2
        f[test.a2b2] = _out
    """)
    #p('ret', ret)
    assert ret == [{
      'out' : 3
    }]

  # def testMultiMerge(self) :
  #   ret = axpress.read_translate("""
  #       z = math.mul(u.unit(1, u.meter), u.unit(1, u.meter))
  #       z = u.unit(_val, _unit)
  #   """)
  #   p('ret', ret)

if __name__ == "__main__" :
  import atexit
  def at() :
    print 'cum_comp_time', axpress.cum_comp_time
    print 'cum_eval_time', axpress.cum_eval_time
  atexit.register(at)

  #print '<root>'
  #import cProfile
  #cProfile.run('unittest.main()')
  try :
    unittest.main()
  except Exception, e:
    print e
  #print '</root>'

