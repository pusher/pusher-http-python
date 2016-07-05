from .config import Config
from .http import POST, Request, request_method

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
			self._host = "yolo.ngrok.io"


	@request_method
	def notify(self, interests, notification):
	    params = {
	        'interests': interests,
	    }
	    params.update(notification)
	    return Request(self, POST, "/customer_api/v1/apps/%s/notifications" % self.app_id, params)