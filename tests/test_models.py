# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()

        # Set the ID of the product object to None and then call the create() method on the product.
        product.id = None
        product.create()

        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)

        # Fetch the product back from the system using the product ID and store it in found_product
        found_product = Product.find(product.id)

        # Assert that the properties of the found_product match with the properties
        # of the original product object, such as id, name, description and price.
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()

        # Set the ID of the product object to None and then call the create() method on the product.
        product.id = None
        product.create()

        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)

        # Update the product in the system with the new property values using the update() method.
        product.description = "testing"
        original_id = product.id
        product.update()

        # Assert that the id is same as the original id but description property of the product object has
        # been updated correctly after calling the update() method.
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")

        # Fetch all the product back from the system.
        products = Product.all()

        # Assert the length of the products list is equal to 1 to verify that after updating the product,
        # there is only one product in the system.
        self.assertEqual(len(products), 1)

        # Assert that the fetched product has id same as the original id.
        self.assertEqual(products[0].id, original_id)

        # Assert that the fetched product has the updated description.
        self.assertEqual(products[0].description, "testing")

    def test_delete_a_product(self):
        """It should Delete a Product"""

        product = ProductFactory()

        # Call the create() method on the product to save it to the database.
        product.create()

        # Assert  if the length of the list returned by Product.all() is equal
        # to 1, to verify that after creating a product and saving it to the database,
        # there is only one product in the system.
        self.assertEqual(len(Product.all()), 1)

        # Call the delete() method on the product object, to remove the product from the database.
        product.delete()

        # Assert if the length of the list returned by Product.all() is now equal to 0,
        # indicating that the product has been successfully deleted from the database.
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()

        # Assert if the products list is empty, indicating that there are no products in
        # the database at the beginning of the test case.
        self.assertEqual(len(products), 0)

        # Use for loop to create five Product objects using a ProductFactory() and call
        # the create() method on each product to save them to the database.
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Fetch all products from the database again using product.all()
        products = Product.all()

        # Assert if the length of the products list is equal to 5, to verify that
        # the five products created in the previous step have been successfully
        # added to the database.
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)

        # Use a for loop to iterate over the products list and call the create() method
        # on each product to save them to the database.
        for product in products:
            product.create()

        # Retrieve the name of the first product in the products list.
        first_product_name = products[0].name

        # Use the variable called count to hold the number of products
        # that match the first product name.
        count = len([product for product in products if product.name == first_product_name])

        # Call the find_by_name() method on the Product class to retrieve products from the
        # database that have the specified name.
        products_by_name = Product.find_by_name(first_product_name)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_name.count(), count)

        # Use a for loop to iterate over the found products and assert that each product's
        # name matches the expected name, to ensure that all the retrieved products have the
        # correct name.
        for product in products_by_name:
            self.assertEqual(product.name, first_product_name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)

        # Use a for loop to iterate over the products list and call the create() method on each
        # product to save them to the database.
        for product in products:
            product.create()

        # Retrieve the availability of the first product in the products list.
        first_availability = products[0].available

        # Use a list comprehension to filter the products based on their availability and then use
        # len() to calculate the length of the filtered list, and use the variable called count to
        # hold the number of products that have the specified availability.
        count = len([product for product in products if product.available == first_availability])

        # Call the find_by_availability() method on the Product class to retrieve products from the database
        # that have the specified availability.
        products_by_availability = Product.find_by_availability(first_availability)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_availability.count(), count)

        # Use a for loop to iterate over the found products and assert that each product's availability
        # matches the expected availability, to ensure that all the retrieved products have the correct
        # availability.
        for product in products_by_availability:
            self.assertEqual(product.available, first_availability)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)

        # Use a for loop to iterate over the products list and call the create() method on each product to
        # save them to the database.
        for product in products:
            product.create()

        # Retrieve the category of the first product in the products list.
        category = products[0].category

        # Use a list comprehension to filter the products based on their category and then use len()
        # to calculate the length of the filtered list, and use the variable called count to hold the
        # number of products that have the specified category.
        count = len([product for product in products if product.category == category])

        # Call the find_by_category() method on the Product class to retrieve products from the database that
        # have the specified category.
        products_by_category = Product.find_by_category(category)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_category.count(), count)

        # Use a for loop to iterate over the found products and assert that each product's category matches
        # the expected category, to ensure that all the retrieved products have the correct category.
        for product in products_by_category:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(10)

        # set a few elements with the same price
        price = 42.0
        products[0].price = price
        products[2].price = price
        products[6].price = price

        # Use a for loop to iterate over the products list and call the create() method on each product to
        # save them to the database.
        for product in products:
            product.create()

        # Use a list comprehension to filter the products based on their price and then use len()
        # to calculate the length of the filtered list, and use the variable called count to hold the
        # number of products that have the specified price.
        count = len([product for product in products if product.price == price])

        # Call the find_by_price() method on the Product class to retrieve products from the database that
        # have the specified price.
        products_by_price = Product.find_by_price(str(price))

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_price.count(), count)

        # Use a for loop to iterate over the found products and assert that each product's price matches
        # the expected price, to ensure that all the retrieved products have the correct price.
        for product in products_by_price:
            self.assertEqual(product.price, price)

    # Sad path tests for complete coverage

    def test_update_with_empty_id(self):
        """It should not Update a Product without an id"""
        product = ProductFactory()

        # Set the ID of the product object to None and then call the create() method on the product.
        product.id = None
        product.create()

        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)

        # Update the product in the system with the new property values using the update() method.
        product.description = "testing"
        product.id = None

        # Assert that a DataValidationError is raised as a result of the id set to None
        self.assertRaises(DataValidationError, product.update)

    def test_deserialize(self):
        """It should not deserialize a Product with an improper input dictionary"""
        product = ProductFactory()

        # Assert that a DataValidationError is raises when an empty dictionary is
        # passed in for deserialization
        self.assertRaises(DataValidationError, product.deserialize, {})

        # load dictionary with values from the product factory
        product_dict = product.serialize()

        # set the available key to an invalid type
        product_dict["available"] = "Not Valid"

        # Assert that a DataValidationError is raised when a dictionary with an invalid
        # available type is passed in for deserialization
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

        # Assert that a DataValidationError is raised when a String is passed in instead
        # of an input dictionary
        self.assertRaises(DataValidationError, product.deserialize, "Test")
