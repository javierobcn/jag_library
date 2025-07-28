from odoo.tests.common import TransactionCase


class TestBook(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.book = self.env["jag.library.book"]
        self.book1 = self.book.create(
            {"name": "Odoo Development Essentials", "isbn": "879-1-78439-279-6"}
        )
        self.book2 = self.book.create(
            {"name": "Don Quijote de la mancha", "isbn": "9788491050759"}
        )

    def test_book_create(self):
        "New Books are active by default"
        self.assertEqual(self.book1.active, True)
        self.assertEqual(self.book2.active, True)

    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.book1.check_isbn)
        self.assertTrue(self.book2.check_isbn)
