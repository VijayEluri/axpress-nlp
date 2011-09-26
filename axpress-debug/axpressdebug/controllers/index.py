# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from axpressdebug.lib.base import BaseController, render

from SimpleSPARQL import p

log = logging.getLogger(__name__)

class IndexController(BaseController):

	def debug(self):
		c.query = request.params.get('query') or ""
		c.ret = ""
		c.debug_html = ""

		if c.query :
			c.ret = g.axpress.read_translate(c.query)
			c.debug_html = g.axpress.compiler.debug_str
		
		return render('debug.mako')