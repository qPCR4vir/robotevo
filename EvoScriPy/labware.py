# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
"""
Worktable and labwares
======================

 - Worktable
 - Worktable.Location
 - Labware.Type
   + Specialized types:
     + DiTiRackType
     + CuvetteType 
 - Labware.Type.Series
 - Labware
   + Specialized labwares:
     + DitiRack
     + Cuvette

---------

"""

__author__ = 'qPCR4vir'


from pathlib import Path
import logging
import xml.etree.ElementTree as ET
base_dir = Path(__file__).parent.parent

class LiquidClass:

    def __init__(self, name:str, liquid_name:str= ""):
        """

        :param name:
        :param liquid_name:
        """
        self.name = name
        self.liquid_name = liquid_name

    def __str__(self):
        return self.name


class LiquidClassDefault(LiquidClass):

    def __init__(self, name:str, liquid_name:str= ""):
        LiquidClass.__init__(self, name, liquid_name)
        self.derived = {}


class LiquidClassDerived(LiquidClass):

    def __init__(self, raw_name:str, origen:LiquidClassDefault):
        raw = raw_name.split(';')


class LiquidClasses:

    def __init__(self, database:Path):
        custom_file = database / 'CustomLCs.XML'
        default_file = database / 'DefaultLCs.XML'
        self.all = {}
        try:
            self._read_def_liq_class_txt_file(default_file)

        except OSError as err:
            logging.info("Reading Default LCs: {0} found. Will generate a new one.".format(err))
            try:
                self._read_def_liq_class_xml_file(default_file)
            except  OSError as err:
                logging.info("OS error: {0}".format(err))

        try:
            self._read_cus_liq_class_txt_file(custom_file)

        except OSError as err:
            logging.info("No: {0} found. Will generate a new one.".format(err))
            try:
                self._read_cus_liq_class_xml_file(custom_file)
            except OSError as err:
                logging.info("OS error: {0}".format(err))

    def _read_cus_liq_class_xml_file(self, custom_file):
        tree = ET.parse(custom_file)
        root = tree.getroot()
        with open(custom_file.with_suffix('.txt'), 'w', encoding='Latin-1', newline='\r\n') as custom:
            for lc in root.findall('LiquidClass'):
                name = lc.get('name')
                liquid_name = lc.get('liquidName')
                logging.debug("name='" + name + "' :liquid Name='" + liquid_name + "'")
                custom.write(name + "\t" + liquid_name + "\t" + "\n")
                lc = LiquidClassDefault(name, liquid_name)
                self.all[lc.name] = lc
                # logging.debug("to txt- name='" + lc.name + " :liquid Name='" + lc.liquid_name + "'")

    def _read_cus_liq_class_txt_file(self, custom_file):
        with open(custom_file.with_suffix('.txt'), 'r', encoding='Latin-1') as custom:
            logging.info('Parsing: ' + str(custom_file.with_suffix('.txt')))
            for lc in custom:
                # logging.debug("Line: " + lc)
                lc = lc.split('\t')
                lc = LiquidClassDefault(name=lc[0], liquid_name=lc[1])
                self.all[lc.name] = lc
                # logging.debug("from txt- name='" + lc.name + " :liquid Name='" + lc.liquid_name + "'")

    def _read_def_liq_class_xml_file(self, default_file):
        logging.info("Going to parse LCs from " + str(default_file))
        tree = ET.parse(default_file)
        root = tree.getroot()
        with open(default_file.with_suffix('.txt'), 'w', encoding='Latin-1', newline='\r\n') as default:
            logging.info('Writing: ' + str(default_file.with_suffix('.txt').relative_to(base_dir)))
            for lc in root.findall('LiquidClass'):
                name = lc.get('name')
                liquid_name = lc.get('liquidName')
                logging.debug("name='" + name + "' :liquid Name='" + liquid_name + "'")
                default.write(name + "\t" + liquid_name + "\t" + "\n")
                lc = LiquidClassDefault(name, liquid_name)
                self.all[lc.name] = lc
                # logging.debug("to- name='" + lc.name + " :liquid Name='" + lc.liquid_name + "'")

    def _read_def_liq_class_txt_file(self, default_file):
        with open(default_file.with_suffix('.txt'), 'r', encoding='Latin-1') as default:
            logging.info('Parsing: ' + str(default_file.with_suffix('.txt').relative_to(base_dir)))
            for lc in default:
                lc = lc.split('\t')
                lc = LiquidClassDefault(name=lc[0], liquid_name=lc[1])
                self.all[lc.name] = lc
                # logging.debug("from txt- name='" + lc.name + " :liquid Name='" + lc.liquid_name + "'")


class WorkTable:
    """
    Collection of carriers.types and Labware.types and pos of instances
    """

    cur_worktable = None

    def __init__(self, template_file, robot_protocol=None, grids=67, sites=127):

        self.labware_series   = {}  # typeName: Series. For each type - a series of labwares (with self have locations)
        self.reagents         = {}  # connect each reagent name with the reagent self
        self.carriers_grid    = []
        self.carriers_no_grid = []  # in reality in grid with index > real number of grids?

        self.template       = []

        self.n_sites            = sites
        self.grids              = [None] * grids            # TODO take this from the template file
        self.template_file_name = None

        self.def_WashWaste      = None
        self.def_WashCleaner    = None
        self.def_DiTiWaste      = None
        self.def_DiTi_type      = None

        WorkTable.cur_worktable  = self

        if isinstance(template_file, list):
            self.template = template_file
            logging.debug("Template file is a list.")
        else:
            logging.debug("Set template file: " + str(template_file.relative_to(base_dir)))
            self.template = self.parse_worktable_file(template_file, robot_protocol)
            self.template_file_name = template_file

    class Location:
        """
        One location in a WorkTable
        """

        def __init__(self, grid=None, site=None, carrier=None, carrier_site=None, worktable=None):
            """
            :param grid: int, 1-67.   worktable grid. Carrier grid position
            :param site: int, 0 - 127. Site on carrier (on RAck?) = labware location - (site on carrier - 1) !!!!!
            :param carrier:
            :param carrier_site:
            """

            # A Location have sense only in a WorkTable
            self.worktable = worktable or WorkTable.cur_worktable
            assert isinstance(self.worktable, WorkTable)

            self.carrier = carrier
            if grid is None:
                assert isinstance(carrier, Carrier)
                grid = carrier.grid
            assert 1 <= grid <= len(self.worktable.grids)
            self.grid = grid
            if self.carrier is None:
                self.carrier = self.worktable.carriers_grid[self.grid]

            site -= 1                                               # TODO revise - it will be an error if site is None
            assert 0 <= site <= self.worktable.n_sites
            self.site = site
            self.carrier_site = carrier_site                        # TODO revise
            if not self.carrier_site:
                self.carrier_site = self.site                       # TODO revise
            if carrier is not None:
                assert isinstance(carrier, Carrier)
                assert 0 <= self.carrier_site < carrier.type.n_sites, ( "There is no site " + str(site) + " carrier type "
                                                                       +  carrier.type.name + 'with number of sites '
                                                                       + str(carrier.type.n_sites) )


        def __str__(self):
            return "grid:{grid:d}, site:{site:d}".format(grid=self.grid, site=self.site + 1)

    class File:
        def __init__(self, input, output, worktable):
            self.worktable                  = worktable
            self.output                     = output
            self.input                      = input
            self.check_summa    : str       = None
            self.date_time      : str       = None
            self.user           : str       = None

        def write(self, worktable):
            lines = [
                self.check_summa,
                self.date_time + " " + self.user,
                " "*128,
                self.roll,               # + " "*115,
                "--{ RES }--",
                "V;" + self.file.version,
                "--{ CFG }--",
                ";".join("999", self.file.n1, self.file.n2, self.file.n3),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",

            ]
            for line in lines:
                self.output.write(line)

        def grid_carrier_line(self):
            line = "14;"
            labw = {}

    def parse_worktable_file(self, template_file, robot_protocol):
        if not template_file:
            return []                                                         # RETURN

        template_list = []                                                    # a grid-line first list the types
        with open(template_file, 'r', encoding='Latin-1') as tmpl:
            # parsing_grid=False
            self.file = WorkTable.File(tmpl, None, self)

            template_list += self._read_worktable_header(tmpl)
            template_list += self._read_worktable_carriers_grid(tmpl, robot_protocol)
            template_list += self._read_worktable_labwares_grid(tmpl, robot_protocol)

            for line in tmpl:
                template_list += [line]
                if line.startswith("--{ RPG }--"):                           # end of the worktable description
                    break                                                     # BREAK
                line = line.split(';')

                if line[0] != "998":
                    continue                                                  # CONTINUE

        self.template = template_list
        self.template_file_name = template_file
        return template_list

    def _read_worktable_header(self, template):
        logging.debug("Read header.")
        template_list = []  # a grid-line first list the types

        line = template.readline()
        template_list += [line]
        self.file.check_summa = line

        line = template.readline()
        template_list += [line]
        self.file.date_time, self.file.user = line.split()

        line = template.readline()
        template_list += [line]

        line = template.readline()
        template_list += [line]
        self.file.roll = line

        line = template.readline()
        template_list += [line]
        assert line.startswith("--{ RES }--")

        line = template.readline()
        template_list += [line]
        v, self.file.version = line.split(';')
        assert v == "V"

        line = template.readline()
        template_list += [line]
        assert line.startswith("--{ CFG }--")

        line = template.readline()
        template_list += [line]
        l999, self.file.n1, self.file.n2, self.file.n3 = line.split(';')
        assert l999 == "999"
        return template_list

    def _read_worktable_carriers_grid(self, template, robot_protocol):
        template_list = []  # a grid-line first list the types

        line = template.readline()
        template_list += [line]
        carriers = line.split(';')
        assert carriers[0] == "14"
        self.carriers_grid = []
        for idx in carriers[1:-1]:
            if idx == "-1":
                self.carriers_grid += [None]
                continue
            idx = int(idx)

            self.carriers_grid += [idx]                   # <--------- set carriers_grid += [idx]

            if idx not in robot_protocol.carrier_types().by_index:
                logging.warning("Unknow carrier index " + str(idx)
                      + " in grid " + str(len(self.carriers_grid) - 1))
            else:
                logging.info("Carrier: " + robot_protocol.carrier_types().by_index[idx].name
                      + " found in line carrier-grid for grid " + str(len(self.carriers_grid) - 1))
        logging.info("Detected " + str(len(self.carriers_grid)) + " grids.")
        return template_list

    def _read_worktable_labwares_grid(self, template, robot_protocol):
        logging.debug("Reading grids ")
        grid_num = -1

        template_list = []
        labware_types = []  # set to an empty, False value

        for line in template:
            template_list += [line]
            # logging.debug("Reading grid " + line)
            line = line.split(';')
            assert line[0] == "998"

            if not labware_types:     # continue to scan fro carrier grid line with labwares types first
                grid_num += 1
                # logging.debug("Reading grid " + str(grid_num) + " of " + str(len(self.carriers_grid)))
                # logging.debug("1-with " + str(labware_types) + " labwares")
                if grid_num >= len(self.carriers_grid):  # len(self.grids):
                    if line[1] != "2":
                        logging.warning("Non ended 2 Grid " + str(grid_num) \
                                                           + " line " + str(len(template_list)) \
                                                           + ": " + template_list[-1])
                    return template_list
                labware_types = line[2:-1]
                assert int(line[1]) == len(labware_types), "Grid " + str(grid_num) \
                                                           + " line " + str(len(template_list)) \
                                                           + ": " + template_list[-1]

            else:     # we have read the types first, now we need to read the labwares labels
                carrier_type_idx = self.carriers_grid[grid_num]
                carrier_type = robot_protocol.carrier_types().by_index[carrier_type_idx]
                assert len(labware_types) == carrier_type.n_sites
                carrier = Carrier(carrier_type=carrier_type, grid=grid_num, worktable=self)
                self.carriers_grid[grid_num] = carrier
                for site, (labw_type_name, labw_label) in enumerate(zip(labware_types, line[1:-1])):
                    if not labw_type_name:
                        if labw_label:
                            logging.warning("Going to ignore entry - The worktable template have a labware label '" +
                                      labw_label + "' in grid, site: " + str(grid_num) + ", " + str(site) +
                                      " but no labware type")
                        continue  # CONTINUE:
                    # if labw_type_name and not labw_label:
                    #    logging.warning("WARNING!! Going to ignore entry - The worktable template have a labware type '" +
                    #              labw_type_name + "' in grid, site: " + str(grid_num) + ", " + str(site) +
                    #              " but no labware")
                    #    continue  # CONTINUE:
                    loc = WorkTable.Location(carrier=carrier, site=site + 1, worktable=self)
                    labw = Labware.create(labw_type_name, loc, labw_label)
                    if labw:
                        pass  # self.add_labware(labw)
                    else:
                        logging.warning("The worktable template have a labware labeled '" +
                              labw_label + "' in grid, site: " + str(grid_num) + ", " + str(site) +
                              " but there is no registered labware type '" + labw_type_name + "'")
                labware_types = []

    def add_new_labware(self, labware, loc: Location = None):
        """
        This will be the first location of this labware. Don't remove from possible old location.
        :param labware:
        :param loc:
        :return:
        :raise "This WT have only " + len(self.grid) + " grid.":
        """

        assert isinstance(labware, Labware)
        if isinstance(loc, WorkTable.Location):                                 # loc take priority
            labware.location = loc
        assert isinstance(labware.location, WorkTable.Location)

        if not isinstance(labware.location.worktable, WorkTable):
            labware.location.worktable = self
        else:
            assert labware.location.worktable is self

        if labware.location.grid >= len(self.grids):
            raise "This WorkTable have only " + str(len(self.grids)) + " grids. Not " + str(loc.grid)
        if labware.location.carrier:
            assert labware.location.grid == labware.location.carrier.grid
            assert labware.location.carrier is self.carriers_grid[labware.location.grid]
        else:
            labware.location.carrier = self.carriers_grid[labware.location.grid]
        labware.location.carrier.add_labware(labware, labware.location.carrier_site)

        for type_name, labw_series in self.labware_series.items():                # loop lab_types already in worktable
            for labw in labw_series.labwares:                               # loop labwares in that series

                if labw is labware:                                         # already there ??
                    logging.warning("The worktable template already have this labware. " +
                          labw.label + "' in grid, site: " + str(loc.grid) + ", " + str(loc.site + 1))
                    return

                if      labware.location.grid == labw.location.grid and \
                        labware.location.site == labw.location.site:

                    logging.warning("Trying to add a labware. The worktable template already have a labware with label '"
                          + labw.label + "' in grid, site: " + str(loc.grid) + ", " + str(loc.site + 1))

        if labware.type.name not in self.labware_series:              # first time this type of labware is in this worktable
            self.labware_series[labware.type.name] = labware.type.create_series(labware)
        else:
            self.labware_series[labware.type.name].add(labware)

        # todo add to self.grid labware.location.grid dict site, labware

    def add_labware(self, labware, loc : Location):
        """

        :param labware:
        :param loc:
        :return:
        :raise "This WT have only " + len(self.grid) + " grid.":
        """

        assert isinstance(labware, Labware)
        assert isinstance(loc, WorkTable.Location)

        if isinstance(labware.location, WorkTable.Location):
            if isinstance(labware.location.worktable, WorkTable):
                if isinstance(loc.worktable, WorkTable):
                    if labware.location.worktable is loc.worktable:
                        labware.location = loc                                  # the simplest intention: move it
                        return
                    else:
                        labware.location.worktable.retire_labware(labware)       # remove from previous worktable
                        return
                else:                                                           # no new worktable
                    loc.worktable = labware.location.worktable                  # just move it in current worktable
                    labware.location = loc
                    return

        # assert labware.series is None, "For now we assume labware with no location or worktable have no series"

        self.retire_labware(labware)                                             # remove from previous worktable/series
        loc.worktable.add_new_labware(labware, loc)                             # add to the new worktable

    def get_current_labware(self, labware):

        if isinstance(labware, Labware):
            series = labware.series
        else:
            if isinstance(labware, Labware.Type):
                labware = labware.name
            if labware not in self.labware_series:                        # todo  what if this is the label of the labware
                raise Exception("Labware '" + labware + "' was not found in worktable: " + self.template_file_name)

            series = self.labware_series[labware]

        return series.current

    def set_current(self, labware):
        assert isinstance(labware, Labware)
        series = self.labware_series[labware.type.name]
        assert isinstance(series, Labware.Type.Series)
        series.current = labware

    def get_labware(self, label: (str, int) = None, labw_type=None):
        """
        Return a `Labware` already created manually or after the worktable template was scanned.
        The labware type is optional (if you provide a label), but it makes the search more robust.
        It is mandatory if you provide no label or an index (no label will return the labware with index `0` in the
        series of labware of the desired type). The type may be a label or a predefined `Labware.Type`
        :type labw_type: (str, Labware.Type)
        :param label:
        :return Labware
        """
        labware = None
        if labw_type is None:
            assert isinstance(label, str), "Please get at least the labware type or label"
            for series in self.labware_series.values():
                if label in series.labels:
                    assert labware is None, ("ERROR: two labware have the label '"  + label
                                            + "' : please indicate the labware type to disambiguate")
                    labware = series.labels[label]
                    assert isinstance(labware, Labware)

            assert labware is not None, ("ERROR: no labware with the label '" + label
                                         + "' was found in worktable: " + str(self.template_file_name))
            return labware

        if isinstance(labw_type, Labware.Type):
            labw_type = labw_type.name
        assert isinstance(labw_type, str)
        series = self.labware_series[labw_type]

        if isinstance(label, str):
            if label in series.labels:
                return series.labels[label]
            raise Exception("ERROR: no labware '" + labw_type + "' with the label '" + label
                            + "' was found in worktable: " + str(self.template_file_name))

        if label is None:
            label = 0
        assert isinstance(label, int), "ERROR: wrong label type"
        return series.labwares[label]

    def set_first_pos(self, labw_type_name=None, posstr=None):
        """
        Default to DITI if no labw_type_name is given. chooses a labware by label and set next well or tip to be used.
        :param labw_type_name:
        :param posstr:
        :return:
        """

        if labw_type_name:
            labw = self.get_current_labware(labw_type_name)
            assert labw, "Failed to find first position."

        else:
            labw = self.get_DITI_series().current
            assert labw, "Failed to find first DITI position."

        if posstr is None:
            posstr = ""

        pos = posstr.split('-')

        if len(pos) == 2:                       # assume posstr = 'N-w
            labw = labw.series[int(pos[0])-1]   # were N is the number of the labw in the series
            fpos = pos[1]                       # and w is the desired position on that labw
        else:
            # labw = labws[0]                   # todo use the current. ? or the first ??
            fpos = pos[0]

        return labw, fpos

    def retire_labware(self, labw):
        assert isinstance(labw, Labware )

        if labw.type.name in self.labware_series:
            assert labw.series is self.labware_series[labw.type.name]

        if isinstance(labw.series, Labware.Type.Series):
            labw.series.remove(labw)

        carrier = None
        if labw.location.carrier:
            carrier = labw.location.carrier
        else:
            carrier = self.carriers_grid[labw.location.grid]
        assert labw is carrier.labwares[labw.location.carrier_site]
        carrier.labwares[labw.location.carrier_site] = None
        labw.location = None
        return labw

    def replace_with_new(self, labw, label):
        assert isinstance(labw, Labware )
        loc = labw.location
        self.retire_labware(labw)
        return labw.type.create_labware(loc, label)

    def set_def_DiTi(self, tips):                 # :Labware.DITIrackType) ->Labware.DITIrackType:
        old = self.def_DiTi_type
        self.def_DiTi_type = tips
        return old

    def get_DITI_series(self, rack =None):
        """

        :type rack:(str, DITIrackType, DITIrack, DITIrackTypeSeries)
        """
        if isinstance(rack, DITIrackTypeSeries):  # get the series directly
            return rack

        if isinstance(rack, DITIrack):
            return rack.series

        if rack is None:
            rack = self.def_DiTi_type.name

        if isinstance(rack, DITIrackType):
            rack = rack.name

        assert isinstance(rack, str)

        if rack in self.labware_series:
            return self.labware_series[rack]

        logging.warning("No labware type registered with label: " + rack)


class Frezeer (WorkTable):
    def __init__(self):
        pass
        # todo logging.error("********  Implement Frezer  ***** ")
        # WorkTable.__init__(self)


stock = Frezeer()


class Carrier:
    """
    Collection of Labwares sites, filled with labwares...
    """

    class Types:

        def __init__(self, carrier_file: Path):
            self.by_name = {}
            self.by_index = {}
            self.parse_file(carrier_file)

        def parse_file(self, carrier_file=None):
            if not carrier_file:
                return []  # RETURN
            with open(carrier_file, 'r', encoding='Latin-1') as config:
                logging.info("Parsing carriers types from " + str(carrier_file.relative_to(base_dir)))
                for line in config:
                    if line.startswith("13;"):  # new Carrier
                        # logging.debug("line-" + line)
                        line = line.split(';')
                        name = line[1]
                        idx, u = line[2].split("/")
                        sites = line[-3]
                        self.add_type(Carrier.Type(name, idx=int(idx), n_sites=int(sites)))

        def add_type(self, carrier_type):
            assert isinstance(carrier_type, Carrier.Type)
            assert carrier_type.name not in self.by_name, "Duplicate Carrier name: " + carrier_type.name
            assert carrier_type.idx not in self.by_index, "Duplicate Carrier index: " + str(carrier_type.idx)
            self.by_name[carrier_type.name] = carrier_type
            self.by_index[carrier_type.idx] = carrier_type

    class Type:

        def __init__(self, name, idx: int = None, widht_in_grids: int = None, n_sites: int = None):
            self.idx                    = idx
            self.widht_in_grids         = widht_in_grids
            self.n_sites                = n_sites
            self.allowed_labwares_types = []
            self.name                   = name

        def __str__(self):
            return self.name

        def __repr__(self):
            return ((self.name or '-') + '[' + (str(self.idx) or '-') + ']')

    def __init__(self,
                 carrier_type : Type,
                 grid         : int,
                 label        : str       = None,
                 worktable    : WorkTable = None):

        worktable = worktable or WorkTable.cur_worktable
        self.grid = grid
        self.type = carrier_type
        self.labwares = [None] * self.type.n_sites
        self.label = label

    def add_labware(self, labware, site):
        if labware.type.name not in self.type.allowed_labwares_types:
            #logging.warning("The labware '" + labware.type.name + ":" + labware.label + "' is not allowed in carrier '"
            #      + self.type.name    + ":" + str(self.label))
            logging.info('            self.allow_labware("' + self.type.name + '", "' + labware.type.name + '")')

        if site >= self.type.n_sites:
            raise "This carrier " + self.type.name + ":" + self.label \
                  + " have only " + str(self.type.n_sites) + " sites."

        if self.labwares[site] is not None:
            logging.warning("Warning: you replaced the labware '" + self.labwares[site].type.name + ":"
                                                        + self.labwares[site].label)

        self.labwares[site] = labware
        if labware.location.grid != self.grid:      # ?????????
            if labware.location.grid is not None:
                logging.warning("Original grid changed to that of the Rack.")
            labware.location.grid = self.grid

    def __str__(self):
        return (self.type.name or '-') + ': ' + (self.label or '-')

    def __repr__(self):
        return str(self)


class Well:
    def __init__(self, labware, Well_Offset):
        self.labware = labware
        assert isinstance(Well_Offset, int)
        self.offset = Well_Offset
        self.selFlag = False
        self.label = ""
        self._vol = 0.0
        self._reagent = None
        self._actions = []
        # self.track = None           # todo use this to check what the tips uses?

        self.vol = 0.0
        self.reagent = None
        self.actions = []           # todo transfer actualize this ? how this works?

    def __str__(self):
        return "well {pos:d} in labware {lab:s}: {label:s} with {vol:.1f} uL of reagent {what:s}"\
                .format(pos  =self.offset+1,
                        lab  =self.labware.label,
                        label=self.label,
                        vol  =self.vol,
                        what = str(self.reagent or ''))
    
    class Action:
        def __init__(self, volume:float, origin=None):
            self.origin = origin
            self.volume = volume
            
        def __str__(self):
            strr = "aspirate " if self.volume < 0 else "dispense "
            strr += str(self.volume) + " µL of " + str(self.origin)
            return strr

    def log(self, vol, origin=None):
        self.actions += [Well.Action(vol, origin if origin else self)]

    def select(self, sel=True):
        self.selFlag = sel

    @property
    def vol(self):
        return self._vol

    @vol.setter
    def vol(self, newvol):
        self._vol = newvol

    @property
    def reagent(self):
        return self._reagent

    @reagent.setter
    def reagent(self, reagent):
        self._reagent = reagent

    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, actions):
        self._actions = actions


class conectedWell(Well):
    @property
    def vol(self):
        return self.labware.vol

    @vol.setter
    def vol(self, newvol):
        self.labware.vol = newvol

    @property
    def reagent(self):
        return self.labware.reagent

    @reagent.setter
    def reagent(self, reagent):
        self.labware.reagent = reagent

    @property
    def actions(self):
        return self.labware.actions

    @actions.setter
    def actions(self, actions):
        self.labware.actions = actions


banned_well = object()                                 # Well(None, 0)


def count_tips(TIP_MASK : int) -> int:
    n = 0
    while TIP_MASK:
        n += (TIP_MASK & 1)
        TIP_MASK = TIP_MASK >> 1
    return n


class Tip:    # OK play with this idea
    def __init__(self, rack_type):
        assert isinstance(rack_type, DITIrackType) or rack_type is Fixed_Tip
        self.vol = 0
        self.type = rack_type

    def __str__(self):
        return "tip {type:s} with {vol:.1f} uL".format(type=self.type.name, vol=self.vol)


class usedTip(Tip):
    def __init__(self, tip : Tip, origin=None):
        Tip.__init__(self, tip.type)
        self.vol = tip.vol
        self.origin = origin

    def __str__(self):
        return " Used " + Tip.__str__(self)+" of {what:s}".format(what=str(self.origin))


class Labware:

    # typeName label-string from template worktable file: labwares class-name.
    # Mountain a list of labwares types
    # like:  {'Trough 100ml': <class 'EvoScriPy.Labware.Labware.CuvetteType'>}
    types = {}

    class Type:

        class Series:

            def __init__(self, labware):                                # labware: Labware
                assert isinstance(labware, Labware)
                self.labwares   = []
                self.labels     = {}
                self.type       = labware.type
                self.add(labware)
                self.current    = labware
                logging.info("Created " + str(self))

            def __str__(self):
                return "serie of {n:d} {type:s}".format(n=len(self.labwares), type=self.type.name)

            def __repr__(self):
                return str(self.nCol) or '-'

            def add(self, labware):                                    # labware : Labware
                assert self.type is labware.type
                self.labwares.append(labware)
                self.labels[ labware.label ] = labware
                labware.series               = self

            def remove(self, labware):
                assert isinstance(labware, Labware)
                assert self is labware.series
                if labware is self.current:
                    self.set_next()
                    assert self.current is not labware

                del self.labwares[labware]
                del self.labels[ labware.label ]
                labware.series = None

            def __iadd__(self, labware):                                # labware : Labware
                self.add(labware)

            def set_next(self):                                         #  ->  (Labware, bool): labware: Labware
                """
                Set current to the next of self.current
                :rtype: (Labware, bool) = (the next labware , serie's current has rotated to the first
                :param labware:
                """
                self.current, rotated = self.show_next()
                return self.current, rotated

            @staticmethod
            def set_current_next_to(labware):                                          #  ->  (Labware, bool): labware: Labware
                assert isinstance(labware, Labware)
                labware.series.current = labware
                return labware.series.set_next()

            @staticmethod
            def show_next_to(labware):                                          #  ->  (Labware, bool): labware: Labware
                assert isinstance(labware, Labware)
                return labware.series.show_next(labware)

            def show_next(self, labware = None):                           #  ->  (Labware, bool): labware: Labware
                """
                return next to self.current
                :rtype: (Labware, bool) = (the next labware , serie's current has rotated to the first
                :param labware:
                """

                if labware is None:
                    labware = self.current
                logging.debug("Showing next to " + labware.label)
                assert self is labware.series

                idx = self.labwares.index(labware) + 1

                if idx == len(self.labwares):
                    return self.labwares[0], True
                else:
                    return self.labwares[idx], False

            def __len__(self):
                return len(self.labwares)

        def __init__(self, name, nRow, nCol=1, max_vol=None):
            assert name not in Labware.types, "Duplicate labware type name: " + name
            self.name           = name
            self.nRow           = nRow
            self.nCol           = nCol
            self.max_vol        = max_vol
            Labware.types[name] = self

        def __str__(self):
            return "{type:s}".format(type=self.type.name)

        def __repr__(self):
            return str(self.nCol) or '-'

        def size(self) -> int:
            return self.nRow * self.nCol

        def create_labware(self, loc, label):
            labw = Labware(self, label, loc)
            return labw

        def create_series(self, labware):
            return Labware.Type.Series(labware)

    class Position:
        def __init__(self, row, col=1):
            self.row = row
            self.col = col

    def __init__(self,
                 type    : Type,
                 label   : str,
                 location: WorkTable.Location = None):
        """

        :param type:
        :param label:
        :param location:

        """
        worktable = None

        if isinstance(location, WorkTable.Location):    # location take priority
            worktable = location.worktable
            if not isinstance(worktable, WorkTable):
                worktable = WorkTable.cur_worktable
                if isinstance(worktable, WorkTable):
                    location.worktable = worktable      # avoid wt.add_labware "moving" new labware

        self.location   = location
        self.type       = type
        self.label      = label
        self.series     = None
        self.Wells      = []

        if isinstance(worktable, WorkTable):
            worktable.add_new_labware(self, location)

        self.init_wells()
        logging.info("Created labware " + str(self) + " in " + str(self.location))

    def __str__(self):
        return "{type:s}:{label:s}".format(type=self.type.name, label=self.label)


    def __repr__(self):
        return ((self.name or '-') + '[' + (str(self.nRow) or '-')
                                         + (str(self.nCol) or '-')    + ']')

    @staticmethod
    def create(labw_t_name  : str,
               loc          : WorkTable.Location,
               label        : str):
        labw_t = Labware.types.get(labw_t_name)
        if not labw_t:
            logging.warning("There is not labware type defined with label '" + labw_t_name + "'. ")
            return None
        assert isinstance(labw_t, Labware.Type)
        labw = labw_t.create_labware(loc, label)
        return labw

    def init_wells(self):
        self.Wells = [Well(self, offset) for offset in range(self.type.size())]

    def autoselect(self, offset=0, maxTips=1, replys=1):   # OK make this "virtual". Implement cuvette
        """

        :param offset:
        :param maxTips:
        :param replys:
        :return:
        """
        nWells = self.type.size()
        maxTips = min(replys, maxTips)
        assert nWells >= offset + maxTips, "Can not select to far"  # todo better msg
        self.selectOnly(range(offset, offset + maxTips))
        return maxTips

    def offset(self, row_pos, col=1):
        assert row_pos is not None

        if isinstance(row_pos, Well):
            assert row_pos.labware is self, "This is a well from another labware."
            return row_pos.offset

        if isinstance(row_pos, str):
            assert col == 1, "Please, define the column only in the row string."
            return self.offsetFromName(row_pos)

        if isinstance(row_pos, Labware.Position):
            col = row_pos.col
            row_pos = row_pos.row

        if isinstance(row_pos, int):
            return row_pos - 1 + (col - 1) * self.type.nRow

        assert len(row_pos.replicas) == 1, "Failed to assume a Reagent with only one replica (aliquot)"
        return self.offset(row_pos, col)

        # assert False, "Unknow row type"

    def offsetFromName(self, wellName):
        row = ord(wellName[0]) - ord('A') + 1
        col = int(wellName[1:])
        return self.offset(row, col)

    def position(self, offset):
        return self.Position(offset % self.type.nCol + 1, offset // self.type.nCol + 1)

    def find_free_wells(self, n=1, init_pos=0) -> (bool, [Well]):
        continuous = True
        free_wells = []
        for i in range(init_pos, len(self.Wells) - n+1):
            if any(w.reagent for w in self.Wells[i:i + n]):
                continue
            return continuous, self.Wells[i:i + n]
        for w in self.Wells[init_pos:]:
            if w.reagent:
                continue
            free_wells += [w]
            if len(free_wells) == n:
                break
        continuous = all((free_wells[i].offset+1 == free_wells[i+1].offset)
                            for i in range(len(free_wells)-1))
        return continuous, free_wells

    def put(self, reagent, pos=None, num_of_aliquots=None) -> list:
        """
        Put a reagent with replicas in the given wells positions of this labware,
        and return a list of the wells used

        :param reagent:
        :param pos: [wells]; if int or [int] will be assumed 1-based not 0-based
        :param num_of_aliquots: number of replicas
        :return:
        """

        num_of_aliquots = num_of_aliquots or reagent.min_num_aliq

        if pos is None:                                          # find self where to put the num_of_aliquots of this reagent
            continuous, pos = self.find_free_wells(num_of_aliquots)
            if len(pos) < num_of_aliquots:
                raise NoFreeWells(labware=self,
                                  error=' to put ' + str(num_of_aliquots) + ' aliquots of reagent - ' + str(reagent))

            assert num_of_aliquots == len(pos), 'putting reagent - ' + str(reagent) + ' - into Labware: ' \
                                                + str(self) + ' different replica number (' + str(num_of_aliquots) \
                                                + ') and number of positions = ' \
                                                + str(pos)        # num_of_aliquots = len(pos)   # todo What to do?

        elif isinstance(pos, list):                              # put one replica on each of the given wells position
            if num_of_aliquots <= len(pos):
                pass                           # num_of_aliquots = len(pos)
            else:
                assert (num_of_aliquots == len(pos)), self.label + ": Can not put " + ' aliquots of reagent ' + str(reagent) \
                                                     + " in " + str(len(pos)) + " positions"

        elif isinstance(pos, Well):                              # put one replica beginning from the given position
            # assert pos.labware is self, "Trying to put the reagent in another labware?"
            pos = pos.labware.Wells[pos.offset: pos.offset + num_of_aliquots]
            # pos = self.Wells[pos.offset: pos.offset + num_of_aliquots]
        else:
            pos = self.offset(pos)            # todo: revise  !!!!!!!!!!!!!!
            pos = self.Wells[pos: pos + num_of_aliquots]
            # pos = self.offset(pos) + 1
            # pos = range(pos, pos + num_of_aliquots)

        aliquots = []    # a list of labware-wells, where the replicas for this reagent are.
        for w in pos:
            if num_of_aliquots == 0:
                return aliquots
            w = w if isinstance(w, Well) else self.Wells[self.offset(w)]
            assert not w.reagent, self.label + ": Can not put " + reagent.name + " in position " + str(
                                  w.offset + 1) + " already occupied by " + w.reagent.name
            w.reagent = reagent
            # w.labware = self
            aliquots += [w]
            num_of_aliquots -= 1

        if not len(aliquots):
            pass
        assert len(aliquots) > 0, 'There are no more free wells in Labware ' + str(self) \
                                  + ' to put aliquots of reagent - ' + str(reagent)

        return aliquots

    def clearSelection(self):
        for well in self.Wells:
            well.selFlag = False
        return self

    def selected(self) -> list :
        """
        :return: list of the selected well offset
        """
        return [well.offset for well in self.Wells if well.selFlag]   

    def selected_wells(self):
        return [well for well in self.Wells if well.selFlag]

    def selectAll(self):
        for well in self.Wells:
            well.selFlag = True
        return self

    def selectOnly(self, sel_idx_list):
        self.clearSelection()
        self.select(sel_idx_list)
        return self

    def select(self, sel_idx_list):
        if isinstance(sel_idx_list, int):
            sel_idx_list = [sel_idx_list]
        for w in sel_idx_list:
            if not isinstance(w, Well):
                w = self.Wells[w]
            else:
                assert w.labware is self
            w.selFlag = True
        return self

    def newOffset(self, pos, offset):
        return self.offset(pos.row, pos.col) + offset

    def newPosition(self, pos, offset):
        return self.position(self.newOffset(pos, offset))

    def posAtParallelMove(self, step, n_tips):
        nR, nC = self.type.nRow, self.type.nCol
        assert step < nC * nR, "too many steps!!"
        SubPlateSize = n_tips * nC
        SubPlate = step // SubPlateSize
        tN_semiCol = step // n_tips
        parit = (SubPlate) % 2
        pos_semiCol = nC * parit + (tN_semiCol % nC) * (-1) ** parit + 1 - parit

        p = self.Position(row=SubPlate * n_tips + step % n_tips + 1, col=pos_semiCol)

        msg = "error in calculation of parallel row {:d}>{:d}".format(p.row, nR)
        assert 0 < p.row <= nR, msg
        msg = "error in calculation of parallel col {:d}>{:d}".format(p.col, nC)
        assert 0 < p.col <= nC, msg
        return p

    def parallelOrder(self, n_tips, original=None):
        original = original or self.selected()
        assert original
        if isinstance(original, int):
            assert 0 < original <= len(self.Wells)
            original = range(original)
        assert isinstance(original, (list, range))
        return [self.offset(self.posAtParallelMove(offset, n_tips)) for offset in original]

    def offsetAtParallelMove(self, step, n_tips):
        p = self.posAtParallelMove(step, n_tips)
        return self.offset(p.row, p.col)

    def moveParallel(self, pos, offset):  #
        return offset % self.type.nCol + 1, offset // self.type.nCol + 1

    def wellSelectionStr(self, wells : (int, [int], [Well] ) = None):
        """
        :return: See A.15.3, pag. A-122
        file:///C:/Prog/RobotEvo/FreedomEVOwareStandardV2.4SP1-2011.ExtendedDeviceSupportManual.pdf
        Many of the advanced worklist commands have a parameter called wellSelection.
        wellSelection is a string which specifies the wells (tips) which should be used for
        the command.
        Characters 1 and 2 of the string specify the number of wells in the x-direction in
        hexadecimal. Characters 3 and 4 of the the string specify the number of wells in
        the y-direction in hexadecimal. For example, 12 x 8 (96 wells) = 0C08.
        All following characters are used for the well selection, whereby each character
        specifies the well selection for a group of 7 adjacent wells using a specially
        adapted bitmap system. Only 7 bits are used per byte [RANGE 0-127 !!!] instead of 8 to avoid screen
        and printer font compatibility problems. Using the 7-bit system, 14 characters are
        needed to represent the well selection for 96 wells (plus characters 1 to 4, total of
        18 characters) and 55 characters are needed to represent the well selection for
        384 wells (total of 59 characters).
        In addition, since most ANSI characters below ANSI 32 are non-printable (nonhuman-
        readable), decimal 48 (ANSI value for “0”) is added to the value
        [RANGE 48-175 !!! 144 have undefined Unicode !!!]  of the
        bitmap to make it easier to read, send by eMail etc. The following shows some
        examples for character 5 of the well selection string for a 96-well microplate in
        landcape orientation.
        Character 5 is responsible for the first group of 7 wells

        this function stores 7 bit per character in the selection string
        the first 2 characters are the number of wells in x direction (columns) in hexadecimal.
        the characters 3 and 4 are the number of wells in y direction (rows) in hexadecimal.
        well are computed in the order back to front, left to right;
        https://docs.python.org/3.4/library/string.html#formatstrings
        """
        X = self.type.nCol
        Y = self.type.nRow
        sel = bytearray()  # sel=sel.encode('ascii')
        bitMask = 0
        null = 48  # ord('0')
        bit = 0

        pre_selected = True
        if wells is not None:
            if not isinstance(wells, list):
                wells = [wells]
        if wells is not None:
            pre_selected = False
            wells = [self.offset(w) for w in wells]
        for w in self.Wells:
            bit = w.offset % 7

            if pre_selected:
                if w.selFlag:
                    bitMask |= (1 << bit)
            elif w.offset in wells:
                bitMask |= (1 << bit)

            if bit == 6:
                sel.append(null + bitMask)
                bitMask = 0
        if bit != 6:
            sel.append(null + bitMask)
        from EvoScriPy.evo_mode import encoding
        return "{:02X}{:02X}".format(X, Y) + sel.decode(encoding)


class NoFreeWells (Exception):
    def __init__(self, labware: Labware, error: str):
        self.labware = labware
        Exception.__init__(self, "In " + str(labware) + error)


class DITIrackTypeSeries(Labware.Type.Series):

    def __init__(self, labware: Labware ):
        Labware.Type.Series.__init__(self, labware)
        self.last_preserved_tips = None              # a tip Well in a DiTi rack

    def find_new_tips(self, TIP_MASK) -> (bool, [Tip]):
        """

        :param TIP_MASK:
        :param lastPos:
        :return:
        """

        number_tips = count_tips(TIP_MASK)
        tips        = []
        continuous  = True
        first       = self.current
        rack        = first

        assert isinstance(first, DITIrack)

        while (True):

            fcontinuous, ftips = rack.find_new_tips(number_tips-len(tips))
            tips += ftips
            if not fcontinuous:
                continuous = False

            if number_tips == len(tips):
                    return continuous, tips

            continuous = False

            # we need to find in other rack
            rack, rotated = self.show_next(rack)
            assert rack is not self.current                                       # todo return incomplete ??

    def retire_new_tips(self, TIP_MASK):
        """
        A response to a get_tips: the tips have to be removed from the rack
        and only after that can appear mounted in the robot arm to pipette.
        The tips are removed at the "current" position, the position where
        begin the fresh tips, with is maintained internally by the robot and
        is unknown to the user
        """
        number_tips = count_tips(TIP_MASK)  # todo do we really need a correspondence mask - wells??
        return self._retire_new_tips(number_tips)

    def _retire_new_tips(self, number_tips):
        """
        Return removed tips.
        Low Level !!! To be called only by implementations of low level Instruction.actualize_robot_state
        as response to getDITI2
        """

        tips  = []
        first = self.current
        assert isinstance(first, DITIrack)
        rack  = first
        while (True):
            tips += rack.retire_new_tips(number_tips-len(tips))
            if number_tips == len(tips):
                    return tips

            # we need to find in other rack
            rack, rotated = self.set_next()
            if rack is first:
                logging.warning("Using DITI rack agains? Put new ?")
                rack = self.refill_next_rack()

    def refill_next_rack(self, worktable=None):    #  -> DITIrack

        # rack = self.next_rack(worktable)                                      # todo what worktable? another Place ?

        next_rack, rotated = self.set_next()
        logging.warning("USER PROMPT: ReFill Rack " + next_rack.label)       # todo ? USER PROMPT: Fill Rack
        assert isinstance(next_rack, DITIrack)
        assert self is not next_rack                                            # todo ???   rack empty ??
        next_rack.fill()                                                        # todo check for tips back !!!!!!
        return next_rack


class DITIrackType(Labware.Type):


    def __init__(self, name, nRow=8, nCol=12, max_vol=None, portrait=False):

        if portrait:
            nCol, nRow = nRow, nCol                  # todo revise !

        Labware.Type.__init__(self, name, nRow, nCol, max_vol)

        self.preserved_tips = {}        # order:well ??? sample order:tip well ??sample offset:tip well todo in series?
        # self.last_preserved_tips = None              # a tip Well in a DiTi rack

    def create_labware(self, loc, label):
        labw = DITIrack(self, loc, label)
        return labw

    def create_series(self, labware : Labware):
        # assert isinstance(labware.type, DITIrackType)
        return DITIrackTypeSeries(labware)


class DITIrack (Labware):
    """
    Objects of this class represent physical objects (with location) of
    some type Labware.DITIrackType
    """

    def __init__(self, type    : DITIrackType,
                       location: WorkTable.Location,
                       label   : str):
        """

        :param type:
        :param location:
        :param label:
        :param worktable:
        """
        assert isinstance(type, DITIrackType)

        Labware.__init__(self, type, label=label, location = location)
        self.pick_next      = 0
        self.pick_next_back = type.nRow * type.nCol - 1
        self.lastPos        = False

        self.fill()

    def set_DITI_counter(self, posInRack, lastPos = False):
        if lastPos:
            self.pick_next_back = self.offset(posInRack)
            self.lastPos        = True
        else:
            self.pick_next = self.offset(posInRack)
            self.lastPos   = False

        # type.last_preserved_tips = ?

    def fill(self, beg=1, end=None):                   # todo it belong to Robot ??

        if isinstance(beg, list):
                            assert end is None
        end = end if end else self.type.size()

        beg = self.offset(beg)
        end = self.offset(end)

        r = range(beg, end+1)
        for w in self.Wells:
            w.reagent = None
        for w in r:
            self.Wells[w].reagent = Tip(self.type)   # How we can actualize the "counters"? Using Instructions
            # self.Wells[w].labware = self    #   hummm ??

        self.pick_next      = beg
        self.pick_next_back = end

    def find_new_tips(self, number_tips)  -> (bool, [Tip]) :
        """
        Return existing tips. May be only partially.
        Just to know there are tips
        """

        tips        = []
        pos         = self.pick_next_back  if self.lastPos  else  self.pick_next
        continuous  = True

        #                  begin                   end                   direction
        r = self.Wells[self.pick_next : self.pick_next_back + 1 : -1 if self.lastPos else 1]

        for w in r:
            if number_tips == len(tips):
                break

            pos += -1 if self.lastPos else 1

            tip = w.reagent
            if isinstance(tip, Tip) and not isinstance(tip, usedTip):
                assert tip.type is self.type, "A tip of unexpected type encountered"    # todo really??
                tips.append(tip)
                logging.info("Pick tip " + str(pos + 1) + " from rack site " + str(self.location.site + 1)
                      + " named: "   + self.label
                      + " have "     + str(len(tips) )
                      + " but need " + str(number_tips))
            else:
                continuous = False

        return continuous, tips

    def retire_new_tips(self, number_tips)  -> [Tip]:
        """
        Return removed tips. May be only partially.
        Low Level !!! To be called only by implementations of low level Instruction.actualize_robot_state
        as part of series.retire_new_tips as response to getDITI2
        """

        tips  = []
        pos   = 0

        #                  begin                   end                   direction
        r = self.Wells[self.pick_next : self.pick_next_back + 1 : -1 if self.lastPos else 1]

        for w in r:
            if number_tips == len(tips):
                break

            if self.lastPos:
                pos = self.pick_next_back
                self.pick_next_back -= 1
            else:
                pos = self.pick_next
                self.pick_next      += 1

            tip = w.reagent
            if isinstance(tip, Tip) and not isinstance(tip, usedTip):
                assert tip.type is self.type, "A tip of unexpected type encountered"    # todo really??
                tips.append(tip)
                w.reagent    = None
                logging.info("Pick tip " + str(pos + 1) + " from rack site " + str(self.location.site + 1)
                      + " named: "   + self.label
                      + " have "     + str(len(tips) )
                      + " but need " + str(number_tips))

        return tips

    def set_back(self, TIP_MASK, tips):
        """ Low level. Part of the job have been already done: tips is a list of the tips in
        the robot arm, passed here just to prevent a call and a link back to the robot.
        And the rack self hat already the target tip-wells selected.

        :param TIP_MASK:
        :param labware_selection:
        :param tips:
        """
        n = count_tips(TIP_MASK)
        assert isinstance(self.type, DITIrackType)
        assert n == len(self.selected()), "Too much or too few wells selected to put tip back"

        for i, w in enumerate(self.selected_wells()):
            tp = tips[i]

            logging.info("Set back " + str(tp) + " in " + str(w) + " of " + self.label)
            assert w.reagent is not Tip, ("Another tip " + w.reagent.type.name + "is already in position "
                                          + str(self.position(i)) + " of " + self.label)
            assert isinstance(tp, usedTip)

            w.reagent = tp
            self.type.preserved_tips[tp.origin] = w
            self.series.last_preserved_tips = w

    def pick_up(self, TIP_MASK) -> [usedTip]:
        """ Low level. Part of the job have been already done: the rack self hat
        already the source tip-wells selected. We need to return these tips.

        :param TIP_MASK:
        """
        n = count_tips(TIP_MASK)
        assert n == len(self.selected()), "Too much or too few wells selected to pick up tips"

        tips = []
        for w in self.selected_wells():
            # todo really ? and what if we want to pick up unused tips?
            logging.info("Pick Up from " + str(w) + " on the DITI rack " + self.label)

            assert isinstance(w.reagent, usedTip), ("No tip " + w.reagent.type.name + " were found in position: "
                                                    + str(w) + " on the DITI rack " + self.label)

            tips += [w.reagent]
            w.reagent = None
            # self.type.preserved_tips[tp.origin.offset] = w # tp.origin.offset
        return tips


class DITIwasteType(Labware.Type):
    def __init__(self, name, capacity=5*96):
        Labware.Type.__init__(self, name, nRow=capacity)

    def create_labware(self, loc, label):
        labw = DITIwaste(self, loc, label)
        return labw


class DITIwaste(Labware):
    def __init__(self, type, location, label=None):
        assert isinstance(type, DITIwasteType)
        Labware.__init__(self, type, label, location)
        self.wasted = 0

    def waste(self, tips):
        for tp in tips:
            self.Wells[self.wasted].reagent = tp      # todo revise ?
            self.wasted += 1                          # todo make following assert a Warning or a UserPrompt
            assert self.wasted < self.type.size(), "Too much tips wasted. Empty yours DiTi waste."

            if isinstance(tp, usedTip):  # this tip is dropped and cannot be used any more
                react_well = tp.origin
                if react_well in tp.type.preserved_tips:
                    tip_well = tp.type.preserved_tips[react_well]
                    assert isinstance(tip_well, Well)
                    if tip_well.reagent is None:
                        tip_well.reagent = banned_well       # don't used this well again (is "contaminated")
                        del tp.type.preserved_tips[react_well]  # todo could be mounted in another position?
                    else:
                        assert tp is not tip_well.reagent


class CuvetteType(Labware.Type):

    def __init__(self,   name,
                         nRow,
                         max_vol,
                         nCol=1):
        Labware.Type.__init__(self, name, nRow=nRow, max_vol=max_vol, nCol=nCol)

    def create_labware(self, loc, label):
        labw = Cuvette(self, loc, label)
        return labw


class Cuvette(Labware):
    def __init__(self, type, location, label=None):
        assert isinstance(type, CuvetteType)
        self.vol = 0.0
        self.reagent = None
        self.actions = []
        Labware.__init__(self, type, label, location)

    def init_wells(self):
        self.Wells = [conectedWell(self, offset) for offset in range(self.type.size())]

    def autoselect(self, offset=0, maxTips=1, replys=1):
        """

        :param offset:
        :param maxTips:
        :param replys:
        :return:
        """
        nWells = self.type.size()
        assert nWells > offset, "Can not select to far"  # todo better msg
        maxTips = min(maxTips, nWells)
        self.selectOnly(range((nWells - maxTips) // 2, (nWells - maxTips) // 2 + maxTips))
        return maxTips


class Te_Mag (Labware.Type):
    pass


#  "predefining" common labwares types:

Trough_100ml    = CuvetteType("Trough 100ml",                8,     max_vol=  100000)
Trough_25ml_rec = CuvetteType("Trough 25ml Max. Recovery",   8,     max_vol=   25000)
Trough_300ml_MCA= CuvetteType("Trough 300ml MCA",       8, nCol=12, max_vol=  300000)  # \todo test it works OK

EppRack16_2mL   = Labware.Type("Tube Eppendorf 2mL 16 Pos",         16,     max_vol=    2000)
GreinRack16_2mL = Labware.Type("Tube Greinerconic 2mL 16 Pos",      16,     max_vol=    2000)
EppRack3x16R    = Labware.Type("Tube Eppendorf 3x 16 PosR",         16, 3,  max_vol=    1500)
EppRack6x4      = Labware.Type("24 Pos Eppi Tube Rack",              4, 6,  max_vol=    1500)
EppRack3x16     = Labware.Type("Tube Eppendorf 3x 16 Pos",          16, 3,  max_vol=    1500)
EppRack6x16     = Labware.Type("Tube Eppendorf 6x 16 Pos",          16, 6,  max_vol=    1500)  # defined in Evoware !!!
MatrixRack1m8x12= Labware.Type("96 Well Matrix Rack 1ml",            8,12,  max_vol=    1000)
                    # by duplicating and then editing the labware 'Tube Eppendorf 3x 16 Pos' and also the carrier
                    # to have 6 instead of 3 columns. It was needed to change the position X of the last well (96)
                    # It was done by change the grig 6 positions to the right and coping the X pos of the first well,
                    # then come back to the originaL GRID AND SET THE COPIED X FOR the last well. The new, duplicated
                    # carrier was set to X width 150 mm
EppCarr16sites  = Carrier.Type("Tube Eppendorf 16 Sites", widht_in_grids=1, n_sites=16)
Greiner2mLx1    = Labware.Type("Tube Greiner conic 2mL 1 Pos",      1, 1,   max_vol=    2000)
Epp2mLx1        = Labware.Type("Tube Eppendorf 2mL 1 Pos",          1, 1,   max_vol=    2000)
Eppx1           = Labware.Type("Tube Eppendorf 1 Pos",              1, 1,   max_vol=    1500)
TubeRack13mmx16 = Labware.Type("Tube 13*100mm 16 Pos",              16,     max_vol=   15000)   # 15 mL ?
EppRackx16      = Labware.Type("Tube Eppendorf 16 Pos",             16,     max_vol=    1500)

EppRack6x16_2mL = Labware.Type("Tube Eppendorf 2m 6x 16 Pos",      16, 6,  max_vol=     2000)# todo define in Evoware !!!


DiTi_1000ul     = DITIrackType("DiTi 1000ul",                       max_vol=     940)  # 940 ??
DiTi_1000ul_SBS = DITIrackType("DiTi 1000ul SBS LiHa",              max_vol=     940)  # 940 ??
DiTi_200ul_SBS  = DITIrackType("DiTi 200ul SBS LiHa",               max_vol=     200)  # 190 ??
DiTi_10ul_SBS   = DITIrackType("DiTi 10ul SBS LiHa",                max_vol=      10)  # 0 9,5 ??
DiTi_200ul_MCA96= DITIrackType("DiTi 200ul SBS MCA96",              max_vol=     200)  # 190 ?? \todo derived ?
DiTi_0200ul     = DITIrackType("DiTi 200 ul",                       max_vol=     190)  # ??
Fixed_Tip       = Labware.Type("fixed tips", 1, max_vol=1500)  # todo ??

Tip_1000maxVol  = DiTi_1000ul.max_vol
Tip_200maxVol   = 190                   # TODO revise

# Evo75_FLI
CleanerShallow  = CuvetteType("Wash Station Cleaner shallow"   , 8, max_vol=  100000)
WasteWash       = CuvetteType("Wash Station Waste",              8, max_vol=10000000)  # 10 L
CleanerDeep     = CuvetteType("Wash Station Cleaner deep",       8, max_vol=  100000)
DiTi_Waste_plate= DITIwasteType("DiTi Nested Waste MCA384")  # Tip Waste ?? Washstation 2Grid DiTi Waste ?? DiTi Nested Waste MCA384 ?? DiTi Waste

# Evo100_FLI
CleanerSWS      = CuvetteType("Washstation 2Grid Cleaner short", 8, max_vol=  100000)
WasteWS         = CuvetteType("Washstation 2Grid Waste",         8, max_vol=10000000)  # 10 L
CleanerLWS      = CuvetteType("Washstation 2Grid Cleaner long",  8, max_vol=  100000)
DiTi_Waste      = DITIwasteType("Washstation 2Grid DiTi Waste")
TeMag48         = Labware.Type("Tube Eppendorf 48 Pos",          8, 6,   max_vol=    1500)

# Evo200_FLI
# CleanerSWS      = CuvetteType("Washstation 2Grid Cleaner short", 8, max_vol=  100000)  # Cleaner1
# WasteWS         = CuvetteType("Washstation 2Grid Waste",         8, max_vol=10000000)  # Waste       10 L
# CleanerLWS      = CuvetteType("Washstation 2Grid Cleaner long",  8, max_vol=  100000)  # Cleaner2
# DiTi_Waste      = DITIwasteType("Washstation 2Grid DiTi Waste")                       # DiTi Waste
AntiCOntamination = CuvetteType("AntiCOntamination",                     8, max_vol=    00) # fake, to fix LiHa position
Eppendorfrack     = Labware.Type("Sampletubes Eppendorfrack",           16, max_vol=  1500) # = "Tube Eppendorf 16 Pos"
TubeRack15mL2x6   = Labware.Type("Tube Falcon 15ml 12 Pos",          2,  6, max_vol= 15000) # ?? Tube 16 mm 10 Pos
MagSeparatPlt8x9  = Labware.Type("96 Well Separation Plate",         8,  9, max_vol=    00) # Magnetic separation 8x9
Filterplate       = Labware.Type("FilterplateaufElutionplate flach", 8, 12, max_vol=  2000) # Te-VacS
MP96MachereyNagel = Labware.Type("96 Well Macherey-Nagel Plate",     8, 12, max_vol=  2000) # Te-VacS
MP96MNflach       = Labware.Type("96 Well 8er Macherey-Nagel flach", 8, 12, max_vol=  2000) # Te-VacS
# MP_3Pos              = Carrier.Type("MP 3Pos"                        , width=4, n_sites=3 , idx=12 )
# ContaminationFlyway  = Carrier.Type("AntiCOntaminationFlyway"        , width=1, n_sites=40, idx=107)
# EppCarr16po          = Carrier.Type("Tube Eppendorf 16 Pos"          , width=1, n_sites=16, idx=43 )
# Washs2GridTroughDiTi = Carrier.Type("Washstation 2Grid Trough DiTi"  , width=2, n_sites=8 , idx=104)


MP96well     = Labware.Type("96 Well Microplate"     , 8, 12, max_vol= 200)
MP96deepwell = Labware.Type("96 Well DeepWell square", 8, 12, max_vol=2000)    # todo define in Evoware !!!
PCR96well    = Labware.Type("96 Well PCR Plate"      , 8, 12, max_vol= 100)
BioRad96well = Labware.Type("96 Well BioRad"         , 8, 12, max_vol= 100)

Box9x9       = Labware.Type("Box 9x9"                , 9,  9, max_vol= 2000)
Box10x10     = Labware.Type("Box 10x10"              ,10, 10, max_vol= 2000)


def getLabware(labw_type, label, worktable=None):
    worktable = worktable or WorkTable.cur_worktable
    return worktable.get_labware(label, labw_type)
