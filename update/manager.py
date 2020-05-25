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

__all__ = ("Manager", )


from .logger import getLogger
from .configuration import mu_conf, EnvVars
from .util import ModuleState, getDelay
import requests
import time


logger = getLogger(__name__.split(".", 1)[-1])


class Manager:

    def __get(self, url):
        response = requests.get(url=url)
        if not response.status_code == 200:
            raise RuntimeError(response.status_code)
        return response.json()

    def __getRemoteModules(self, url, mod_ids):
        modules = dict()
        for mod_id in mod_ids:
            try:
                modules[mod_id] = self.__get("{}/{}".format(url, mod_id))
            except Exception as ex:
                logger.error("can't retrieve module '{}' from registry - {}".format(mod_id, ex))
        return modules

    def __mergeConfigs(self, old: dict, new: dict):
        for key in old:
            for k, v in old[key]["service_configs"].items():
                if k in new[key]["service_configs"] and not v == new[key]["service_configs"][k]:
                    logger.debug("found user value for '{}'".format(k))
                    new[key]["service_configs"][k] = v

    def run(self):
        try:
            while True:
                time.sleep(getDelay())
                try:
                    local_mods = self.__get("{}/{}".format(mu_conf.MM.url, mu_conf.MM.api))
                    remote_mods = self.__getRemoteModules("{}/{}".format(mu_conf.MR.url, mu_conf.MR.api), local_mods.keys())
                    pending = list()
                    for mod_id in set(local_mods) & set(remote_mods):
                        logger.info("checking '{}' ...".format(local_mods[mod_id]["name"]))
                        if not local_mods[mod_id]["hash"] == remote_mods[mod_id]["hash"]:
                            pending.append(mod_id)
                            logger.info("update pending for '{}' ...".format(local_mods[mod_id]["name"]))
                    for mod_id in pending:
                        logger.info("merging configs for '{}' ...".format(local_mods[mod_id]["name"]))
                        configs = self.__get("{}/{}/{}".format(mu_conf.CS.url, mu_conf.CS.api, mod_id))
                        self.__mergeConfigs(configs, remote_mods[mod_id]["services"])
                    for mod_id in pending:
                        logger.info("updating '{}' ...".format(local_mods[mod_id]["name"]))
                        requests.patch(url="{}/{}/{}".format(mu_conf.MM.url, mu_conf.MM.api, mod_id), json={"state": ModuleState.inactive})
                        while True:
                            response = self.__get("{}/{}/{}".format(mu_conf.MM.url, mu_conf.MM.api, mod_id))
                            if response["state"] == ModuleState.inactive:
                                break
                            time.sleep(1)
                        remote_mods[mod_id]["id"] = mod_id
                        requests.post(url="{}/{}".format(mu_conf.MM.url, mu_conf.MM.api), json=remote_mods[mod_id])
                        requests.patch(url="{}/{}/{}".format(mu_conf.MM.url, mu_conf.MM.api, mod_id), json={"state": ModuleState.active})
                        logger.info("update for '{}' successful".format(local_mods[mod_id]["name"]))
                except Exception as ex:
                    logger.exception("error during update:".format(ex))
        finally:
            pass
