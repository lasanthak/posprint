# POS Print

A Python application for formatting and printing POS (Point of Sale) receipts on 80mm thermal printers using the ESC/POS protocol.

## Features

- Structured data models for shops, items, orders, payments, and charges
- 48-character wide receipt formatting (80mm thermal paper, Font A)
- Support for fixed and rate-based charges (tax, service fees, etc.)
- Shop surcharges and per-order extras
- Multi-payment support with change calculation
- Logo/image printing via BMP files
- Windows raw printer output via `python-escpos` and `pywin32`

## Requirements

- Python >= 3.14
- An 80mm ESC/POS compatible thermal printer
- Windows OS (uses `Win32Raw` printer driver)

## Installation

```bash
uv sync
```

## Usage

### Update Confgis
You need to update the `confgi.json` with appropriate configuration values that suites your use case. E.g.: Most importantly change the printer name.

### Define a shop

```python
from pos import PosShop, PosCharge

shop = PosShop(
    name="Charlie & The Chocolate Factory",
    address1="123 Business Road",
    city="Austin",
    state="TX",
    zip_code="78701",
    phone="012-345-6789",
    surcharges=[PosCharge(name="Tax", amount=0.15, fixed=False)]
)
```

### Create an order

```python
from pos import PosItem, PosOrder

items = [
    PosItem(name="Apple Juice", price=250.00, count=2),
    PosItem(name="Biscuits (Large)", price=180.00, count=1),
]

order = PosOrder(
    order_id="ORD001",
    shop=shop,
    items=items,
    customer_name="John Doe",
    notes="Please pack carefully"
)
```

### Process payment

```python
from pos import PosPayment, PosOrderPayment

payment = PosOrderPayment(
    order=order,
    payments=[PosPayment(amount=1000.00, method="Cash")]
)
```

### Print a receipt

```python
from pos1 import print_receipt

print_receipt()
```

## Project Structure

```
posprint/
  pos.py             # Core data models (PosShop, PosItem, PosOrder, etc.)
  pos1.py            # Receipt printing via Win32Raw printer
  pos_calibrate.py   # Printer width calibration utility
  tests/
    test_pos.py      # Unit tests for data models
```

## Running Tests

```bash
python -m unittest tests/test_pos.py
```

## Printer Calibration

Use `pos_calibrate.py` to verify your printer is configured for 80mm (48-character) width:

```bash
python pos_calibrate.py
```

## License & Philosophy

This software is open-source and licensed under the **GNU Affero General Public License v3.0 (AGPL v3)**. You can view the full license text in the [LICENSE.txt](./LICENSE.txt) file.

### 1. Project Philosophy
> **"I want software enthusiasts, non-profits, and small business owners to use this software to be successful."**

This project was built to empower independent creators and local organizations. While the AGPL allows strictly defined redistribution, the primary goal of this work is to support:
* **Individual Enthusiasts & Students**
* **Non-Profit Organizations**
* **Small Businesses** (Defined ideally as <100 employees or <$10M revenue)

### 2. Critical Disclaimer (Read Before Use)
**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**

* **Calculation Risks:** This software performs complex calculations. **You must verify all outputs manually** before using them for financial, tax, or critical business decisions.
* **Liability:** The author is **not responsible** for any financial losses, compliance fines, or business interruptions caused by errors in this software. By using this tool, you accept full responsibility for the results.

### 3. A Note on AI Training
While the AGPL allows for the inspection of source code, **I explicitly do not consent** to this codebase, its documentation, or its outputs being used as a dataset for training, fine-tuning, or validating Large Language Models (LLMs) or other generative AI systems. I ask that you respect the human effort behind this project.

---
*For questions about enterprise usage or commercial licensing, please contact the author.*