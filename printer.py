from escpos.printer import Win32Raw
from config import app_config


def get_printer():
    printer_name = app_config["printer_name"]
    p = None
    try:
        p = Win32Raw(printer_name, profile="TM-T88V")
    except Exception as e:
        print(f"⚠️ Warning: Printer '{printer_name}' connection problem with TM-T88V profile")
        print("Trying default profile...")
        try:
            p = Win32Raw(printer_name)
        except Exception as e:
            print(f"⚠️ Warning: Printer '{printer_name}' connection problem with default profile")
            print(e)
    if p is None:
        print(f"❗No printer connection available for '{printer_name}'. Printing functions will not work.")
    return p

printer = get_printer()


def calibrate_width():
    p = Win32Raw(app_config["printer_name"], profile="TM-T88V")

    # Reset
    p._raw(b'\x1b\x40') 
    
    # Test 1: Standard Text
    p.text("--- 80mm Ruler Test (42 Chars) ---\n")
    p.text("123456789012345678901234567890123456789012\n")
    p.text("I----------------------------------------I\n")
    
    # Test 2: Double Width (Should fill more space)
    p.set(width=2, height=2, align='center')
    p.text("STRETCH TEST\n")
    
    # Test 3: Right Alignment (Does it go to the far right?)
    p.set(align='right', width=1, height=1)
    p.text("This should be at the 72mm mark -> |\n")
    
    # Test 4: Try a very long dashed line
    p.set(width=1, height=1, align='left')
    p.text("-" * 48 + "\n") # Standard 80mm width
    p.text("If this line wraps, the printer is in 58mm mode.\n")
    
    p.cut()

def _calibrate_nuclear_option():
    # Raw ESC/POS command to set the printing area width
    # GS W nL nH (Sets printable area width)
    # For 576 dots (72mm): nL=64, nH=2
    p = Win32Raw(app_config["printer_name"], profile="TM-T88V")
    p._raw(b'\x1d\x57\x40\x02')

if __name__ == "__main__":
    calibrate_width()