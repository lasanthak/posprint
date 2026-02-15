from abc import ABC, abstractmethod
from typing import List
from config import app_config

class PosPrintable(ABC):
    @abstractmethod
    def print48(self) -> List[str]:
        """
        Method to return a list of 48-character wide strings (80mm printer)
        representation of the item for receipt printing.
        """
        pass

CURRENCY = app_config["currency"]

class PosCharge:
    def __init__(self, name: str, amount: float, fixed: bool = True):
        """
         Represents an additional charge on the receipt, such as tax or service charge.
          - name: Description of the charge (e.g., "Tax", "Service Fee", "GST 12.5%")
          - amount: The amount of the charge (e.g., 5.00 for $5.00 for fixed, or 0.125 for 12.5% for a rate)
          - fixed: If True, the charge is a fixed amount; if False, it is a rate applied to the subtotal of taxable items.
        """
        self.name = name.strip() if name else ""
        assert self.name and len(self.name) <= 15, "Charge name must be 1-15 characters"
        if fixed:
            assert amount >= 0, "Fixed charge should not be negative"
        else:
            assert 0.0 <= amount <= 1.0, "Rate charge should be between 0 and 1"
        self.amount = amount
        self.fixed = fixed

class PosChargeItem:
    def __init__(self, charge: PosCharge, count: int = 1, base_amount: float = 0.0, name: str = ""):
        assert count > 0, f"{charge.name} - Count must be greater than 0"
        self.count = count
        assert base_amount >= 0, f"{charge.name} - Base amount must be greater than or equal to 0"
        self.base_amount = base_amount
        self.charge = charge
        self.name = name if name else charge.name
    
    @property
    def total_amount(self) -> float:
        if self.charge.fixed:
            return self.count * self.charge.amount
        else:
            return self.count * self.charge.amount * self.base_amount

class PosItem(PosPrintable):
    def __init__(self, name: str, price: float, count: int = 1, note: str = ""):
        self.name = name
        assert price >= 0, f"{name} - Price must be greater than or equal to 0"
        self.price = price
        assert count > 0, f"{name} - Count must be greater than 0"
        self.count = count
        self.note = note

    @property
    def total_price(self) -> float:
        return self.price * self.count

    def print48(self) -> str:
        # Left-aligned and padded
        count_str = f"{self.count:>2}"
        price_str = f"{self.price:>6,.2f}"
        total_str = f"{self.total_price:>6,.2f}"
        sub_len = len(count_str) + len(price_str) + len(total_str) + 4  # spaces
        name_len = 48 - sub_len - 3  # 3 spaces: start, between name and count, and end
        if name_len < 10 and len(self.name) > name_len:
            name_len = 10  # Ensure at least 10 chars for name if possible
        # Left-aligned and padded/truncated
        name_str = f"{self.name:<{name_len}.{name_len}}"

        lines = [f" {name_str} {count_str}  {price_str}  {total_str} "]
        if self.note:
            lines.append(f" {self.note:.32}") # truncated to 32 chars

        return lines


class PosShop(PosPrintable):
    def __init__(self, name: str, 
                 address1: str, city: str,state: str, zip_code: str,
                 phone: str, address2: str = "", email: str = "",
                 surcharges: List[PosCharge] = []):
        """
        Represents the shop information to be printed on the receipt.
         - surcharges: A list of PosCharge objects that represent additional charges (e.g., tax, service charge) that should be applied to the order. These can be fixed amounts or rates based on the subtotal of taxable items.
        """
        self.name = name.strip() if name else ""
        assert self.name, "Shop name cannot be empty"
        self.address1 = address1.strip() if address1 else ""
        assert self.address1, "Shop address cannot be empty"
        self.city = city.strip() if city else ""
        assert self.city, "Shop city cannot be empty"
        self.state = state.strip() if state else ""
        assert self.state, "Shop state cannot be empty"
        self.zip_code = zip_code.strip() if zip_code else ""
        assert self.zip_code, "Shop zip code cannot be empty"
        self.phone = phone.strip() if phone else ""
        assert self.phone, "Shop phone cannot be empty"
        self.address2 = address2.strip() if address2 else ""
        self.email = email.strip() if email else ""
        self.surcharges = surcharges
    
    def print48(self) -> str:
        # 46 chars for content - expecting additional 2 spaces for padding (not added here)
        lines = [
            f"{self.name:.46}",
            f"{self.address1:.46}"
        ]
        if self.address2:
            lines.append(f"{self.address2:.46}")
        lines.append(f"{f'{self.city}, {self.state} {self.zip_code}':.46}")
        if self.phone:
            lines.append(f"{f'Tel: {self.phone}':.46}")
        if self.email:
            lines.append(f"{f'Email: {self.email}':.46}")

        return lines

class PosOrder(PosPrintable):

    def __init__(self,
                 order_id: str,
                 shop: PosShop,
                 items: List[PosItem],
                 extras: List[PosCharge] = [],
                 currency: str = CURRENCY,
                 customer_name: str = "",
                 notes: str = ""):
        self.order_id = order_id.strip() if order_id else ""
        assert self.order_id and len(self.order_id) <= 12, "Order ID must be 1-12 characters"
        self.currency = currency
        self.shop = shop
        assert items or extras, f"Order {order_id} must contain at least one item"
        self.items = items
        self.sub_total = sum(i.total_price for i in items)
        self.extras = [PosChargeItem(charge=c, base_amount=self.sub_total) for c in extras]
        self.sub_total_extras = sum(c.total_amount for c in self.extras)
        self.surcharges = [PosChargeItem(charge=c, base_amount=self.sub_total) for c in self.shop.surcharges]
        self.sub_total_surcharges = sum(c.total_amount for c in self.surcharges)
        self.total = self.sub_total + self.sub_total_extras + self.sub_total_surcharges
        self.customer_name = customer_name.strip() if customer_name else ""
        self.customer_name = self.customer_name[:32] if self.customer_name else f"Customer {order_id}"
        self.notes = _split_text(notes, max_width=48, max_parts=3)

    def print48(self) -> str:
        lines = []
        for item in self.items:
            lines.extend(item.print48())
        total_str = f"{self.total:>6,.2f}"
        lines.append(f"{'TOTAL':>42} {total_str} ")
        return lines

PAYMENT_METHODS = ["Cash", "CreditCard", "DebitCard", "ApplePay", "GooglePay", "Check", "PayPal", "Venmo", "Other"]

class PosPayment:
    def __init__(self, amount: float, method: str = "Other"):
        self.method = method.strip() if method else ""
        assert self.method and len(self.method) <= 12, "Payment method must be 1-12 characters"
        self.amount = amount
        assert self.amount >= 0, "Payment amount must be greater than or equal to 0"

class PosOrderPayment:
    def __init__(self, order: PosOrder, payments: List[PosPayment]):
        self.order = order
        self.payments = payments
        total_paid = sum(payment.amount for payment in payments)
        assert total_paid >= self.order.total, f"Order {self.order.order_id} - Total payment must be >= order total ({self.order.total})"
        self.change = total_paid - self.order.total

def _split_text(text: str, max_width: int, max_parts: int = 3) -> List[str]:
    """
     Splits text by whitespace, line break and truncate each part to 46 chars if too long upto 3 parts
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    parts = clean_text.split()
    truncated_parts = []
    current_line = ""
    for part in parts:
        if len(current_line) + len(part) + 1 <= max_width:
            current_line += (part + " ")
        else:
            truncated_parts.append(current_line.strip())
            current_line = part + " "
        if len(truncated_parts) == max_parts:
            break
    if current_line and len(truncated_parts) < max_parts:
        truncated_parts.append(current_line.strip())
    
    return truncated_parts
