# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models

GMAPS_LANG_LOCALIZATION = [
    ('af', 'Afrikaans'),
    ('ja', 'Japanese'),
    ('sq', 'Albanian'),
    ('kn', 'Kannada'),
    ('am', 'Amharic'),
    ('kk', 'Kazakh'),
    ('ar', 'Arabic'),
    ('km', 'Khmer'),
    ('ar', 'Armenian'),
    ('ko', 'Korean'),
    ('az', 'Azerbaijani'),
    ('ky', 'Kyrgyz'),
    ('eu', 'Basque'),
    ('lo', 'Lao'),
    ('be', 'Belarusian'),
    ('lv', 'Latvian'),
    ('bn', 'Bengali'),
    ('lt', 'Lithuanian'),
    ('bs', 'Bosnian'),
    ('mk', 'Macedonian'),
    ('bg', 'Bulgarian'),
    ('ms', 'Malay'),
    ('my', 'Burmese'),
    ('ml', 'Malayalam'),
    ('ca', 'Catalan'),
    ('mr', 'Marathi'),
    ('zh', 'Chinese'),
    ('mn', 'Mongolian'),
    ('zh-CN', 'Chinese (Simplified)'),
    ('ne', 'Nepali'),
    ('zh-HK', 'Chinese (Hong Kong)'),
    ('no', 'Norwegian'),
    ('zh-TW', 'Chinese (Traditional)'),
    ('pl', 'Polish'),
    ('hr', 'Croatian'),
    ('pt', 'Portuguese'),
    ('cs', 'Czech'),
    ('pt-BR', 'Portuguese (Brazil)'),
    ('da', 'Danish'),
    ('pt-PT', 'Portuguese (Portugal)'),
    ('nl', 'Dutch'),
    ('pa', 'Punjabi'),
    ('en', 'English'),
    ('ro', 'Romanian'),
    ('en-AU', 'English (Australian)'),
    ('ru', 'Russian'),
    ('en-GB', 'English (Great Britain)'),
    ('sr', 'Serbian'),
    ('et', 'Estonian'),
    ('si', 'Sinhalese'),
    ('fa', 'Farsi'),
    ('sk', 'Slovak'),
    ('fi', 'Finnish'),
    ('sl', 'Slovenian'),
    ('fil', 'Filipino'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('es-419', 'Spanish (Latin America)'),
    ('fr-CA', 'French (Canada)'),
    ('sw', 'Swahili'),
    ('gl', 'Galician'),
    ('sv', 'Swedish'),
    ('ka', 'Georgian'),
    ('ta', 'Tamil'),
    ('de', 'German'),
    ('te', 'Telugu'),
    ('el', 'Greek'),
    ('th', 'Thai'),
    ('gu', 'Gujarati'),
    ('tr', 'Turkish'),
    ('iw', 'Hebrew'),
    ('uk', 'Ukrainian'),
    ('hi', 'Hindi'),
    ('ur', 'Urdu'),
    ('hu', 'Hungarian'),
    ('uz', 'Uzbek'),
    ('is', 'Icelandic'),
    ('vi', 'Vietnamese'),
    ('id', 'Indonesian'),
    ('zu', 'Zulu'),
    ('it', 'Italian'),
]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_region_selection(self):
        country_ids = self.env['res.country'].search([])
        values = [(country.code, country.name) for country in country_ids]
        return values

    google_maps_view_api_key = fields.Char(
        string='Google Maps View Api Key',
        config_parameter='google_map_route.api_key')
    google_maps_lang_localization = fields.Selection(
        selection=GMAPS_LANG_LOCALIZATION,
        string='Google Maps Language Localization',
        config_parameter='google_map_route.lang_localization',default='en')
    google_maps_region_localization = fields.Selection(
        selection=get_region_selection,
        string='Google Maps Region Localization',
        config_parameter='google_map_route.region_localization',default='US')
    google_maps_theme = fields.Selection(
        selection=[('default', 'Default'),
                   ('aubergine', 'Aubergine'),
                   ('night', 'Night'),
                   ('dark', 'Dark'),
                   ('retro', 'Retro'),
                   ('silver', 'Silver')],
        string='Map theme',default='default',
        config_parameter='google_map_route.theme')
    google_maps_libraries = fields.Char(
        string='Libraries',
        config_parameter='google_map_route.libraries')
    google_autocomplete_lang_restrict = fields.Boolean(
        string='Google Autocomplete Language Restriction',
        config_parameter='google_map_route.autocomplete_lang_restrict')

    @api.onchange('google_maps_lang_localization')
    def onchange_lang_localization(self):
        if not self.google_maps_lang_localization:
            self.google_maps_region_localization = ''
