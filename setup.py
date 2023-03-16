from setuptools import setup
from sentry_mattermost import VERSION

setup(
    name="sentry_mattermost_miare",
    version=VERSION,
    author="Miare Team",
    author_email="it@miare.ir",
    description=("A Sentry plugin to send Mattermost notifications"),
    license="MIT",
    keywords="sentry mattermost devops",
    url="https://github.com/miare-ir/sentry-mattermost",
    packages=['sentry_mattermost'],
    entry_points={
       'sentry.plugins': [
            'mattermost = sentry_mattermost.plugin:Mattermost'
        ],
    },
)
