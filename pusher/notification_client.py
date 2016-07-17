from .config import Config
from .http import POST, Request, request_method
from .util import ensure_text

DEFAULT_HOST = "nativepushclient-cluster1.pusher.com"
RESTRICTED_GCM_KEYS = ['to', 'registration_ids']
API_PREFIX = 'customer_api'
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
		self.validate_notification(params)
		path =  "/%s/%s/apps/%s/notifications" % (API_PREFIX, API_VERSION, self.app_id)
		return Request(self, POST, path, params)

	def validate_notification(self, notification):
		gcm_payload = notification.get('gcm')

		if not gcm_payload and not notification.get('apns') :
			raise ValueError("Notification must have fields APNS or GCM")

		if gcm_payload:
			for restricted_key in RESTRICTED_GCM_KEYS:
				gcm_payload.pop(restricted_key, None)

			ttl = gcm_payload.get('time_to_live')
			if ttl:
				if not isinstance(ttl, int):
					raise ValueError("GCM time_to_live must be an int")

				if not (0 <= ttl <= GCM_TTL):
					raise ValueError("GCM time_to_live must be between 0 and 241920 (4 weeks)")

			gcm_payload_notification = gcm_payload.get('notification')
			if gcm_payload_notification:
				title = gcm_payload_notification.get('title')
				icon = gcm_payload_notification.get('icon')
				if not isinstance(title, str):
					raise ValueError("GCM notification title is required must be a string")

				if not isinstance(icon, str):
					raise ValueError("GCM notification icon is required must be a string")

				if len(title) is 0:
					raise ValueError("GCM notification title must not be empty")

				if len(icon) is 0:
					raise ValueError("GCM notification icon must not be empty")

		webhook_url = notification.get('webhook_url')
		webhook_level = notification.get('webhook_level')

		if webhook_level:
			if not webhook_url:
				raise ValueError("webhook_level cannot be used without a webhook_url")

			if not webhook_level in WEBHOOK_LEVELS:
				raise ValueError("webhook_level must be either INFO or DEBUG. Blank will default to INFO")
