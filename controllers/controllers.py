# -*- coding: utf-8 -*-
from odoo import http

# class NbetCustom(http.Controller):
#     @http.route('/nbet_custom/nbet_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nbet_custom/nbet_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nbet_custom.listing', {
#             'root': '/nbet_custom/nbet_custom',
#             'objects': http.request.env['nbet_custom.nbet_custom'].search([]),
#         })

#     @http.route('/nbet_custom/nbet_custom/objects/<model("nbet_custom.nbet_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nbet_custom.object', {
#             'object': obj
#         })