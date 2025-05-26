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

    def test_validate_channel(self):
        valid_channels = ["123", "xyz", "xyz123", "xyz_123", "xyz-123", "Channel@123", "channel_xyz", "channel-xyz", "channel,456", "channel;asd", "-abc_ABC@012.xpto,987;654"]

        invalid_channels = ["#123", "x" * 201, "abc%&*", "#server-to-user1234", "#server-to-users"]

        for channel in valid_channels:
            self.assertEqual(channel, pusher.util.validate_channel(channel))

        for invalid_channel in invalid_channels:
            with self.assertRaises(ValueError):
                pusher.util.validate_channel(invalid_channel)

    def test_validate_server_to_user_channel(self):
        self.assertEqual("#server-to-user-123", pusher.util.validate_channel("#server-to-user-123"))
        self.assertEqual("#server-to-user-user123", pusher.util.validate_channel("#server-to-user-user123"))
        self.assertEqual("#server-to-user-ID-123", pusher.util.validate_channel("#server-to-user-ID-123"))

        with self.assertRaises(ValueError):
            pusher.util.validate_channel("#server-to-useR-123")
            pusher.util.validate_channel("#server-to-user1234")
            pusher.util.validate_channel("#server-to-users")

    def test_validate_event_name(self):
        valid_events = ["e" * 200, "123", "xyz", "xyz123", "xyz_123", "xyz-123", "Channel@123", "channel_xyz", "channel-xyz", "channel,456", "channel;asd", "-abc_ABC@012.xpto,987;654"]
        invalid_events = ["e" * 201]
        invalid_types = [123, None, {}]

        for event in valid_events:
            self.assertEqual(event, pusher.util.validate_event_name(event))

        for invalid_event in invalid_events:
            with self.assertRaises(ValueError):
                pusher.util.validate_event_name(invalid_event)

        for invalid_event in invalid_types:
            with self.assertRaises(TypeError):
                pusher.util.validate_event_name(invalid_event)



if __name__ == '__main__':
    unittest.main()
