from .config import Config
from .http import POST, Request, request_method
from .util import ensure_text

DEFAULT_HOST = "nativepush-cluster1.pusher.com"
RESTRICTED_GCM_KEYS = ['to', 'registration_ids']
API_PREFIX = 'server_api'
API_VERSION = 'v1'
GCM_TTL = 241920
WEBHOOK_LEVELS = ['INFO', 'DEBUG', '']

class NotificationClient(Config):

	def __init__(self, app_id, key, secret, ssl=True, host=None, port=None, timeout=5, cluster=None,
				 json_encoder=None, json_decoder=None, backend=None, **backend_options):

		super(NotificationClient, self).__init__(
			app_id, key, secret, ssl,
			host, port, timeout, cluster,
			json_encoder, json_decoder, backend,
			**backend_options)

		if host:
			self._host = ensure_text(host, "host")
		else:
			self._host = DEFAULT_HOST


	@request_method
	def notify(self, interests, notification):
		if not isinstance(interests, list) and not isinstance(interests, set):
			raise TypeError("Interests must be a list or a set")

		if len(interests) is not 1:
			raise ValueError("Currently sending to more than one interest is unsupported")

		if not isinstance(notification, dict):
			raise TypeError("Notification must be a dictionary")

		params = {
			'interests': interests,
		}
		params.update(notification)
		path =  "/%s/%s/apps/%s/notifications" % (API_PREFIX, API_VERSION, self.app_id)
		return Request(self, POST, path, params)
