from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_book = fields.Boolean(string="Is a book")
    isbn = fields.Char("ISBN")
    number_of_pages = fields.Integer()
    copies = fields.Integer(default=1)
    rating = fields.Selection(
        selection=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
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
    condition = fields.Selection(
        [
            ("new", _("New")),
            ("good", _("Good")),
            ("used", _("Used")),
            ("damaged", _("Damaged")),
        ],
        default="new",
    )

    @api.depends("publication_date")
    def _compute_publication_year(self):
        for book in self:
            if book.publication_date:
                book.publication_year = book.publication_date.year

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

    #     @api.depends("publisher_id.country_id")
    #     def _compute_publisher_country(self):
    #         for book in self:
    #             book.publisher_country_id = book.publisher_id.country_id

    #     def _inverse_publisher_country(self):
    #         for book in self:
    #             book.publisher_id.country_id = book.publisher_country_id

    #     def _search_publisher_country(self, operator, value):
    #         return [("publisher_id.country_id", operator, value)]

    #     publisher_country_id = fields.Many2one(
    #         "res.country",
    #         string="Publisher Country",
    #         compute="_compute_publisher_country",
    #         inverse="_inverse_publisher_country",
    #         search="_search_publisher_country",
    #     )


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
