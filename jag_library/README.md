# **Library Module (JAG Library) for Odoo 18**

This module customizes Odoo 18 to enable advanced library management, treating books as a special class of products and managing authors and publishers as specific contacts. It adds a dedicated "Library" application menu for easy access to all library-related features.

## **✨ Key Features**

* **Dedicated Library Application**: A new top-level "Library" menu provides centralized access to the Book Catalog and Genres.
* **Book Management as Products**: Adds multiple tabs and detailed fields for products marked as "Is a book".
* **Specialized Contacts**: Allows classifying contacts as **Authors** (if they are individuals) or **Publishers** (if they are companies).
* **Enhanced Book Catalog**:
  * **Custom Kanban View**: An attractive and functional kanban view for the book catalog, displaying the cover, author(s), publisher, genres, and page count.
  * **Detailed Fields**: ISBN, publication details, binding, edition, synopsis, number of pages, and more.
  * **Personal Tracking**: Fields for tracking reading progress, including start/end dates, personal rating, and reading notes.
  * **Physical Book Details**: Track the book's condition (new, used, etc.) and its physical location in the warehouse (computed automatically).
  * **ISBN Validation**: Includes a button to verify if the ISBN-13 format is correct.
  * **Image Management**: Separate fields for the front and back cover images.
* **Hierarchical Genres**: Create and manage a hierarchical structure of literary genres for detailed classification.
* **Contact Integration**:
  * Author records show all the books they have written.
  * Publisher records show all the books they have published.
* **Filters and Searches**: New filters in product and contact views to quickly find books, authors, or publishers.
* **Security**: Introduces two new permission groups to control access to library management:
  * **Library User**: Read-only permissions.
  * **Library Manager**: Full create, read, update, and delete (CRUD) permissions.
* **Automated Tests**: Includes a comprehensive test suite to ensure module stability and correctness.

## **🔧 Models and Views**

### **Modified Models**

* product.template:
  * is\_book (Boolean): Marks a product as a book.
  * Adds numerous fields like isbn, publication\_date, publisher\_id, author\_ids, genre\_ids, synopsis, rating, condition, location, etc.
  * Includes SQL constraints to ensure data integrity (e.g., unique ISBN, publication date cannot be in the future).
* res.partner:
  * is\_author (Boolean): Marks a contact (person) as an author.
  * is\_publisher (Boolean): Marks a contact (company) as a publisher.
  * authored\_book\_ids (Many2many): Books written by the author.
  * published\_book\_ids (One2many): Books published by the publisher.

### **New Models**

* product.book.genre:
  * Model for creating hierarchical book genres and subgenres.

### **Key Views**

* **Kanban View for Books**: product\_template\_kanban\_view\_books (highly customized).
* **Extended Product Form**: Multiple new tabs ("Book Information", "Images", "Reading Notes") on the product form.
* **Extended Contact Form**: Options to mark as author/publisher and a tab to view their books.
* **Views for Genres**: List and form views to manage genres, including a list of associated books.

## **🚀 Installation**

1. Clone or download this repository.
2. Copy the jag\_library folder into your Odoo addons directory.
3. Restart the Odoo service.
4. Go to Apps in Odoo, search for "JAG Library", and install it.

## **📖 Usage**

### **1\. Navigate to the Library App**

* Click on the "Library" icon from the main Odoo applications menu.

### **2\. Create an Author or a Publisher**

* Go to the **Contacts** application.
* Create a new contact.
* If it is an individual, you will see the **"Is author"** option. Check it.
* If it is a company, you will see the **"Is publisher"** option. Check it.

### **3\. Manage Book Genres**

* Go to **Library \> Book Genres**.
* Here you can create, edit, and organize genres in a parent-child structure.

### **4\. Add a Book to the Catalog**

* Go to **Library \> Book Catalog**.
* Create a new product.
* Enable the **"Is a book"** option at the top of the form.
* This will reveal several new tabs. Fill in the details in the **"Book Information"**, **"Images"**, and **"Reading Notes"** tabs.
* You can use the **"Verify ISBN"** button to check its validity.

## **🔐 Security**

The module creates two user groups that you will find in **Settings \> Users & Companies \> Groups**:

* **Services/Library / User**: Users in this group can read library information but cannot modify it.
* **Services/Library / Manager**: Users in this group have full control over books and genres. By default, the system administrator belongs to this group.

## **✍️ Author**

**Javier Antó García**

* Email: [hola@javieranto.com](mailto:hola@javieranto.com)

## **📄 License**

This module is distributed under the **GNU GENERAL PUBLIC LICENSE** license. See the LICENSE file for more details.

zz
