# Copyright 2025 Javier Antó Garcia <hola@javieranto.com>
# License AGPL-3.0 or later (https://ww

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_book = fields.Boolean(string="Is a book")
    isbn = fields.Char("ISBN")
    number_of_pages = fields.Integer()
    copies = fields.Integer(default=1)
    rating = fields.Selection(
        [
            ('0', 'Not Rated'),
            ('1', 'Very Bad'),
            ('2', 'Fair'),
            ('3', 'Good'),
            ('4', 'Very Good'),
            ('5', 'Masterpiece')
        ],
        string='Rating',
        default='0'
    )
    date_start_reading = fields.Date()
    date_end_reading = fields.Date()
    publication_year = fields.Integer(
        compute="_compute_publication_year",
        store=True,
    )
    publication_date = fields.Date()
    publisher_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_publisher", "=", True)],
    )
    author_ids = fields.Many2many(
        "res.partner",
        "res_partner_product_template_rel",
        "book_id",
        "partner_id",
        domain=[("is_author", "=", True)],
    )
    genre_ids = fields.Many2many(
        "product.book.genre",
        index=True,
    )
    language = fields.Many2one("res.lang", domain="[]")
    binding = fields.Selection(
        [
            ("hardcover", _("Hard cover")),
            ("paperback", _("paperback")),
            ("spiral", _("Spiral")),
            ("ebook", _("eBook")),
            ("other", _("Other")),
        ],
    )
    edition = fields.Char()
    synopsis = fields.Html()
    reading_notes = fields.Html()
    image_back_cover_1920 = fields.Image(
        "Back Cover", max_width=1920, max_height=1920
    )
    image_back_cover_1024 = fields.Image(
        "Back Cover 1024",
        related="image_back_cover_1920",
        max_width=1024,
        max_height=1024,
        store=True,
    )
    image_back_cover_512 = fields.Image(
        "Back Cover 512",
        related="image_back_cover_1920",
        max_width=512,
        max_height=512,
        store=True,
    )
    image_back_cover_256 = fields.Image(
        "Back Cover 256",
        related="image_back_cover_1920",
        max_width=256,
        max_height=256,
        store=True,
    )
    image_back_cover_128 = fields.Image(
        "Back Cover 128",
        related="image_back_cover_1920",
        max_width=128,
        max_height=128,
        store=True,
    )
    condition = fields.Selection(
        [
            ("new", _("New")),
            ("good", _("Good")),
            ("used", _("Used")),
            ("damaged", _("Damaged")),
        ],
        default="new",
    )
    location = fields.Char(
        string="Location",
        compute="_compute_location",
        store=True,
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help="Determines the order in the list view. The lowest number is displayed first."
    )

    @api.depends("publication_date")
    def _compute_publication_year(self):
        for book in self:
            if book.publication_date:
                book.publication_year = book.publication_date.year

    @api.depends(
        "product_variant_ids.stock_quant_ids.location_id",
        "product_variant_ids.stock_quant_ids.quantity",
        "qty_available"
    )
    def _compute_location(self):
        for book in self:
            # Filter quants to only include those in 'internal' locations
            # with a positive quantity.
            quants = book.product_variant_ids.mapped("stock_quant_ids")
            quants_in_internal_locs = quants.filtered(
                lambda q: q.location_id.usage == "internal" and q.quantity > 0
            )
            # Get the unique display names of these locations
            locations = quants_in_internal_locs.mapped(
                "location_id.display_name"
            )
            # Join the unique location names
            book.location = ", ".join(list(set(locations)))

    _sql_constraints = [
        (
            "library_book_name_date_uq",
            "UNIQUE (name, publication_date)",
            _("Book title and publication date must be unique."),
        ),
        (
            "library_book_check_date",
            "CHECK (publication_date <= current_date)",
            _("Publication date must not be in the future."),
        ),
        ("isbn_uniq", "UNIQUE (isbn)", _("ISBN must be unique.")),
    ]

    @api.constrains("isbn")
    def _constrain_isbn_valid(self):
        for book in self:
            if book.isbn and not book.check_isbn():
                raise ValidationError(
                    _("ISBN {} is invalid").format(book.isbn),
                )

    def check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [
                a * b
                for a, b in zip(
                    digits[:12],
                    ponderations,
                    strict=False,
                )
            ]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check
        return False

    def button_check_isbn(self):
        result = False
        for book in self:
            if not book.isbn:
                raise ValidationError(
                    _("Provide an ISBN for {} ").format(book.name),
                )
            if book.isbn and not book.check_isbn():
                raise ValidationError(
                    _("{} ISBN is invalid").format(book.isbn),
                )
        result = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "ISBN",
                "message": "ISBN OK!",
                "type": "info",
                "sticky": True,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        return result

    publisher_country_id = fields.Many2one(
        "res.country",
        string="Publisher Country",
        related="publisher_id.country_id",
        readonly=False,
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    def button_check_isbn(self):
        """
        Delegates the ISBN check to the product template.
        The button is on the product.product form, but the logic and fields
        (like ISBN) are on the product.template.
        """
        return self.product_tmpl_id.button_check_isbn()


class ProductBookGenre(models.Model):
    _name = "product.book.genre"
    _description = "Book Genre"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "complete_name"

    name = fields.Char(index=True, required=True)
    complete_name = fields.Char(
        compute="_compute_complete_name", recursive=True, store=True
    )
    parent_id = fields.Many2one(
        _name, "Parent Category", index=True, ondelete="cascade"
    )
    parent_path = fields.Char(index=True)
    book_ids = fields.Many2many("product.template")
    child_ids = fields.One2many(_name, "parent_id", "Child Categories")
    notes = fields.Text()
    color = fields.Integer()

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = (
                    f"{category.parent_id.complete_name} / {category.name}"
                )
            else:
                category.complete_name = category.name
