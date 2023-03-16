from __future__ import absolute_import

import logging

from sentry import http, tagstore
from sentry.plugins.bases import notify
from sentry.utils import json
from sentry.utils.http import absolute_uri

import sentry_mattermost

class MattermostPlugin(notify.NotificationPlugin):
    title = 'Mattermost'
    slug = 'mattermost'
    author = 'Miare Team'
    author_url = 'https://github.com/miare-ir/sentry-mattermost'
    description = 'Post notifications to mattermost webhook'
    version = sentry_mattermost.VERSION
    resource_links = (
        ('Source', 'https://github.com/miare-ir/sentry-mattermost'),
    )
    conf_key = 'mattermost'

    logger = logging.getLogger('sentry.plugins.sentry_mattermost_miare')

    def markdown_link(self, display, target_url):
        return f"[{display}]({target_url})"

    def is_configured(self, project):
        return bool(self.get_option('webhook_url', project))

    def get_config(self, project, **kwargs):
        return [
            {
                'name': 'webhook_url',
                'label': 'Mattermost webhook url',
                'type': 'url',
                'placeholder': 'https://mattermost.example.org/hooks/2crt99i3rfcvudctz9tzo4iqgt',
                'required': True,
                'help': 'Mattermost instance incoming webhook url'
            },
            {
                'name': 'show_tags',
                'label': 'Show tags',
                'type': 'bool',
                'required': False,
                'help': 'Show event tags'
            }
        ]

    def prepare_text(self, data: dict) -> str:
        text = ''
        text += f'# {data["title"]}\n'
        text += data['link'] + '\n'
        text += f'Culprit: {data["culprit"]}\n'

        if 'tags' in data:
            text += '| Tag | Value |\n'
            text += '|-----|-------|\n'
            text += '\n'.join(['| %s | %s |' % tag for tag in data['tags']])

        return text

    def notify(self, notification, raise_exception=False):
        data = {}

        event = notification.event
        group = event.group
        project = group.project

        if not self.is_configured(project):
            return

        webhook_url = self.get_option('webhook_url', project)
        project_name = project.get_full_name().encode('utf-8')
        notification_link = self.markdown_link('Click Here', self.add_notification_referrer_param(group.get_absolute_url()))

        title = event.title.encode('utf-8')
        error_message = event.message.encode('utf-8')

        data.update({'title': title, 'project_name': project_name, 'link': notification_link, 'msg': error_message, 'culprit': group.culprit})

        if self.get_option('show_tags', project):
            data['tags'] = event.tags

        self.logger.debug(f'preparing text using { data = }')
        text = self.prepare_text(data)
        self.logger.debug('text has been prepared: %s' % text)

        return http.safe_urlopen(webhook_url, method='POST', data={
            'text': text,
            "icon_url": "https://myovchev.github.io/sentry-slack/images/logo32.png",
            "username": "Sentry",
            })

