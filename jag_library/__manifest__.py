{
    "name": "Library Management",
    "summary": "Manage library catalog",
    "author": " Javier Antó Garcia, JAG",
    "license": "AGPL-3",
    "website": "https://github.com/javierobcn/jag_library",
    "version": "18.0.0.0.1",
    "category": "Services/Library",
    "depends": ["base", "web", "product", "stock"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/book_genre_views.xml",
        "views/product_template.xml",
        "views/jag_library_menu.xml",
    ],
    "application": True,
}
