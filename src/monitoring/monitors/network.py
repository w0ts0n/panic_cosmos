import logging
from datetime import datetime, timedelta
from time import sleep
from typing import List, Optional

import dateutil

from src.alerting.channels.channel import ChannelSet
from src.monitoring.monitor_utils.get_json import get_cosmos_json
from src.monitoring.monitor_utils.live_check import live_check
from src.monitoring.monitors.monitor import Monitor
from src.node.node import Node
from src.utils.exceptions import NoLiveFullNodeException
from src.utils.redis_api import RedisApi


class NetworkMonitor(Monitor):

    def __init__(self, monitor_name: str, channels: ChannelSet,
                 logger: logging.Logger, redis: Optional[RedisApi],
                 all_full_nodes: List[Node], all_validators: List[Node]):
        super().__init__(monitor_name, channels, logger, redis)

        self._all_full_nodes = all_full_nodes
        self._all_validators = all_validators

        self.last_full_node_used = None
        self._last_height_checked = None

        self._redis_alive_key_timeout = \
            self._internal_conf.redis_network_monitor_alive_key_timeout
        self._redis_last_height_checked_key = \
            self._internal_conf.redis_network_monitor_last_height_key_prefix + \
            self._monitor_name
        self._redis_alive_key = \
            self._internal_conf.redis_network_monitor_alive_key_prefix + \
            self._monitor_name

        self.load_state()

    def load_state(self) -> None:
        # If Redis is enabled, load the last height checked, if any
        if self.redis_enabled:
            self._last_height_checked = self.redis.get_int(
                self._redis_last_height_checked_key, None)

            self.logger.debug(
                'Restored %s state: %s=%s', self._monitor_name,
                self._redis_last_height_checked_key, self._last_height_checked)

    def save_state(self) -> None:
        # If Redis is enabled, save the current last height checked and the
        # current time, indicating that the monitor was alive at this time
        if self.redis_enabled:
            self.logger.debug(
                'Saving network monitor state: %s=%s',
                self._redis_last_height_checked_key, self._last_height_checked)

            # Set last height checked key
            self.redis.set(self._redis_last_height_checked_key,
                           self._last_height_checked)

            # Set alive key (to be able to query latest update from Telegram)
            key = self._redis_alive_key
            until = timedelta(seconds=self._redis_alive_key_timeout)
            self.redis.set_for(key, str(datetime.now()), until)

    @property
    def node(self) -> Node:
        # Get one of the full nodes to use as data source
        for n in self._all_full_nodes:
            if live_check(n.rpc_url + '/health', self.logger):
                n.set_as_up(self.channels, self.logger)
                self.last_full_node_used = n
                return n
        raise NoLiveFullNodeException()

    def monitor(self) -> None:
        # Get abci_info and, from that, the last height to be checked
        abci_info = get_cosmos_json(self.node.rpc_url + '/abci_info',
                                    self._logger)
        last_height_to_check = int(abci_info['response']['last_block_height'])

        # If this is the first height being checked, ignore previous heights
        if self._last_height_checked is None:
            self._last_height_checked = last_height_to_check - 1

        # Consider any height that is after the previous last height
        height = self._last_height_checked + 1
        while height <= last_height_to_check:
            self._logger.info('%s obtaining data at height %s',
                              self._monitor_name, height)

            # Get block
            block = get_cosmos_json(self.node.rpc_url + '/block?height=' +
                                    str(height), self._logger)

            # Get validators participating in the precommits of last commit
            block_precommits = block['block']['last_commit']['precommits']
            non_null_precommits = filter(lambda p: p, block_precommits)
            block_precommits_validators = set(
                map(lambda p: p['validator_address'], non_null_precommits))
            total_no_of_missing_validators = \
                len(block_precommits) - len(block_precommits_validators)

            self._logger.debug('Precommit validators: %s',
                               block_precommits_validators)
            self._logger.debug('Total missing validators: %s',
                               total_no_of_missing_validators)

            # Call method based on whether block missed or not
            for v in self._all_validators:
                if v.pubkey not in block_precommits_validators:
                    block_time = block['block']['header']['time']
                    v.add_missed_block(
                        height - 1,  # '- 1' since it's actually previous height
                        dateutil.parser.parse(block_time, ignoretz=True),
                        total_no_of_missing_validators, self.channels,
                        self.logger)
                else:
                    v.clear_missed_blocks(self.channels, self.logger)

            self._logger.debug('Moving to next height.')

            # Move to next block
            height += 1

            # If there is a next height to check, sleep for a bit
            if height <= last_height_to_check:
                self.logger.debug('Sleeping for 0.5 second between heights.')
                sleep(0.5)

        self._last_height_checked = last_height_to_check