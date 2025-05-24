# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

import unittest
from Assembler import Assembler


# Mock validate_memory and validate_register functions
def validate_memory(**Args):
    """Mock function for memory validation."""
    return True


def validate_register(**Args):
    """Mock function for register validation."""
    return True


class TestAssembler(unittest.TestCase):
    def setUp(self):
        """Set up a new Assembler instance for each test."""
        self.assembler = Assembler()
        # Initialize memory with some test values
        self.assembler.s = {0: 10, 1: 20, 2: 30, 3: -5, 4: 0}
        self.assembler.max_pc = 100  # Set max program counter for jump tests

    def test_initialization(self):
        """Test that the Assembler initializes with default values."""
        assembler = Assembler()
        self.assertEqual(assembler.acc, 0)
        self.assertEqual(assembler.in1, 0)
        self.assertEqual(assembler.in2, 0)
        self.assertEqual(assembler.pc, 0)
        self.assertEqual(assembler.s, {})
        self.assertEqual(assembler.max_pc, 0)
        self.assertEqual(assembler.message, "")
        self.assertEqual(assembler.debug_message, "")

    def test_load(self):
        """Test load method."""
        # Test loading from memory to ACC
        result = self.assembler.load("acc", 1)
        self.assertEqual(self.assembler.acc, 20)
        self.assertTrue(result)

        # Test loading from non-existent memory location (should load 0)
        result = self.assembler.load("in1", 10)
        self.assertEqual(self.assembler.in1, 0)
        self.assertTrue(result)

        # Test loading to PC (should return False)
        result = self.assembler.load("pc", 2)
        self.assertEqual(self.assembler.pc, 30)
        self.assertFalse(result)

    def test_loadin1(self):
        """Test loadin1 method."""
        self.assembler.in1 = 2
        result = self.assembler.loadin1("acc", 1)
        self.assertEqual(self.assembler.acc, self.assembler.s.get(3, 0))
        self.assertEqual(self.assembler.acc, -5)
        self.assertTrue(result)

    def test_loadin2(self):
        """Test loadin2 method."""
        self.assembler.in2 = 1
        result = self.assembler.loadin2("acc", 2)
        self.assertEqual(self.assembler.acc, self.assembler.s.get(3, 0))
        self.assertEqual(self.assembler.acc, -5)
        self.assertTrue(result)

    def test_loadi(self):
        """Test loadi method."""
        result = self.assembler.loadi("acc", 42)
        self.assertEqual(self.assembler.acc, 42)
        self.assertTrue(result)

        result = self.assembler.loadi("pc", 5)
        self.assertEqual(self.assembler.pc, 5)
        self.assertFalse(result)

    def test_store(self):
        """Test store method."""
        self.assembler.acc = 99
        result = self.assembler.store(10)
        self.assertEqual(self.assembler.s[10], 99)
        self.assertTrue(result)

    def test_storein1(self):
        """Test storein1 method."""
        self.assembler.acc = 99
        self.assembler.in1 = 5
        result = self.assembler.storein1(2)
        self.assertEqual(self.assembler.s[7], 99)
        self.assertTrue(result)

    def test_storein2(self):
        """Test storein2 method."""
        self.assembler.acc = 99
        self.assembler.in2 = 3
        result = self.assembler.storein2(4)
        self.assertEqual(self.assembler.s[7], 99)
        self.assertTrue(result)

    def test_move(self):
        """Test move method."""
        self.assembler.acc = 42
        result = self.assembler.move("acc", "in1")
        self.assertEqual(self.assembler.in1, 42)
        self.assertTrue(result)

        # Test moving to PC
        result = self.assembler.move("acc", "pc")
        self.assertEqual(self.assembler.pc, 42)
        self.assertFalse(result)

    def test_subi(self):
        """Test subi method."""
        self.assembler.acc = 50
        result = self.assembler.subi("acc", 10)
        self.assertEqual(self.assembler.acc, 40)
        self.assertTrue(result)

        # Test with PC
        self.assembler.pc = 20
        result = self.assembler.subi("pc", 5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

    def test_addi(self):
        """Test addi method."""
        self.assembler.acc = 30
        result = self.assembler.addi("acc", 15)
        self.assertEqual(self.assembler.acc, 45)
        self.assertTrue(result)

        # Test with PC
        self.assembler.pc = 10
        result = self.assembler.addi("pc", 5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

    def test_sub(self):
        """Test sub method."""
        self.assembler.acc = 100
        result = self.assembler.sub("acc", 0)  # Subtract memory[0] which is 10
        self.assertEqual(self.assembler.acc, 90)
        self.assertTrue(result)

        # Test with non-existent memory location
        self.assembler.acc = 100
        result = self.assembler.sub(
            "acc", 10
        )  # Memory location doesn't exist, should subtract 0
        self.assertEqual(self.assembler.acc, 100)
        self.assertTrue(result)

    def test_add(self):
        """Test add method."""
        self.assembler.acc = 5
        result = self.assembler.add("acc", 1)  # Add memory[1] which is 20
        self.assertEqual(self.assembler.acc, 25)
        self.assertTrue(result)

        # Test with non-existent memory location
        self.assembler.acc = 5
        result = self.assembler.add(
            "acc", 10
        )  # Memory location doesn't exist, should add 0
        self.assertEqual(self.assembler.acc, 5)
        self.assertTrue(result)

    def test_oplusi(self):
        """Test oplusi (XOR) method."""
        self.assembler.acc = 10  # 1010 in binary
        result = self.assembler.oplusi("acc", 6)  # 0110 in binary
        # 1010 XOR 0110 = 1100 = 12
        self.assertEqual(self.assembler.acc, 12)
        self.assertTrue(result)

    def test_andi(self):
        """Test andi (AND) method."""
        self.assembler.acc = 10  # 1010 in binary
        result = self.assembler.andi("acc", 6)  # 0110 in binary
        # 1010 AND 0110 = 0010 = 2
        self.assertEqual(self.assembler.acc, 2)
        self.assertTrue(result)

    def test_ori(self):
        """Test ori (OR) method."""
        self.assembler.acc = 10  # 1010 in binary
        result = self.assembler.ori("acc", 6)  # 0110 in binary
        # 1010 OR 0110 = 1110 = 14
        self.assertEqual(self.assembler.acc, 14)
        self.assertTrue(result)

    def test_oplus(self):
        """Test oplus (XOR with memory) method."""
        self.assembler.acc = 15  # 1111 in binary
        self.assembler.s[5] = 6  # 0110 in binary
        result = self.assembler.oplus("acc", 5)
        # 1111 XOR 0110 = 1001 = 9
        self.assertEqual(self.assembler.acc, 9)
        self.assertTrue(result)

    def test_and(self):
        """Test and_ (AND with memory) method."""
        self.assembler.acc = 15  # 1111 in binary
        self.assembler.s[5] = 6  # 0110 in binary
        result = self.assembler.and_("acc", 5)
        # 1111 AND 0110 = 0110 = 6
        self.assertEqual(self.assembler.acc, 6)
        self.assertTrue(result)

    def test_or(self):
        """Test or_ (OR with memory) method."""
        self.assembler.acc = 9  # 1001 in binary
        self.assembler.s[5] = 6  # 0110 in binary
        result = self.assembler.or_("acc", 5)
        # 1001 OR 0110 = 1111 = 15
        self.assertEqual(self.assembler.acc, 15)
        self.assertTrue(result)

    def test_nop(self):
        """Test nop method."""
        result = self.assembler.nop()
        self.assertTrue(result)

    def test_jump(self):
        """Test jump method."""
        self.assembler.pc = 10
        result = self.assembler.jump(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)
        self.assertIn("Jump Granted", self.assembler.debug_message)

        # Test negative jump
        self.assembler.pc = 15
        result = self.assembler.jump(-10)
        self.assertEqual(self.assembler.pc, 5)
        self.assertFalse(result)

        # Test jump that would cause negative PC
        self.assembler.pc = 5
        with self.assertRaises(ValueError):
            self.assembler.jump(-10)

        # Test jump beyond max_pc
        self.assembler.pc = 50
        with self.assertRaises(ValueError):
            self.assembler.jump(60)  # max_pc is 100 (set in setUp)

    def test_jump_eq(self):
        """Test jump_eq method."""
        # Test when ACC == 0
        self.assembler.acc = 0
        self.assembler.pc = 10
        result = self.assembler.jump_eq(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

        # Test when ACC != 0
        self.assembler.acc = 10
        self.assembler.pc = 20
        result = self.assembler.jump_eq(5)
        self.assertEqual(self.assembler.pc, 20)  # PC should not change
        self.assertTrue(result)
        self.assertIn("Jump Denied", self.assembler.debug_message)

    def test_jump_ne(self):
        """Test jump_ne method."""
        # Test when ACC != 0
        self.assembler.acc = 10
        self.assembler.pc = 10
        result = self.assembler.jump_ne(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

        # Test when ACC == 0
        self.assembler.acc = 0
        self.assembler.pc = 20
        result = self.assembler.jump_ne(5)
        self.assertEqual(self.assembler.pc, 20)  # PC should not change
        self.assertTrue(result)
        self.assertIn("Jump Denied", self.assembler.debug_message)

    def test_jump_le(self):
        """Test jump_le method."""
        # Test when ACC < 0
        self.assembler.acc = -5
        self.assembler.pc = 10
        result = self.assembler.jump_le(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

        # Test when ACC == 0
        self.assembler.acc = 0
        self.assembler.pc = 20
        result = self.assembler.jump_le(5)
        self.assertEqual(self.assembler.pc, 25)
        self.assertFalse(result)

        # Test when ACC > 0
        self.assembler.acc = 5
        self.assembler.pc = 30
        result = self.assembler.jump_le(5)
        self.assertEqual(self.assembler.pc, 30)  # PC should not change
        self.assertTrue(result)
        self.assertIn("Jump Denied", self.assembler.debug_message)

    def test_jump_ge(self):
        """Test jump_ge method."""
        # Test when ACC > 0
        self.assembler.acc = 5
        self.assembler.pc = 10
        result = self.assembler.jump_ge(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

        # Test when ACC == 0
        self.assembler.acc = 0
        self.assembler.pc = 20
        result = self.assembler.jump_ge(5)
        self.assertEqual(self.assembler.pc, 25)
        self.assertFalse(result)

        # Test when ACC < 0
        self.assembler.acc = -5
        self.assembler.pc = 30
        result = self.assembler.jump_ge(5)
        self.assertEqual(self.assembler.pc, 30)  # PC should not change
        self.assertTrue(result)
        self.assertIn("Jump Denied", self.assembler.debug_message)

    def test_jump_lt(self):
        """Test jump_lt method."""
        # Test when ACC < 0
        self.assembler.acc = -5
        self.assembler.pc = 10
        result = self.assembler.jump_lt(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

        # Test when ACC >= 0
        self.assembler.acc = 0
        self.assembler.pc = 20
        result = self.assembler.jump_lt(5)
        self.assertEqual(self.assembler.pc, 20)  # PC should not change
        self.assertTrue(result)
        self.assertIn("Jump Denied", self.assembler.debug_message)

    def test_jump_gt(self):
        """Test jump_gt method."""
        # Test when ACC > 0
        self.assembler.acc = 5
        self.assembler.pc = 10
        result = self.assembler.jump_gt(5)
        self.assertEqual(self.assembler.pc, 15)
        self.assertFalse(result)

        # Test when ACC <= 0
        self.assembler.acc = 0
        self.assembler.pc = 20
        result = self.assembler.jump_gt(5)
        self.assertEqual(self.assembler.pc, 20)  # PC should not change
        self.assertTrue(result)
        self.assertIn("Jump Denied", self.assembler.debug_message)


if __name__ == "__main__":
    unittest.main()
