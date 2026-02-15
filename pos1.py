from escpos.printer import Win32Raw
from datetime import datetime
from config import app_config

def print_receipt():
    printer_name = app_config["printer_name"]
    
    try:
        p = Win32Raw(printer_name)
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    p.set(font='a', align='center', width=1, height=1)

    p.image(app_config["logo_path"])

    # 1. Header (Centered, Bold, Double Size)
    p.set(bold=True)
    p.text("CHARLIE & THE CHOCOLATE FACTGORY\n")
    
    # 2. Reset to Normal
    p.set(bold=False)
    p.text("123 Business Road, Austin, TX 78701\n")
    p.text("Tel: 012-345-6789\n")
    p.text("www.charliechocolate.com\n")
    
    # Date and Time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    p.set(align='left')
    p.text("-" * 48 + "\n")

    # 3. Item List

    p.text("    Apple Juice                   Rs. 250.00    \n")
    p.text("    Biscuits (Large)              Rs. 180.00    \n")
    p.text("-" * 48 + "\n")

    # 4. Total
    p.set(bold=True)
    p.text("                      TOTAL       Rs. 430.00    \n\n")

    # 5. Barcode (Standard EAN13 requires 12 or 13 digits)
    # p.set(align='center')
    # try:
    #     # '64' is height, '2' is width of bars
    #     p.barcode('123456789012', 'EAN13', 64, 2, '', '')
    # except Exception as e:
    #     print(f"Barcode error: {e}")

    # 6. Finalize
    p.set(font='b', align='center', width=1, height=1)
    p.text(f"\n{now}\n")
    p.text("Thank you for shopping with us!\n")
    #p.ln(1)
    p.cut()

if __name__ == "__main__":
    print_receipt()