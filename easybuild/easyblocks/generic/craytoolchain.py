##
# Copyright 2015-2015 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for installing Cray toolchains, implemented as an easyblock

@author: Kenneth Hoste (Ghent University)
"""

from easybuild.easyblocks.generic.bundle import Bundle


KNOWN_PRGENVS = ['PrgEnv-cray', 'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi']


class CrayToolchain(Bundle):
    """
    Compiler toolchain: generate module file only, nothing to build/install
    """
    def make_module_dep(self):
        """
        Generate load/swap statements for dependencies in the module file
        """
        # build dict with info for 'module swap' statements for dependencies
        swap_info = {}
        for dep in self.toolchain.dependencies:
            mod_name = dep['full_mod_name']
            if not mod_name.startswith('PrgEnv-'):
                depname = '/'.join(mod_name.split('/')[:-1])
                swap_info.update({mod_name: depname})
        self.log.debug("Swap info for dependencies of %s: %s", self.full_mod_name, swap_info)

        txt = super(CrayToolchain, self).make_module_dep(swap_info=swap_info)

        # unload statements for PrgEnv-* modules must be included *first*
        comment = self.module_generator.comment("first, unload any PrgEnv module that may be loaded").strip()
        prgenv_unloads = ['', comment]
        for prgenv in KNOWN_PRGENVS:
            prgenv_unloads.append(self.module_generator.unload_module(prgenv).strip() + '\n')

        comment = self.module_generator.comment("next, load toolchain components")
        txt = '\n'.join(prgenv_unloads) + '\n' + comment + txt

        return txt

