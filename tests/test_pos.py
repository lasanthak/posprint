import unittest
import sys
import os

# Add the parent directory to sys.path so we can import formatter_util
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pos

class TestPosCharge(unittest.TestCase):

    def test_PosCharge_init(self):
        # valid cases
        pos.PosCharge(name="Fixed Fee", amount=10.0, fixed=True)
        pos.PosCharge(name="Fixed Fee", amount=0.5, fixed=True)
        pos.PosCharge(name="Fixed Fee", amount=0.0, fixed=True)
        pos.PosCharge(name="Service Fee", amount=0.7, fixed=False)
        pos.PosCharge(name="Service Fee", amount=1.0, fixed=False)
        pos.PosCharge(name="Service Fee", amount=0.0, fixed=False)

        invalid_cases = [
            ("", 10.0, True),                   # Empty name
            ("This name is way too long", 10.0, True), # Name too long
            ("Fixed Charge", -5.0, True),         # Negative fixed amount
            ("Service Charge", 1.5, False),         # Rate > 1.0
            ("Service Charge", -0.1, False),        # Rate < 0.0
        ]
        for name, amount, fixed in invalid_cases:
            with self.subTest(name=name, amount=amount, fixed=fixed):
                with self.assertRaises(AssertionError):
                    pos.PosCharge(name=name, amount=amount, fixed=fixed)


class TestPosChargeItem(unittest.TestCase):

    def test_PosChargeItem_init(self):
        c = pos.PosCharge(name="Tax", amount=0.1, fixed=False)
        pos.PosChargeItem(charge=c, count=2, base_amount=58.60) # valid
        
        invalid_cases = [
            (c, 0, 5.0),   # Count = 0
            (c, -1, 5.0),  # Negative count
            (c, 2, -5.0),  # Negative base_amount
        ]
        for c, count, base_amount in invalid_cases:
            with self.subTest(count=count, base_amount=base_amount):
                with self.assertRaises(AssertionError):
                    pos.PosChargeItem(charge=c, count=count, base_amount=base_amount)
    
    def test_PosChargeItem_total_amount(self):
        c_rate = pos.PosCharge(name="Tax", amount=0.125, fixed=False)
        self.assertEqual(pos.PosChargeItem(charge=c_rate, count=2, base_amount=100.0).total_amount, 25.0) # 12.5% of 100 * 2
        c_fixed = pos.PosCharge(name="Service Fee", amount=5.0, fixed=True)
        self.assertEqual(pos.PosChargeItem(charge=c_fixed, count=3, base_amount=5.0).total_amount, 15.0) # 5 * 3

class TestPosItem(unittest.TestCase):
    
    def test_PosItem_init(self):
        pos.PosItem(name="Apple Juice", price=250.00, count=2, note="Special Request") # valid

        invalid_cases = [
            ("Milk", -150.00, 1),  # Negative price
            ("Bread", 50.00, 0),   # Count = 0
            ("Eggs", 30.00, -1),   # Negative count
        ]
        for name, price, count in invalid_cases:
            with self.subTest(name=name, price=price, count=count):
                with self.assertRaises(AssertionError):
                    pos.PosItem(name=name, price=price, count=count)
    
    def test_PosItem_total_price(self):
        self.assertEqual(pos.PosItem(name="Apple Juice", price=250.00, count=2).total_price, 500.00)
    
    def test_PosItem_print48(self):
        self.assertEqual(
            pos.PosItem(name="Milk", price=150.00).print48(), 
            [f" Milk                         1  150.00  150.00 "])
        self.assertEqual(
            pos.PosItem(name="Pan Cake", price=16.50, count=3).print48(), 
            [f" Pan Cake                     3   16.50   49.50 "])
        self.assertEqual(
            pos.PosItem(name="Pan Cake and Cheese and Avocado", price=16.50, count=3).print48(), 
            [f" Pan Cake and Cheese and Avo  3   16.50   49.50 "])
        self.assertEqual(
            pos.PosItem(name="Milk", price=150.00, count=9999).print48(), 
            [f" Milk                9999  150.00  1,499,850.00 "])
        self.assertEqual(
            pos.PosItem(name="Milk", price=150.00, count=9999999999).print48(), 
            [f" Milk  9999999999  150.00  1,499,999,999,850.00 "])
        self.assertEqual(
            pos.PosItem(name="New Cat Food", price=150.00, count=9999999999).print48(), 
            [f" New Cat Fo 9999999999  150.00  1,499,999,999,850.00 "])
        
        self.assertEqual(
            pos.PosItem(name="Gift Candy", price=0.00, count=2).print48(), 
            [f" Gift Candy                   2    0.00    0.00 "])
        self.assertEqual(
            pos.PosItem(name="Pan Cake", price=16.50, count=3, note="Special Request").print48(), 
            [f" Pan Cake                     3   16.50   49.50 ", 
             " Special Request"])
        self.assertEqual(
            pos.PosItem(name="Pan Cake", price=16.50, count=3, note="Special request for the very special dinner").print48(), 
            [f" Pan Cake                     3   16.50   49.50 ", 
             " Special request for the very spe"])

class TestPosShop(unittest.TestCase):
    
    def test_PosShop_init(self):
        pos.PosShop(name="My Shop", address1="123 Main St", city="Colombo", state="Western", zip_code="12345", phone="0123456780") # valid
        pos.PosShop(name="My Shop", address1="123 Main St", address2="Suite 100", city="Austin", state="TX", zip_code="78729", phone="0123456780", email="myshop@example.com") # valid

        invalid_cases = [
            ("", "123 Main St", "", "Colombo", "Western", "12345", "0123456780"),  # Empty name
            ("My Shop", "", "", "Colombo", "Western", "12345", "0123456780"),  # Empty address
            ("My Shop", "123 Main St", "", "", "Western", "12345", "0123456780"),  # Empty city
            ("My Shop", "123 Main St", "", "Colombo", "", "12345", "0123456780"),  # Empty state
            ("My Shop", "123 Main St", "", "Colombo", "Western", "", "0123456780"),  # Empty zip code
            ("My Shop", "123 Main St", "", "Colombo", "Western", "12345", ""),  # Empty phone
        ]
        for name, address1, address2, city, state, zip_code, phone in invalid_cases:
            with self.subTest(name=name, address1=address1, address2=address2, city=city, state=state, zip_code=zip_code, phone=phone):
                with self.assertRaises(AssertionError):
                    pos.PosShop(name=name, address1=address1, address2=address2, city=city, state=state, zip_code=zip_code, phone=phone)

    def test_PosShop_print48(self):
        self.assertEqual(
            pos.PosShop(name="My Cool Shop", address1="123 Main St", address2="", city="Colombo", state="Western", zip_code="12345", phone="0123456780").print48(),
            ["My Cool Shop", "123 Main St", "Colombo, Western 12345", "Tel: 0123456780"])
        self.assertEqual(
            pos.PosShop(name="My Shop", address1="123 Main St", address2="Suite 100", city="Austin", state="TX", zip_code="78729", phone="0123456780", email="myshop@example.com").print48(),
            ["My Shop", "123 Main St", "Suite 100", "Austin, TX 78729", "Tel: 0123456780", "Email: myshop@example.com"])
        self.assertEqual(
            pos.PosShop(name="My Very Long Shop Name That Exceeds 48 Characters", address1="123 Main St That Also Exceeds Forty Eight Characters In Length", address2="", 
                        city="New York With A Very Long Name That Exceeds Forty Eight Characters", state="Western With A Very Long Name That Exceeds Forty Eight Characters", 
                        zip_code="12345 With A Very Long Zip Code That Exceeds Forty Eight Characters", phone="0123456780").print48(),
            ["My Very Long Shop Name That Exceeds 48 Charact", 
             "123 Main St That Also Exceeds Forty Eight Char",
             "New York With A Very Long Name That Exceeds Fo",
             "Tel: 0123456780"])

class TestPosOrder(unittest.TestCase):

    def test_PosOrder_init(self):
        sp1=pos.PosShop(name="My Shop", address1="123 Main St", city="Colombo", state="Western", zip_code="12345", phone="0123456780", 
                       surcharges=[pos.PosCharge(name="Tax", amount=0.15, fixed=False), pos.PosCharge(name="Fee", amount=17.00, fixed=True)])
        sp2=pos.PosShop(name="My Shop", address1="123 Main St", city="Colombo", state="Western", zip_code="12345", phone="0123456780") # no surcharges
        it1 = pos.PosItem(name="Apple Juice", price=250.00, count=2)
        it2 = pos.PosItem(name="Biscuits (Large)", price=180.00, count=1)
        ex1 = pos.PosCharge(name="Donation", amount=150.00, fixed=True)
        ex2 = pos.PosCharge(name="Donation2", amount=0.1, fixed=False)
        currency = "£"
        order1 = pos.PosOrder(order_id="ORD001", shop=sp1, items=[it1]) # valid 
        order2 = pos.PosOrder(order_id="ORD002", shop=sp1, items=[], extras=[ex1], customer_name="John Doe", notes="It's a gift") # valid 
        order3 = pos.PosOrder(order_id="ORD003", shop=sp2, items=[it1, it2], extras=[ex1, ex2], currency=currency) # valid with no charges
        self.assertEqual(order1.customer_name, "Customer ORD001") 
        self.assertEqual(order1.notes, [])
        self.assertEqual(order2.customer_name, "John Doe") 
        self.assertEqual(order2.notes, ["It's a gift"])
        self.assertEqual(order2.currency, "$")
        self.assertEqual(order3.currency, "£")

        order4 = pos.PosOrder(order_id="ORD004", shop=sp1, items=[it1, it2], extras=[ex1, ex2],
                              customer_name="John Doe 1234567890 1234567890 1234567890", 
                              notes="Please pack the cookie carefully \nas it's a gift. \tThis note is too long and \rshould be split into multiple lines.") # valid 
        self.assertEqual(order4.customer_name, "John Doe 1234567890 1234567890 1") 
        self.assertEqual(order4.notes, ["Please pack the cookie carefully as it's a",
                                        "gift. This note is too long and should be split", 
                                        "into multiple lines."])
        expected_sub_total = 2*250.00 + 180.00
        self.assertAlmostEqual(order4.sub_total, expected_sub_total)
        expected_sub_total_extras = 150.00 + 0.1*expected_sub_total
        self.assertAlmostEqual(order4.sub_total_extras, expected_sub_total_extras)
        expected_sub_total_surcharges = 17.00 + 0.15*expected_sub_total
        self.assertAlmostEqual(order4.sub_total_surcharges, expected_sub_total_surcharges)
        expected_total = expected_sub_total + expected_sub_total_extras + expected_sub_total_surcharges
        self.assertAlmostEqual(order4.total, expected_total)

        invalid_cases = [
            ("", sp1, [pos.PosItem(name="Apple Juice", price=250.00, count=2)], []),  # Empty order ID
            ("ORD005", sp2, [], []),  # No items or extras
        ]
        for order_id, shop, items, extras in invalid_cases:
            with self.subTest(order_id=order_id, shop=shop, items=items, extras=extras):
                with self.assertRaises(AssertionError):
                    pos.PosOrder(order_id=order_id, shop=shop, items=items, extras=extras)

    def test_PosOrder_print48(self):
        pass

        
if __name__ == '__main__':
    unittest.main()