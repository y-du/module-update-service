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


from .configuration import mu_conf, EnvVars
import datetime


__all__ = ("ModuleState", "getDelay")


class ModuleState:
    active = "active"
    inactive = "inactive"


def getDelay():
    x = datetime.datetime.today()
    if not any((mu_conf.Update.hour, mu_conf.Update.minute, mu_conf.Update.second)):
        y = x.replace(day=x.day, hour=x.hour, minute=x.minute, second=x.second, microsecond=0) + datetime.timedelta(seconds=mu_conf.Update.interval)
        delay = y - x
        return delay.total_seconds()
    if mu_conf.Update.second and not mu_conf.Update.minute and not mu_conf.Update.hour:
        y = x.replace(day=x.day, hour=x.hour, minute=x.minute, second=mu_conf.Update.second, microsecond=0)
        delta = datetime.timedelta(minutes=1)
    if mu_conf.Update.minute and not mu_conf.Update.second and not mu_conf.Update.hour:
        y = x.replace(day=x.day, hour=x.hour, minute=mu_conf.Update.minute, second=0, microsecond=0)
        delta = datetime.timedelta(hours=1)
    if mu_conf.Update.minute and mu_conf.Update.second and not mu_conf.Update.hour:
        y = x.replace(day=x.day, hour=x.hour, minute=mu_conf.Update.minute, second=mu_conf.Update.second, microsecond=0)
        delta = datetime.timedelta(hours=1)
    if mu_conf.Update.hour and not mu_conf.Update.minute and not mu_conf.Update.second:
        y = x.replace(day=x.day, hour=mu_conf.Update.hour, minute=0, second=0, microsecond=0)
        delta = datetime.timedelta(days=1)
    if mu_conf.Update.hour and any((mu_conf.Update.minute, mu_conf.Update.second)):
        y = x.replace(day=x.day, hour=mu_conf.Update.hour, minute=mu_conf.Update.minute or 0, second=mu_conf.Update.second or 0, microsecond=0)
        delta = datetime.timedelta(days=1)
    delay = y - x
    if delay.total_seconds() <= 0:
        y = y + delta
        delay = y - x
    return delay.total_seconds()
