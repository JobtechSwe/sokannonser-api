from datetime import datetime
from typing import Optional, Dict, List, Any

from sokannonser import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_text

import slack
from slack import errors


if settings.SLACK_STORE_MESSAGE:
    def retrieve_outbox_slack_messages():
        # Returns locally stored messages during tests
        if 'outbox' not in globals():
            return []
        global outbox  # noqa
        return outbox

    def clear_slack_messages():
        if 'outbox' in globals():
            global outbox
            outbox = []


def get_channel_id(channel_name: str) -> str:
    client = slack.WebClient(token=settings.SLACK_TOKEN)

    slack_response = client.channels_list()  # Let exceptions propagate. There's nothing we can do here.
    if slack_response['ok'] is False:
        raise errors.SlackClientError  # Something's wrong with either the token or user permissions

    try:
        channel_id = list(filter(lambda chan: chan['name'] == channel_name, slack_response['channels']))[0]['id']
    except IndexError:
        raise ValueError("Channel {} does not exist".format(channel_name))

    return channel_id


class SlackAttachment(object):
    # Default attachment colors, you can also hex codes.
    GOOD = 'good'           # Green
    WARNING = 'warning'     # Yellow
    DANGER = 'danger'       # Red

    default_markdown_fields = ['pretext', 'text', 'fields']

    def __init__(
            self, fallback: str = '', color: str = GOOD, pretext: Optional[str] = None,
            author_name: Optional[str] = None,
            author_link: Optional[str] = None, author_icon: Optional[str] = None, title: str = '',
            title_link: Optional[str] = None,
            text: str = '', fields: Optional[List[Dict]] = None, image_url: Optional[str] = None,
            thumb_url: Optional[str] = None,
            footer: Optional[str] = None, footer_icon: Optional[str] = None, ts: Optional[datetime] = None,
            mrkdwn_in: Optional[List[str]] = None, **kwargs
    ) -> None:
        self.fallback = fallback
        self.color = color
        self.pretext = pretext
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        self.title = title
        self.title_link = title_link
        self.text = text
        self.fields = fields
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.footer = footer
        self.footer_icon = footer_icon
        self.ts = ts

        if mrkdwn_in is None:
            mrkdwn_in = self.default_markdown_fields

        self.mrkdwn_in = mrkdwn_in

    def __eq__(self, o: object) -> bool:
        if type(o) != SlackAttachment:
            return False

        return self.to_dict() == getattr(o, 'to_dict')()

    def to_dict(self) -> Dict[str, Any]:
        ret = {
            'fallback': self.fallback,
            'color': self.color,
            'pretext': self.pretext,
            'author_name': self.author_name,
            'author_link': self.author_link,
            'author_icon': self.author_icon,
            'title': self.title,
            'title_link': self.title_link,
            'text': self.text,
            'fields': self.fields,
            'image_url': self.image_url,
            'thumb_url': self.thumb_url,
            'footer': self.footer,
            'footer_icon': self.footer_icon,
            'ts': self.ts.timestamp() if self.ts else None,
            'mrkdwn_in': self.mrkdwn_in,
        }

        return {k: v for k, v in ret.items() if v is not None}

    def __repr__(self):
        return 'Text: {}'.format(self.text)


class Empty:
    pass


class SlackMessage(object):
    """
    To use, do SlackMessage(**kwargs).send().
    For attachments argument, use above SlackAttachment class and provide as an iterable.
    """
    def __eq__(self, o: object) -> bool:
        if type(o) != SlackMessage:
            return False

        for field in ('message', 'channel', 'attachments', 'template'):
            if not getattr(self, field) == getattr(o, field, Empty):
                return False

        return True

    def __hash__(self):
        return hash(str(self))

    def __init__(self, message='', attachments=None, channel=None, template=None) -> None:
        if channel is None:
            channel = settings.SLACK_CHANNEL

        if template is None:
            template = settings.SLACK_DEFAULT_TEMPLATE

        self.message = message
        self._channel = channel
        self._attachments = attachments
        self.template = template

        self._timestamp = None
        self._channel_id = None

    def __str__(self):
        return str({
            "channel": self._channel,
            "text": self.message,
            "attachments": self.attachments,
            "template": self.template,
        })

    def __repr__(self):
        return "SlackMessage({})".format(str(self))

    @property
    def channel(self):
        # If we set SLACK_REDIRECT_CHANNEL setting, override channel provided on __init__.
        return settings.SLACK_REDIRECT_CHANNEL if settings.SLACK_REDIRECT_CHANNEL else self._channel

    @property
    def context(self):
        return {
            "channel": self.channel,
            "message": self.message,
        }

    @property
    def attachments(self):
        return [attachment.to_dict() for attachment in self._attachments] if self._attachments else None

    @property
    def rendered_template(self):
        return force_text(render_to_string(self.template, self.context).strip())

    @property
    def id(self):
        return self._timestamp

    @id.setter
    def id(self, value):
        self._timestamp = value

    @property
    def channel_id(self):
        if not self._channel_id:
            # The id is not needed for regular sending, so we load it only if we use it
            self._channel_id = get_channel_id(self.channel)

        return self._channel_id

    def replace_last_attachment(self, attachment):
        # Replace last attachment if exists, else sets attachment at index 0.
        try:
            self._attachments[-1] = attachment
        except IndexError:
            # TODO: Or do nothing and let exception go up?
            self._attachments.append(attachment)

    def set_attachments(self, attachments):
        if type(attachments) in (list, tuple):
            self._attachments = attachments
        elif type(attachments) == SlackAttachment:
            self._attachments = [attachments]
        else:
            raise ValueError

    def add_attachment(self, attachment: SlackAttachment):
        if self._attachments:
            self._attachments.append(attachment)
        else:
            self._attachments = [attachment]

    def send(self, fail_silently=True):
        if settings.SLACK_STORE_MESSAGE:
            # Store messages locally during tests
            if 'outbox' not in globals():
                global outbox
                outbox = []
            outbox.append(self)

        if not settings.SLACK_ENABLED:
            if settings.PRINT_SLACK_MESSAGE:
                print(self)
            return
        else:
            try:
                client = slack.WebClient(token=settings.SLACK_TOKEN)
                slack_response = client.chat_postMessage(
                    channel=self.channel,
                    text=self.message,
                    attachments=self.attachments,
                    as_user=False,
                )

                if slack_response['ok']:
                    self.id = slack_response['ts']
                else:
                    raise errors.SlackClientError
            except Exception as e:
                if not fail_silently:
                    raise e
        return True

    def update(self, fail_silently=True):
        if self.id:
            try:
                client = slack.WebClient(token=settings.SLACK_TOKEN)
                slack_response = client.chat_update(
                    channel=self.channel_id,
                    ts=self.id,
                    text=self.message,
                    attachments=self.attachments,
                    as_user=False
                )
                if slack_response['ok']:
                    self.id = slack_response['ts']
                else:
                    raise errors.SlackClientError
            except Exception as e:
                if not fail_silently:
                    raise e
        else:
            if not fail_silently:
                raise ValueError("Message has not been sent yet or does not have a valid timestmap")


def retrieve_slack_message(channel: str, ts: str):
    if ts is None:
        # This is convenient, however the channel must always be present
        return None

    if settings.SLACK_REDIRECT_CHANNEL:
        channel = settings.SLACK_REDIRECT_CHANNEL

    channel_id = get_channel_id(channel)

    client = slack.WebClient(token=settings.SLACK_TOKEN)
    try:
        response = client.channels_history(channel=channel_id, latest=ts, inclusive=1, limit=1)
        if response['ok']:
            message_data = response['messages'][0]

            attachments = []
            for attachment_data in message_data.get('attachments', []):
                attachments.append(
                    SlackAttachment(**attachment_data)
                )

            message = SlackMessage(channel=channel, message=message_data['text'], attachments=attachments)
            message.id = message_data['ts']

            return message
        else:
            raise ValueError("Message with timestamp {} does not exist in channel {}".format(ts, channel))
    except errors.SlackClientError as e:
        # Network or auth error. There's nothing we can do.
        raise e
