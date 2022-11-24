from odoo import api, fields, models

class Person(models.Model):
    _name= 'mod.prueba.person'
    _description = 'modulo de prueba'

    sequence = fields.Integer("sequence", default=1)
    firstname = fields.Char(string='firstname', required=True)
    lastname = fields.Char(string='lastname')
    age = fields.Integer("Edad")
    create_date = fields.Datetime(string='Fecha de creacion', default=lambda self: fields.Datetime.now())
    status = fields.Selection(
        [('active', 'Activo'), ('deleted', 'Eliminado'), ('deactivate', 'Desactivado')], string='Status', required=True,
        default='active')
    # status = fields.Boolean(string='Habilitado?', default=True)
    friend_id = fields.Many2one('res.partner', string="Contacto, Tercero")