from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

# Import database exceptions directly from psycopg2
from psycopg2 import IntegrityError
from psycopg2.errors import CheckViolation


class TestBook(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # It's good practice to create a clean test environment
        # and run it as a user with appropriate permissions (admin in this case).
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)

        # Create test data
        self.author_cervantes = self.env["res.partner"].create(
            {"name": "Miguel de Cervantes", "is_author": True, "company_type": "person"}
        )
        self.author_reis = self.env["res.partner"].create(
            {"name": "Daniel Reis", "is_author": True, "company_type": "person"}
        )
        self.author_packt_team = self.env["res.partner"].create(
            {"name": "Packt Community", "is_author": True, "company_type": "person"}
        )
        self.publisher_planeta = self.env["res.partner"].create(
            {
                "name": "Editorial Planeta",
                "is_publisher": True,
                "company_type": "company",
            }
        )
        self.publisher_packt = self.env["res.partner"].create(
            {
                "name": "Packt Publishing",
                "is_publisher": True,
                "company_type": "company",
            }
        )
        self.genre_novel = self.env["product.book.genre"].create({"name": "Novel"})

        # Main model to test
        self.Book = self.env["product.template"]

        # Test records
        self.book_odoo = self.Book.create(
            {
                "name": "Odoo Development Essentials",
                "isbn": "978-1784392796",
                "number_of_pages": 214,
                "copies": 1,
                "rating": "5",
                "publication_date": "2022-01-01",
                "author_ids": [(6, 0, [self.author_reis.id])],
                "publisher_id": self.publisher_packt.id,
                "genre_ids": [(6, 0, [self.genre_novel.id])],
            }
        )
        self.book_quijote = self.Book.create(
            {
                "name": "Don Quijote de la mancha",
                "isbn": "9788491050759",
                "author_ids": [(6, 0, [self.author_cervantes.id])],
                "publisher_id": self.publisher_planeta.id,
            }
        )

    # --- EXISTING TESTS (for reference) ---

    def test_book_create(self):
        "Test 1: New books are active by default."
        self.assertEqual(self.book_odoo.active, True)
        self.assertEqual(self.book_quijote.active, True)

    def test_check_isbn(self):
        "Test 2: Check that a valid ISBN is accepted."
        # check_isbn() is a method that returns a boolean.
        self.assertTrue(self.book_odoo.check_isbn())
        self.assertTrue(self.book_quijote.check_isbn())

    # --- NEW TESTS ---

    def test_invalid_isbn(self):
        "Test 3: An invalid ISBN should not be accepted."
        # We use `assertRaises` to verify that Odoo raises an exception
        # when we try to do something that is not allowed.
        # The `with` statement ensures the exception occurs within this block.
        with self.assertRaises(ValidationError, msg="Should fail with an invalid ISBN"):
            self.Book.create({"name": "Book with Bad ISBN", "isbn": "123-456"})

    def test_sql_constraint_unique_isbn(self):
        "Test 4: Test the SQL constraint that the ISBN must be unique."
        # The `_sql_constraints` are triggered at the database level (PostgreSQL).
        # This causes a `IntegrityError` from psycopg2, which Odoo wraps.
        with self.assertRaises(
            IntegrityError,
            msg="It should not be possible to create a book with a duplicate ISBN.",
        ):
            self.Book.create(
                {
                    "name": "Duplicate Book",
                    "isbn": "978-1784392796",  # ISBN from the Odoo book
                }
            )

    def test_book_relations(self):
        "Test 5: Verify that the relations (author, publisher, genre) are assigned correctly."
        # Check the relations for the first book
        self.assertEqual(self.book_odoo.publisher_id, self.publisher_packt)
        self.assertIn(self.author_reis, self.book_odoo.author_ids)
        self.assertIn(self.genre_novel, self.book_odoo.genre_ids)
        self.assertEqual(
            len(self.book_odoo.author_ids), 1, "Odoo book should have a single author."
        )

        # Check the relations for the second book
        self.assertEqual(self.book_quijote.publisher_id, self.publisher_planeta)
        self.assertIn(self.author_cervantes, self.book_quijote.author_ids)
        self.assertEqual(
            len(self.book_quijote.author_ids),
            1,
            "Don Quijote should have a single author.",
        )

    def test_publication_date_in_future_constraint(self):
        "Test 6: Test the constraint that prevents future publication dates."
        # The log indicates that this is a DB constraint (CheckViolation),
        # not a Python validation (ValidationError).
        with self.assertRaises(
            CheckViolation, msg="The publication date cannot be in the future."
        ):
            self.Book.create(
                {
                    "name": "Future Book",
                    "isbn": "978-1234567890",
                    "publication_date": "2999-12-31",
                }
            )

    def test_book_with_multiple_authors(self):
        "Test 7: Create a book with multiple authors and verify the assignment."
        book_multi_author = self.Book.create(
            {
                "name": "Multi-Author Book",
                "isbn": "978-9876543217",  # Corrected to a valid ISBN-13
                "author_ids": [
                    (6, 0, [self.author_reis.id, self.author_packt_team.id])
                ],
            }
        )
        # Check that the number of authors is correct
        self.assertEqual(
            len(book_multi_author.author_ids), 2, "The book should have 2 authors."
        )
        # Check that both authors are in the list
        self.assertIn(self.author_reis, book_multi_author.author_ids)
        self.assertIn(self.author_packt_team, book_multi_author.author_ids)

    def test_computed_publication_year(self):
        "Test 8: Verify that the publication year is computed correctly."
        # The `publication_year` field is computed from `publication_date`.
        self.assertEqual(self.book_odoo.publication_year, 2022)

    def test_onchange_partner_type(self):
        "Test 9: Verify the onchange logic for the partner type."
        # 1. If an author ('person') is changed to a company, they should no longer be an author.
        self.author_cervantes.company_type = "company"
        self.author_cervantes._onchange_company_type_set_partner_type()
        self.assertFalse(
            self.author_cervantes.is_author, "A company cannot be an author."
        )

        # 2. If a publisher ('company') is changed to an individual, it should no longer be a publisher.
        self.publisher_packt.company_type = "person"
        self.publisher_packt._onchange_company_type_set_partner_type()
        self.assertFalse(
            self.publisher_packt.is_publisher, "A person cannot be a publisher."
        )

    def test_button_check_isbn_action(self):
        "Test 10: Verify that the check ISBN button action is correct."
        # The method should return a notification action dictionary if the ISBN is valid.
        action = self.book_odoo.button_check_isbn()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "info")
