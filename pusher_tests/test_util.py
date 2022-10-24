import unittest

import pusher.util

class TestUtil(unittest.TestCase):
    def test_validate_user_id(self):
        valid_user_ids = ["1", "12", "abc", "ab12", "ABCDEFG1234"]
        invalid_user_ids = ["", "x" * 201, "abc%&*"]

        for user_id in valid_user_ids:
            self.assertEqual(user_id, pusher.util.validate_user_id(user_id))

        for user_id in invalid_user_ids:
            with self.assertRaises(ValueError):
                pusher.util.validate_user_id(user_id)

if __name__ == '__main__':
    unittest.main()
