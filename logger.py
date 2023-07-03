import os
import logging
import toml

config = toml.load('config.toml')
env = config['default'].get('env')

log = logging.getLogger('pickleLogger')

if env == "prod":
    from systemd.journal import JournalHandler
    journald_handler = JournalHandler(SYSLOG_IDENTIFIER='pickleprobe')
    log.addHandler(journald_handler)
    log.setLevel(logging.INFO)
else:
    stream_handler = logging.StreamHandler()
    log.addHandler(stream_handler)

log.setLevel(logging.INFO)
log.info(os.uname()[1])
