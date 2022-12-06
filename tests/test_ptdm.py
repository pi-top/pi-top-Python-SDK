from unittest import TestCase
from unittest.mock import Mock, patch

from tests.utils import wait_until


class PTDMSubscribeClientTestCase(TestCase):
    def setUp(self):
        self.zmq_patch = patch("pitop.common.ptdm.zmq")
        self.zmq_mock = self.zmq_patch.start()
        self.poller_mock = Mock()
        self.context_mock = Mock()
        self.socket_mock = Mock()

        self.socket_mock.recv_string.return_value = ""
        self.context_mock.socket.return_value = self.socket_mock
        self.zmq_mock.Context.return_value = self.context_mock
        self.zmq_mock.Poller.return_value = self.poller_mock
        self.poller_mock.poll.return_value = []
        self.addCleanup(self.zmq_patch.stop)

    def test_callback_called_when_message_is_published(self):
        from pitop.common.ptdm import Message, PTDMSubscribeClient

        self.poller_mock.poll.return_value = [1]
        self.socket_mock.recv_string.return_value = f"{Message.PUB_LOW_BATTERY_WARNING}"

        def callback():
            callback.counter += 1

        callback.counter = 0

        client = PTDMSubscribeClient()
        client.initialise({Message.PUB_LOW_BATTERY_WARNING: callback})
        client.start_listening()

        wait_until(lambda: callback.counter > 0, timeout=3)

        client.stop_listening()

    def test_callback_not_included_if_has_wrong_signature(self):
        from pitop.common.ptdm import Message, PTDMSubscribeClient

        self.socket_mock.recv_string.return_value = f"{Message.PUB_LOW_BATTERY_WARNING}"

        def callback(x, y):
            callback.counter += 1

        callback.counter = 0

        client = PTDMSubscribeClient()
        client.initialise(
            {
                Message.PUB_LOW_BATTERY_WARNING: callback,
            }
        )

        assert client._callback_funcs.get(Message.PUB_LOW_BATTERY_WARNING) is None

    def test_subscribe_client_cleanup_closes_socket(self):
        from pitop.common.ptdm import Message, PTDMSubscribeClient

        self.socket_mock.recv_string.return_value = f"{Message.PUB_LOW_BATTERY_WARNING}"

        client = PTDMSubscribeClient()
        client.initialise(
            {
                Message.PUB_LOW_BATTERY_WARNING: lambda: None,
            }
        )
        client.start_listening()
        client.stop_listening()

        wait_until(lambda: client._zmq_socket is None)

    def test_uri(self):
        from pitop.common.ptdm import PTDMSubscribeClient

        assert PTDMSubscribeClient.URI == "tcp://127.0.0.1:3781"


class PTDMRequestClientTestCase(TestCase):
    def setUp(self):
        self.zmq_patch = patch("pitop.common.ptdm.zmq")
        self.zmq_mock = self.zmq_patch.start()
        self.context_mock = Mock()
        self.socket_mock = Mock()

        self.socket_mock.recv_string.return_value = ""
        self.context_mock.socket.return_value = self.socket_mock
        self.zmq_mock.Context.return_value = self.context_mock
        self.addCleanup(self.zmq_patch.stop)

    def test_uri(self):
        from pitop.common.ptdm import PTDMRequestClient

        assert PTDMRequestClient.URI == "tcp://127.0.0.1:3782"

    def test_send_message_opens_socket(self):
        from pitop.common.ptdm import Message, PTDMRequestClient

        self.socket_mock.recv_string.return_value = f"{Message.RSP_SET_OLED_CONTROL}"

        client = PTDMRequestClient()
        assert self.socket_mock.connect.call_count == 0
        client.send_request(Message.REQ_SET_OLED_CONTROL, [0])
        assert self.socket_mock.connect.call_count == 1

    def test_send_request_uses_send_message(self):
        from pitop.common.ptdm import Message, PTDMRequestClient

        self.socket_mock.recv_string.return_value = f"{Message.RSP_SET_OLED_CONTROL}"

        client = PTDMRequestClient()
        client.send_message = Mock()

        message = Message.from_parts(Message.REQ_SET_OLED_CONTROL, [0])
        assert client.send_message.call_count == 0
        client.send_message(message)
        assert client.send_message.call_count == 1

    def test_send_message_closes_socket(self):
        from pitop.common.ptdm import Message, PTDMRequestClient

        self.socket_mock.recv_string.return_value = f"{Message.RSP_SET_OLED_CONTROL}"

        client = PTDMRequestClient()
        assert self.socket_mock.close.call_count == 0
        client.send_request(Message.REQ_SET_OLED_CONTROL, [0])
        assert self.socket_mock.close.call_count == 1

    def test_raises_exception_on_error_message(self):
        from pitop.common.ptdm import Message, PTDMRequestClient

        client = PTDMRequestClient()

        for message in (
            Message.RSP_ERR_SERVER,
            Message.RSP_ERR_MALFORMED,
            Message.RSP_ERR_UNSUPPORTED,
        ):
            self.socket_mock.recv_string.return_value = f"{message}"
            self.assertRaises(
                Exception,
                lambda: client.send_request(Message.REQ_SET_OLED_CONTROL, [0]),
            )

    def test_raises_exception_on_incorrect_response(self):
        from pitop.common.ptdm import Message, PTDMRequestClient

        self.socket_mock.recv_string.return_value = f"{Message.RSP_BLANK_SCREEN}"

        client = PTDMRequestClient()
        self.assertRaises(
            Exception, lambda: client.send_request(Message.REQ_SET_OLED_CONTROL, [0])
        )
