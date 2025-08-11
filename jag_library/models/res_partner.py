# Copyright 2025 Javier Antó Garcia <hola@javieranto.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_author = fields.Boolean(string="Is author")
    is_publisher = fields.Boolean(string="Is publisher")

    authored_book_ids = fields.Many2many(
        "product.template",
        "res_partner_product_template_rel",
        "partner_id",
        "book_id",
        string="Authored Books",
        domain=[("is_book", "=", True)],
    )

    published_book_ids = fields.One2many(
        "product.template",
        "publisher_id",
        string="Published Books",
    )

    @api.onchange("company_type")
    def _onchange_company_type_set_partner_type(self):
        if self.company_type == "person":
            self.is_publisher = False
        elif self.company_type == "company":
            self.is_author = False
