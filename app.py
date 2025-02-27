"""
   Copyright 2020 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from update.logger import initLogger, getLogger
from update.configuration import mu_conf
from update.manager import Manager
import signal
import sys


initLogger(mu_conf.Logger.level)


logger = getLogger("app")


def sigtermHandler(_signo, _stack_frame):
    logger.warning("got SIGTERM - exiting ...")
    sys.exit(0)


update_manager = Manager()

signal.signal(signal.SIGTERM, sigtermHandler)
update_manager.run()
