import unittest

from scripts import export_spell_fixture as exporter


class SpellFixtureTests(unittest.TestCase):
    def test_decodes_confirmed_fixed_width_fields(self):
        data = bytearray(405)
        data[0:9] = b"Test bolt"
        data[80:88] = b"testbolt"
        data[90:92] = (71).to_bytes(2, "little")
        data[332] = 1
        data[336] = 32
        data[338] = 20
        data[339] = 1
        data[340:342] = (6).to_bytes(2, "little")
        data[349], data[351], data[353] = 2, 2, 16
        data[389:391] = (0).to_bytes(2, "little", signed=True)
        for offset in range(391, 399, 2):
            data[offset : offset + 2] = (-1).to_bytes(2, "little", signed=True)
        data[404] = 8

        spell = exporter.decode_spell(bytes(data))

        self.assertEqual(spell["id"], 71)
        self.assertEqual(spell["name"], "Test bolt")
        self.assertEqual(spell["mana_cost"], 20)
        self.assertEqual(spell["effects"], [{"handler": 0, "dice_count": 2, "roll_min": 2, "roll_max": 16}])
        self.assertEqual(spell["damage_type"], 8)

    def test_rejects_non_spell_record_length(self):
        with self.assertRaises(ValueError):
            exporter.decode_spell(b"short")


if __name__ == "__main__":
    unittest.main()
