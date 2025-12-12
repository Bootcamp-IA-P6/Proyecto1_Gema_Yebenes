import unittest
import sys
import os

# Esto permite importar main.py desde la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from main import calculate_fare


class TestCalculateFare(unittest.TestCase):
    def test_calculate_fare_basic(self):
        prices = {
            "stopped":0.02,
            "moving": 0.05
        }
        result = calculate_fare(10, 10, prices)
        self.assertEqual(result, 0.2 + 0.5)  # 10 * 0.02 + 10 * 0.05
    
    def test_calculate_fare_only_stopped(self):
        prices = {
            "stopped":0.02,
            "moving": 0.05
        }
        result= calculate_fare(10, 0, prices)
        self.assertEqual(result, 0.2)
    
    def test_calculate_fare_only_moving(self):
        prices = {
            "stopped":0.02,
            "moving": 0.05
        }
        result= calculate_fare(0, 10, prices)
        self.assertEqual(result, 0.5) 

if __name__ == "__main__":
    unittest.main()
    
    