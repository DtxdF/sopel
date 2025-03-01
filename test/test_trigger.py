"""Tests for message parsing"""
from __future__ import annotations

import datetime
import re

import pytest

from sopel.tools import Identifier
from sopel.trigger import PreTrigger, Trigger


TMP_CONFIG = """
[core]
owner = Foo
admins =
    Bar
"""


TMP_CONFIG_ACCOUNT = """
[core]
owner = Foo
owner_account = bar
admins =
    Bar
"""


@pytest.fixture
def nick():
    return Identifier('Sopel')


def test_basic_pretrigger(nick):
    line = ':Foo!foo@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['#Sopel', 'Hello, world']
    assert pretrigger.text == 'Hello, world'
    assert pretrigger.plain == 'Hello, world'
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == '#Sopel'


def test_pm_pretrigger(nick):
    line = ':Foo!foo@example.com PRIVMSG Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['Sopel', 'Hello, world']
    assert pretrigger.text == 'Hello, world'
    assert pretrigger.plain == 'Hello, world'
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == Identifier('Foo')


def test_quit_pretrigger(nick):
    line = ':Foo!foo@example.com QUIT :quit message text'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['quit message text']
    assert pretrigger.text == 'quit message text'
    assert pretrigger.plain == 'quit message text'
    assert pretrigger.event == 'QUIT'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender is None


def test_join_pretrigger(nick):
    line = ':Foo!foo@example.com JOIN #Sopel'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['#Sopel']
    assert pretrigger.text == '#Sopel'
    assert pretrigger.plain == '#Sopel'
    assert pretrigger.event == 'JOIN'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == Identifier('#Sopel')


def test_tags_pretrigger(nick):
    line = '@foo=bar;baz;sopel.chat/special=value :Foo!foo@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {'baz': None,
                               'foo': 'bar',
                               'sopel.chat/special': 'value'}
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['#Sopel', 'Hello, world']
    assert pretrigger.text == 'Hello, world'
    assert pretrigger.plain == 'Hello, world'
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == '#Sopel'


def test_intents_pretrigger(nick):
    line = '@intent=ACTION :Foo!foo@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {'intent': 'ACTION'}
    assert pretrigger.ctcp is None
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['#Sopel', 'Hello, world']
    assert pretrigger.text == 'Hello, world'
    assert pretrigger.plain == 'Hello, world'
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == '#Sopel'


def test_unusual_pretrigger(nick):
    line = 'PING'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.ctcp is None
    assert pretrigger.hostmask is None
    assert pretrigger.line == line
    assert pretrigger.args == []
    assert pretrigger.text == 'PING'
    assert pretrigger.plain == ''
    assert pretrigger.event == 'PING'


def test_ctcp_intent_pretrigger(nick):
    line = ':Foo!foo@example.com PRIVMSG Sopel :\x01VERSION\x01'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.ctcp == 'VERSION'
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['Sopel', '']
    assert pretrigger.text == '\x01VERSION\x01'
    assert pretrigger.plain == ''
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == Identifier('Foo')


def test_ctcp_data_pretrigger(nick):
    line = ':Foo!foo@example.com PRIVMSG Sopel :\x01PING 1123321\x01'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.ctcp == 'PING'
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['Sopel', '1123321']
    assert pretrigger.text == '\x01PING 1123321\x01'
    assert pretrigger.plain == '1123321'
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == Identifier('Foo')


def test_ctcp_action_pretrigger(nick):
    line = ':Foo!foo@example.com PRIVMSG #Sopel :\x01ACTION Hello, world\x01'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {}
    assert pretrigger.ctcp == 'ACTION'
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['#Sopel', 'Hello, world']
    assert pretrigger.text == '\x01ACTION Hello, world\x01'
    assert pretrigger.plain == 'Hello, world'
    assert pretrigger.event == 'PRIVMSG'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == '#Sopel'


def test_ctcp_action_trigger(nick, configfactory):
    line = ':Foo!bar@example.com PRIVMSG #Sopel :\x01ACTION Hello, world\x01'
    pretrigger = PreTrigger(nick, line)

    config = configfactory('default.cfg', TMP_CONFIG)
    fakematch = re.match('.*', line)

    trigger = Trigger(config, pretrigger, fakematch)
    assert trigger.sender == '#Sopel'
    assert trigger.raw == line
    assert trigger.is_privmsg is False
    assert trigger.hostmask == 'Foo!bar@example.com'
    assert trigger.user == 'bar'
    assert trigger.nick == Identifier('Foo')
    assert trigger.host == 'example.com'
    assert trigger.event == 'PRIVMSG'
    assert trigger.match == fakematch
    assert trigger.group == fakematch.group
    assert trigger.groups == fakematch.groups
    assert trigger.groupdict == fakematch.groupdict
    assert trigger.args == ['#Sopel', 'Hello, world']
    assert trigger.plain == 'Hello, world'
    assert trigger.tags == {}
    assert trigger.ctcp == 'ACTION'
    assert trigger.account is None
    assert trigger.admin is True
    assert trigger.owner is True


def test_ircv3_extended_join_pretrigger(nick):
    line = ':Foo!foo@example.com JOIN #Sopel bar :Real Name'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.tags == {'account': 'bar'}
    assert pretrigger.hostmask == 'Foo!foo@example.com'
    assert pretrigger.line == line
    assert pretrigger.args == ['#Sopel', 'bar', 'Real Name']
    assert pretrigger.text == 'Real Name'
    assert pretrigger.plain == 'Real Name'
    assert pretrigger.event == 'JOIN'
    assert pretrigger.nick == Identifier('Foo')
    assert pretrigger.user == 'foo'
    assert pretrigger.host == 'example.com'
    assert pretrigger.sender == Identifier('#Sopel')


def test_ircv3_extended_join_trigger(nick, configfactory):
    line = ':Foo!foo@example.com JOIN #Sopel bar :Real Name'
    pretrigger = PreTrigger(nick, line)

    config = configfactory('default.cfg', TMP_CONFIG)

    fakematch = re.match('.*', line)

    trigger = Trigger(config, pretrigger, fakematch)
    assert trigger.sender == '#Sopel'
    assert trigger.raw == line
    assert trigger.is_privmsg is False
    assert trigger.hostmask == 'Foo!foo@example.com'
    assert trigger.user == 'foo'
    assert trigger.nick == Identifier('Foo')
    assert trigger.host == 'example.com'
    assert trigger.event == 'JOIN'
    assert trigger.match == fakematch
    assert trigger.group == fakematch.group
    assert trigger.groups == fakematch.groups
    assert trigger.args == ['#Sopel', 'bar', 'Real Name']
    assert trigger.plain == 'Real Name'
    assert trigger.account == 'bar'
    assert trigger.tags == {'account': 'bar'}
    assert trigger.ctcp is None
    assert trigger.owner is True
    assert trigger.admin is True


def test_ircv3_intents_trigger(nick, configfactory):
    line = '@intent=ACTION :Foo!bar@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)

    config = configfactory('default.cfg', TMP_CONFIG)
    fakematch = re.match('.*', line)

    trigger = Trigger(config, pretrigger, fakematch)
    assert trigger.sender == '#Sopel'
    assert trigger.raw == line
    assert trigger.is_privmsg is False
    assert trigger.hostmask == 'Foo!bar@example.com'
    assert trigger.user == 'bar'
    assert trigger.nick == Identifier('Foo')
    assert trigger.host == 'example.com'
    assert trigger.event == 'PRIVMSG'
    assert trigger.match == fakematch
    assert trigger.group == fakematch.group
    assert trigger.groups == fakematch.groups
    assert trigger.groupdict == fakematch.groupdict
    assert trigger.args == ['#Sopel', 'Hello, world']
    assert trigger.plain == 'Hello, world'
    assert trigger.tags == {'intent': 'ACTION'}
    assert trigger.ctcp is None
    assert trigger.account is None
    assert trigger.admin is True
    assert trigger.owner is True


def test_ircv3_account_tag_trigger(nick, configfactory):
    line = '@account=bar :Nick_Is_Not_Foo!foo@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)

    config = configfactory('default.cfg', TMP_CONFIG_ACCOUNT)
    fakematch = re.match('.*', line)

    trigger = Trigger(config, pretrigger, fakematch)
    assert trigger.admin is True
    assert trigger.owner is True


def test_ircv3_server_time_trigger(nick, configfactory):
    line = '@time=2016-01-09T03:15:42.000Z :Foo!foo@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)
    config = configfactory('default.cfg', TMP_CONFIG)
    fakematch = re.match('.*', line)

    trigger = Trigger(config, pretrigger, fakematch)
    assert trigger.time == datetime.datetime(
        2016, 1, 9, 3, 15, 42, 0, tzinfo=datetime.timezone.utc
    )

    # Spec-breaking string
    line = '@time=2016-01-09T04:20 :Foo!foo@example.com PRIVMSG #Sopel :Hello, world'
    pretrigger = PreTrigger(nick, line)
    assert pretrigger.time is not None
