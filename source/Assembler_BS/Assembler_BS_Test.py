# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

import unittest
from Assembler import Assembler

# TODO:
# muli - Multiply destination by immediate value
# divi - Divide destination by immediate value
# modi - Mod destination by immediate value
# mul - Multiply destination by memory value
# div - Divide destination by memory value
# mod - Mod destination by memory value


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

    def test_loadin(self):
        """Test loadin method."""
        self.assembler.ds = -3
        result = self.assembler.loadin("ds", "pc", 6)
        self.assertEqual(self.assembler.pc, self.assembler.s.get(3, 0))
        self.assertEqual(self.assembler.pc, -5)
        self.assertFalse(result)

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
        self.assembler.in1 = 99
        result = self.assembler.store("in1", 10)
        self.assertEqual(self.assembler.s[10], 99)
        self.assertTrue(result)

    def test_storein1(self):
        """Test storein1 method."""
        self.assembler.acc = 99
        self.assembler.in1 = 5
        result = self.assembler.storein1("acc", 2)
        self.assertEqual(self.assembler.s[7], 99)
        self.assertTrue(result)

    def test_storein2(self):
        """Test storein2 method."""
        self.assembler.acc = 99
        self.assembler.in2 = 3
        result = self.assembler.storein2("acc", 4)
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

    def test_muli(self):
        """Test muli (Multiply by immediate value) method."""
        self.assembler.acc = 5
        result = self.assembler.muli("acc", 6)
        self.assertEqual(self.assembler.acc, 30)
        self.assertTrue(result)

        self.assembler.in1 = 42
        result = self.assembler.muli("in1", 0)
        self.assertEqual(self.assembler.in1, 0)
        self.assertTrue(result)

        self.assembler.sp = 7
        result = self.assembler.muli("sp", -3)
        self.assertEqual(self.assembler.sp, -21)
        self.assertTrue(result)

    def test_divi(self):
        """Test divi (Divide by immediate value) method."""
        self.assembler.acc = 20
        result = self.assembler.divi("acc", 4)
        self.assertEqual(self.assembler.acc, 5)
        self.assertTrue(result)

        # Test with integer division (truncation)
        self.assembler.in1 = 10
        result = self.assembler.divi("in1", 3)
        self.assertEqual(
            self.assembler.in1, 3
        )  # 10 / 3 = 3.33... -> 3 (integer division)
        self.assertTrue(result)

        # Test with negative number
        self.assembler.sp = -15
        result = self.assembler.divi("sp", 3)
        self.assertEqual(self.assembler.sp, -5)
        self.assertTrue(result)

    def test_modi(self):
        """Test modi (Modulo by immediate value) method."""
        self.assembler.acc = 17
        result = self.assembler.modi("acc", 5)
        self.assertEqual(self.assembler.acc, 2)  # 17 % 5 = 2
        self.assertTrue(result)

        self.assembler.pc = 13
        result = self.assembler.modi("pc", 4)
        self.assertEqual(self.assembler.pc, 1)  # 13 % 4 = 1
        self.assertFalse(result)

    def test_mul(self):
        """Test mul (Multiply by memory value) method."""
        self.assembler.acc = -5
        result = self.assembler.mul("acc", 1)  # Multiply by memory[1] which is 20
        self.assertEqual(self.assembler.acc, -100)
        self.assertTrue(result)

        self.assembler.in1 = 42
        result = self.assembler.mul(
            "in1", 10
        )  # Memory location doesn't exist, should multiply by 0
        self.assertEqual(self.assembler.in1, 0)
        self.assertTrue(result)

    def test_div(self):
        """Test div (Divide by memory value) method."""
        self.assembler.acc = 100
        result = self.assembler.div("acc", 1)  # Divide by memory[1] which is 20
        self.assertEqual(self.assembler.acc, 5)
        self.assertTrue(result)

        self.assembler.in1 = 100
        result = self.assembler.div("in1", 2)  # Divide by memory[2] which is 30
        self.assertEqual(
            self.assembler.in1, 3
        )  # 100 / 30 = 3.33... -> 3 (integer division)
        self.assertTrue(result)

        self.assembler.sp = 30
        result = self.assembler.div("sp", 3)  # Divide by memory[3] which is -5
        self.assertEqual(self.assembler.sp, -6)
        self.assertTrue(result)

    def test_mod(self):
        """Test mod (Modulo by memory value) method."""
        self.assembler.acc = 102
        result = self.assembler.mod("acc", 1)  # Mod by memory[1] which is 20
        self.assertEqual(self.assembler.acc, 2)  # 102 % 20 = 2
        self.assertTrue(result)

        # Test with negative memory value
        self.assembler.sp = 17
        result = self.assembler.mod("sp", 3)  # Mod by memory[3] which is -5
        self.assertEqual(self.assembler.sp, -3)  # 17 % -5 = -3
        self.assertTrue(result)

        # Test with PC (should return False)
        self.assembler.pc = 13
        result = self.assembler.mod("pc", 3)  # Mod by memory[3] which is -5
        self.assertEqual(self.assembler.pc, -2)  # 13 % -5 = -2
        self.assertFalse(result)

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

    def test_addr(self):
        """Test addr (Add Register) method."""
        self.assembler.acc = 30
        self.assembler.in1 = 15
        self.assembler.addr("acc", "in1")
        self.assertEqual(self.assembler.acc, 45)

        # Test with PC as destination
        self.assembler.pc = 10
        self.assembler.ds = 5
        self.assertFalse(self.assembler.addr("pc", "ds"))
        self.assertEqual(self.assembler.pc, 15)

    def test_subr(self):
        """Test subr (Subtract Register) method."""
        self.assembler.acc = 50
        self.assembler.in1 = 20
        self.assembler.subr("acc", "in1")
        self.assertEqual(self.assembler.acc, 30)

        self.assembler.sp = 30
        self.assembler.baf = 50
        self.assembler.subr("sp", "baf")
        self.assertEqual(self.assembler.sp, -20)

    def test_mulr(self):
        """Test mulr (Multiply Register) method."""
        self.assembler.acc = 5
        self.assembler.in1 = 6
        self.assembler.mulr("acc", "in1")
        self.assertEqual(self.assembler.acc, 30)

        self.assembler.sp = 100
        self.assembler.ds = 0
        self.assembler.mulr("sp", "ds")
        self.assertEqual(self.assembler.sp, 0)

    def test_divr(self):
        """Test divr (Divide Register) method."""
        self.assembler.acc = 100
        self.assembler.in1 = 20
        self.assembler.divr("acc", "in1")
        self.assertEqual(self.assembler.acc, 5)

        # Test with integer division (truncation)
        self.assembler.sp = 10
        self.assembler.baf = 3
        self.assembler.divr("sp", "baf")
        self.assertEqual(self.assembler.sp, 3)  # 10/3 = 3.33... -> 3 (integer division)

    def test_modr(self):
        """Test modr (Modulo Register) method."""
        self.assembler.acc = 17
        self.assembler.in1 = 5
        self.assembler.modr("acc", "in1")
        self.assertEqual(self.assembler.acc, 2)  # 17 % 5 = 2

        # Test with mod that results in 0
        self.assembler.sp = 50
        self.assembler.ds = 10
        self.assembler.modr("sp", "ds")
        self.assertEqual(self.assembler.sp, 0)  # 50 % 10 = 0

        # Test with mod for negative numbers
        self.assembler.cs = -17
        self.assembler.pc = 5
        self.assembler.modr("cs", "pc")
        self.assertEqual(self.assembler.cs, 3)  # -17 % 5 = 3

    def test_oplusr(self):
        """Test oplusr (XOR Register) method."""
        self.assembler.acc = 10  # 1010 in binary
        self.assembler.in1 = 6  # 0110 in binary
        self.assembler.oplusr("acc", "in1")
        # 1010 XOR 0110 = 1100 = 12 in decimal
        self.assertEqual(self.assembler.acc, 12)

        # Test XOR with same value (should be 0)
        self.assembler.sp = 42
        self.assembler.ds = 42
        self.assembler.oplusr("sp", "ds")
        self.assertEqual(self.assembler.sp, 0)

    def test_orr(self):
        """Test orr (OR Register) method."""
        self.assembler.acc = 9  # 1001 in binary
        self.assembler.in1 = 6  # 0110 in binary
        self.assembler.orr("acc", "in1")
        # 1001 OR 0110 = 1111 = 15 in decimal
        self.assertEqual(self.assembler.acc, 15)

        # Test OR with 0 (should be unchanged)
        self.assembler.sp = 42
        self.assembler.ds = 0
        self.assembler.orr("sp", "ds")
        self.assertEqual(self.assembler.sp, 42)

    def test_andr(self):
        """Test andr (AND Register) method."""
        self.assembler.acc = 15  # 1111 in binary
        self.assembler.in1 = 6  # 0110 in binary
        self.assembler.andr("acc", "in1")
        # 1111 AND 0110 = 0110 = 6 in decimal
        self.assertEqual(self.assembler.acc, 6)

        # Test AND with 0 (should be 0)
        self.assembler.sp = 42
        self.assembler.ds = 0
        self.assembler.andr("sp", "ds")
        self.assertEqual(self.assembler.sp, 0)

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
