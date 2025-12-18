import sys
import Snowflake # type: ignore
import urandom

# --- LED CLASS ---
class LED:
    """LED-களைக் கட்டுப்படுத்தும் கிளாஸ்."""
    def __init__(self, num_leds):
        self.NUM_LEDS = num_leds

    def set_all(self, r, g, b):
        for i in range(1, self.NUM_LEDS + 1):
            Snowflake.setSingleLED(i, (r, g, b))

    # --- புதிய மாற்றம் இங்கே உள்ளது ---
    def set_custom(self, led_list, r, g, b):
        self.off()
        for i in led_list:
            if 1 <= i <= self.NUM_LEDS:
                Snowflake.setSingleLED(i, (r, g, b))

    def off(self):
        self.set_all(0, 0, 0)

# --- SETUP ---
led = LED(num_leds=9)
led.set_all(0, 0, 0) # ஆரம்பத்தில் விளக்கை அணைக்கவும்

print("Waiting for Data...")

# --- MAIN LOOP ---
while True:
    data_line = sys.stdin.readline()

    if data_line:
        data = data_line.strip()
        print("Received:", data)

        # --- STOP (S) : Red (எல்லாம் எரியும்) ---
        if "car : S" in data: 
            led.set_all(255, 0, 0) 
            
        # --- FORWARD (F) : Green (1, 2, 3 மட்டும் எரியும்) ---
        # இங்கே மாற்றம் செய்யப்பட்டுள்ளது
        if "car : F" in data:
            # 1, 2, 3 மட்டும் Green கலரில் எரியும்
            led.set_custom([2, 8], 0, 255, 0)

        # --- LEFT (L) : Blue ---
        if "car : L" in data:
            led.set_custom([7,9], 0, 150, 150)

        # --- RIGHT (R) : Orange ---
        if "car : R" in data:
            led.set_custom([3,9], 150, 150, 0)

        # --- UP (U) : Rose ---
        if "Ang : U" in data:
            led.set_custom([1], 100, 100, 100)

        # --- DOWN (D) : Violet ---
        if "Ang : D" in data:
            led.set_custom([5], 200, 200, 200)
