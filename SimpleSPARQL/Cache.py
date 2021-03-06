import time, copy
from PrettyQuery import *
import Namespaces
n = Namespaces.globalNamespaces()
n.bind('cache', '<http://dwiel.net/axpress/cache/0.1/>')

class Cache :
	def __init__(self, sparql) :
		self.sparql = sparql
	
	def call(self, translation, vars) :
		# TODO: make this read query check for the most recent of multiple cache
		#   values.  Or double check/prove that it isnt necessary
		ret = self.sparql.read([{
			n.cache.translation : translation['name'],
			n.cache.vars : vars,
			n.cache.value : None,
			n.cache.date : None,
		}])
		if ret[n.sparql.status] == n.sparql.ok and \
		   ret[n.sparql.result] and \
			 ret[n.sparql.result][0][n.cache.date] + translation['expiration_length'] > time.time() :
			return ret[n.sparql.result][0][n.cache.value]
		else :
			old_vars = copy.copy(vars)
			ret = translation['function'](vars)
			if ret == None :
				ret = vars
			if type(ret) is not list :
				ret = [ret]
			# TODO: error check result of write
			self.sparql.write([
				[n.bnode.x, n.cache.value, ret],
				[n.bnode.x, n.cache.date, time.time()],
				[n.bnode.x, n.cache.translation, translation['name']],
				[n.bnode.x, n.cache.vars, old_vars]
			], var, n.tvar)
			return ret
			
			#self.sparql.write({
				#n.sparql.create : n.sparql.unless_exists,
				#n.cache.value : ret,
				#n.cache.date : time.time(),
				#n.cache.translation : translation['name'],
				#n.cache.vars : vars,
			#})




