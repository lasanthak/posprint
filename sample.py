from escpos.printer import Win32Raw
from datetime import datetime
from config import app_config
import printer
import pos

def print_receipt():
    p = printer.pos80
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    currency = app_config["currency"]

    _shop = pos.PosShop(
        name="Charlie & The Chocolate Factory", 
        address1="123 Business Road",
        city="Austin",
        state="TX",
        zip_code="78701",
        phone="012-345-6789", 
        email="email@charliechocolate.com",
        surcharges=[pos.PosCharge(name="Tax", amount=0.15, fixed=False)]
        )
    
    _items = [
        pos.PosItem(name="The Wonka Bar", price=3.50, count=3),
        pos.PosItem(name="Everlasting Gobstoppers", price=1.00, count=10),
        pos.PosItem(name="Wonka's Whipple-Scrumptious Fudgemallow Delight", price=9.99, count=2, note="Limit - 2 per customer"),
        pos.PosItem(name="Hair Toffee", price=2.25, count=5),
        pos.PosItem(name="Three-Course Dinner Chewing Gum", price=23.75, count=1),
    ]

    _order = pos.PosOrder(
        order_id="012",
        shop=_shop,
        items=_items,
        extras=[pos.PosCharge(name="Donation", amount=30.00, fixed=True)],
        customer_name="John Doe",
        notes="It's a gift"
    )

    _payements = [
        pos.PosPayment(method="Cash", amount=50.00),
        pos.PosPayment(method="CreditCard", amount=_order.total-45.00)
    ]
    _order_payments = pos.PosOrderPayment(order=_order, payments=_payements)


    # Initialize printer
    p._raw(b'\x1b\x40')       # Reset printer
    p._raw(b'\x1b\x52\x00')   # Set USA character set
    p._raw(b'\x1b\x74\x00')   # Set Code Page 437

    p.set(font='a', align='center', width=1, height=1)
    # Logo
    p.image(app_config["logo_path"])
    # Header
    p.set(bold=True)
    _lines_shop = _shop.print48()
    p.text(_lines_shop[0] + "\n")
    p.set(bold=False)
    for line in _lines_shop[1:]:
        p.text(line + "\n")

    # Order ID
    p.ln(1)
    p._raw(b'\x1d\x21\x11')  # double width + double height
    p.text(f"ORDER: {_order.order_id}\n")
    p._raw(b'\x1d\x21\x00')  # reset to normal

    # Customer Name
    p.text("-" * 48 + "\n")
    p.set(align='left', bold=True)
    p.text(f"Name: {_order.customer_name}\n")
    # Date and Time
    p.set(font='b', bold=False)
    p.text(f"Date & Time: {now}\n")
    p.text(f"Currency: {currency['name']}\n")

    # Item Header
    p.set(font='a', bold=False)
    p.text("-" * 48 + "\n")
    p.set(bold=True)
    p.text(pos.PosItem.print48_header() + "\n")
    # Item List
    p.set(bold=False)
    _lines_items = [line for i in _items for line in i.print48() ]
    p.text("-" * 48 + "\n")
    for line in _lines_items:
        p.text(line + "\n")

    # Subtotal and Charges
    _lines_order = _order.print48()
    p.text("-" * 48 + "\n")
    for line in _lines_order[:-1]:
        p.text(line + "\n")
    p.text("-" * 48 + "\n")
    p.text(_lines_order[-1] + "\n")

    # Payment Method and Amount
    p.ln(1)
    p.text(f" Payments:\n")
    _lines_order_payment = _order_payments.print48()
    for line in _lines_order_payment:
        p.text(line + "\n")
    p.text("-" * 48 + "\n")

    # Grand Total (Double Size)
    p.set(font='b', align='center')
    p._raw(b'\x1d\x21\x11')  # double width + double height
    p.text(f"Grand Total: {_order.total:.2f}\n")
    p._raw(b'\x1d\x21\x00')  # reset to normal

    # Finalize
    p.set(font='b', align='center')
    p.ln(1)
    p.text("Thank you for shopping with us!\n")

    p.cut()

if __name__ == "__main__":
    print_receipt()