# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
"""
`Reagent` - a fundamental concept
=================================

A `Reagent` is a fundamental concept in RobotEvo programming. It makes possible to define a protocol in a natural way,
matching what a normal laboratory's protocol indicates.
Defines a named homogeneous liquid solution, the wells it occupy, the initial amount needed to run the protocol
(auto calculated), and how much is needed per sample, if applicable. It is also used to define samples,
intermediate reactions and products. It makes possible a robust tracking of all actions and a logical error
detection, while significantly simplifying the  programming of non trivial protocols.

todo: implement units for volume, concentration, etc.

Main classes and functions:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Abstract information classes:
-----------------------------

 - :py:class:`MixComponent`: like an item in some table summarizing components of some Mix.
 - :py:class:`~PreMixComponent` like an item in some table summarizing components of some PreMix.
 - :py:class::Primer
 - :py:class::PrimerMixComponent
 - :py:class::PrimerMix
 - :py:class::PCRMasterMix
 - :py:class::PCReaction
 - :py:class::PCRexperiment
 - :py:class::
 - :py:class::
 - :py:class::

Robot classes:
--------------

 - :py:class::Reagent
 - :py:class::Mix
 - :py:class::Dilution
 - :py:class::PreMix
 - :py:class::PrimerReagent
 - :py:class::PrimerMixReagent
 - :py:class::PCRMasterMixReagent
 - :py:class::PCReactionReagent
 - :py:class::PCRexperimentRtic
 - :py:class::
 - :py:class::
 - :py:class::


"""

__author__ = 'qPCR4vir'


import logging
from pathlib import Path

import EvoScriPy.labware as lab

def_reagent_excess = 4
def_mix_excess = 8


class Reagent:
    """
    A Reagent is a fundamental concept in RobotEvo programming.
    It makes possible to define a protocol in a natural way, matching what a normal
    laboratory's protocol indicates. Defines a named homogeneous liquid solution,
    the wells it occupy, the initial amount needed to run the protocol (auto calculated),
    and how much is needed per sample, if applicable. It is also used to define samples,
    intermediate reactions and products. It makes possible a robust tracking
    of all actions and a logical error detection, while significantly simplifying
    the programming of non trivial protocols.
    """

    current_protocol = None                                               # to (auto)register a list of reagents
    use_minimal_number_of_aliquots = True

    def __init__(self,
                 name          : str,
                 labware       : (lab.Labware, str, [])    = None,
                 wells         : (int, [int], [lab.Well])  = None,
                 num_of_aliquots: int                      = None,
                 minimize_aliquots: bool                   = None,
                 def_liq_class : (str, (str, str))         = None,
                 volpersample  : float                     = 0.0,  # todo move to PreMixComponent
                 num_of_samples: int                       = None, # todo move to Exp? to prepare?
                 single_use    : float                     = None, # todo move to MixComponent
                 excess        : float                     = None, # todo move to MixComponent
                 initial_vol   : float                     = 0.0,
                 min_vol       : float                     = 0.0,
                 fill_limit_aliq : float                   = 100,
                 concentration : float                     = None  # todo implement use. Absolut vs. relative? Units?
                 ):
        """
        This is a named set of aliquots of an homogeneous solution.
        Put a reagent into labware wells, possible distributed into aliquots and set the amount to be used for each sample,
        if applicable.
        Each reagent is added to a list of reagents of the worktable were the labware is.
        The specified excess in % will be calculated/expected. A default excess of 4% will be assumed
        if None is indicated.
        A minimal needed volume will be calculated based on either the number of samples
        and the volume per sample to use or the volume per single use. This can be forced setting min_vol.
        A minimal number of replicas (wells, aliquots) will be calculated based on the minimal volume,
        taking into account the maximum allowed volume per well and the excess specified. Aliquots will be filled not more
        than the percent of the well volumen indicated by fill_limit_aliq.

        :param name:            Reagent name. Ex: "Buffer 1", "forward primer", "IC MS2"
        :param labware:         Labware or his label in the worktable; if None will be deduced from `wells`.
        :param volpersample:    how much is needed per sample, if applicable, in uL
        :param single_use;      Not a "per sample" multiple use? Set then here the volume for one single use
        :param wells:           or offset to begging to put replica. If None will try to assign consecutive wells in labware
        :param num_of_aliquots;        def min_num_of_replica(), number of replicas
        :param def_liq_class;     the name of the Liquid class, as it appears in your own EVOware database.
                                instructions.def_liquidClass if None
        :param excess;          in %
        :param initial_vol;     is set for each replica. If default (=None) is calculated als minimum.
        :param min_vol;         force a minimum volume to be expected or prepared.
        :param fill_limit_aliq;    maximo allowed volume in % of the wells capacity
        :param num_of_samples;  if None, the number of samples of the current protocol will be assumed
        :param minimize_aliquots;  use minimal number of aliquots? Defaults to `Reagent.use_minimal_number_of_aliquots`,
                                   This default value can be temporally change by setting that global.
        """
        logging.debug("Creating Reagent " + name)

        self.user_min_vol = min_vol
        self.need_vol = 0.0  #: calculated volume needed during the execution of the protocol
        if labware is None:
            if isinstance(wells, lab.Well):
                labware = wells.labware
            elif isinstance(wells, list) and isinstance(wells[0], lab.Well):
                labware = wells[0].labware
        self.labwares = labware if isinstance(labware, list) else [labware]
        for idx, lw in enumerate(self.labwares):
            if isinstance(lw, str):
                self.labwares[idx] = Reagent.current_protocol.worktable.get_labware(label=lw)
            else:
                assert isinstance(lw, lab.Labware), "No labware defined for Reagent " + str(self)
        self.labware = self.labwares[0]

        # add self to the list of reagents of the worktable were the labware is.
        worktable = None
        assert isinstance(self.labware.location.worktable,   lab.WorkTable)                                   # todo temporal
        if (    isinstance(self.labware,                     lab.Labware)
            and isinstance(self.labware.location,            lab.WorkTable.Location)
            and isinstance(self.labware.location.worktable,  lab.WorkTable)):

            worktable = self.labware.location.worktable
        else:
            if Reagent.current_protocol:
                worktable = Reagent.current_protocol.worktable                         # todo temporal

        assert name not in worktable.reagents, "The reagent " + name + " was already in the worktable"
        worktable.reagents[name] = self
        ex = def_reagent_excess if excess is None else excess

        self.fill_limit_aliq = 1.0 if fill_limit_aliq is None else fill_limit_aliq / 100.0
        self.excess = 1.0 + ex/100.0
        self.def_liq_class = def_liq_class
        self.name = name
        self.volpersample = volpersample
        self.components = []                                # todo reserved for future use ??
        if minimize_aliquots is not None:
            self.minimize_aliquots = minimize_aliquots
        else:
            self.minimize_aliquots = Reagent.use_minimal_number_of_aliquots
        if single_use:
            assert not volpersample, str(name) + \
                                     ": this is a single use-reagent. Please, don't set any volume per sample."
            if num_of_samples is None:
                num_of_samples = 1
            assert num_of_samples == 1, "this is a single use-reagent, don't set num_of_samples " + str(num_of_samples)

            self.volpersample = single_use
        else:
            if num_of_samples is None:
                num_of_samples = Reagent.current_protocol.num_of_samples or 0

        self.min_num_aliq = self.min_num_of_replica(num_of_samples=num_of_samples)

        # coordinate: min_num_aliq, wells, num_of_aliquots, initial_vol. todo fine-tune warnings.
        if num_of_aliquots is None:
            num_of_aliquots = self.min_num_aliq
        assert num_of_aliquots >= self.min_num_aliq, ("too few wells (" + str(len(wells)) + ") given for the minimum "
                                                      + "number of replica needed (" + str(self.min_num_aliq) + " )")

        if isinstance(wells, list):                         # use len(pos) to correct num_of_aliquots
            assert len(wells) >= self.min_num_aliq, ("too few wells (" + str(len(wells)) + ") given for the minimum "
                                                     + "number of replica needed (" + str(self.min_num_aliq) + " )")
            if num_of_aliquots < len(wells):
                logging.warning("WARNING !! putting more replica of " + name + " to fit the initial volume list provided")
                num_of_aliquots = len(wells)
            assert not num_of_aliquots > len(wells), ("too few wells (" + str(len(wells)) + ") given for the desired "
                                                      + "number of replicas (" + str(num_of_aliquots) + " )")
            if isinstance(initial_vol, list):
                assert num_of_aliquots == len(initial_vol)
            if num_of_aliquots > self.min_num_aliq:                              # todo revise !! for PreMix components
                logging.warning("WARNING !! You may be putting more wells replicas (" + str(len(wells)) + ") of " + name
                                + " that the minimum you need(" + str(self.min_num_aliq) + " )")

        if not isinstance(initial_vol, list):
            initial_vol = [initial_vol] * num_of_aliquots

        if num_of_aliquots < len(initial_vol):
            logging.warning("WARNING !! putting more replica of " + name + " to fit the initial volume list provided")
            num_of_aliquots = len(initial_vol)
            if num_of_aliquots > self.min_num_aliq:                                      # todo revise !! for PreMix components
                logging.warning("WARNING !! You may be putting more inital volumens values (" + str(num_of_aliquots) + ") of " + name
                                + " that the minimum number of replicas you need(" + str(self.min_num_aliq) + " )")

        try:
            self.Replicas   = self.labware.put(self, wells, self.min_num_aliq if self.minimize_aliquots else num_of_aliquots)
        except lab.NoFreeWells as er:
            logging.warning("No free wells: " + str(er))
            for lwre in self.labwares:
                if lwre is self.labware:
                    continue
                try:
                    self.Replicas = lwre.put(self, wells,
                                                     self.min_num_aliq if self.minimize_aliquots else num_of_aliquots)
                    self.labware = lwre
                    break
                except lab.NoFreeWells as er:
                    logging.warning("No free wells: " + str(er))
            else:
                er = lab.NoFreeWells(labware=self.labware, error=' to put ' + str(num_of_aliquots)
                                                                 + ' aliquots of reagent - ' + str(self))
                logging.warning(str(er))
                raise er

        self.pos        = self.Replicas[0].offset                                   # ??

        self.init_vol(NumSamples=num_of_samples, initial_vol=initial_vol)            # put the minimal initial volume
        self.include_in_check = True
        logging.debug("Created Reagent " + str(self))

    def min_num_of_replica(self, num_of_samples: int = None) -> int:
        """
        A minimal number of replicas (wells, aliquots) will be calculated based on the minimal volume,
        taking into account the maximum allowed volume per well and the excess specified.
        :param num_of_samples:
        :return:
        """
        return int(self.min_vol(num_of_samples) / (self.labware.type.max_vol * self.fill_limit_aliq)) + 1

    @staticmethod
    def set_reagent_list(protocol):
        Reagent.current_protocol = protocol                    # ??

    @staticmethod
    def StopReagentList():
        Reagent.current_protocol = None

    def __str__(self):
        return "{name:s}".format(name=self.name)

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.Replicas or '-') + ']'

    def min_vol(self, num_samples=None)->float:
        """
        A minimal volume will be calculated based on either the number of samples
        and the volume per sample to use (todo or the volume per single use.)???
        :param num_samples:
        :return:
        """

        if self.volpersample:
            num_samples = num_samples or Reagent.current_protocol.num_of_samples or 0
            self.need_vol = self.volpersample * num_samples * self.excess

        return self.need_vol

    def init_vol(self, NumSamples=None, initial_vol=None):
        if initial_vol is not None:
            assert isinstance(initial_vol, list)
            for w,v in zip(self.Replicas, initial_vol):
                w.vol = v
                assert w.labware.type.max_vol >= w.vol, 'Excess initial volume for '+ str(w)
        self.put_min_vol(NumSamples)

    def put_min_vol(self, NumSamples=None):          # todo create num_of_aliquots if needed !!!!
        """
        Force you to put an initial volume of reagent that can be used to distribute into samples,
        aspiring equal number of complete doses for each sample from each replica,
        exept the firsts replicas that can be used to aspirate one more dose for the last/rest of samples.
        That is: all replica have equal volumen (number) of doses or the firsts have one more dose
        :param NumSamples:
        :return:
        """
        if NumSamples is None:
            NumSamples = Reagent.current_protocol.num_of_samples
        if not NumSamples:
            return
        V_per_sample = self.volpersample * self.excess
        replicas=len(self.Replicas)
        for i, w in enumerate(self.Replicas):
            v = V_per_sample * (NumSamples + replicas - (i+1))//replicas
            if v > w.vol:  w.vol += (v-w.vol)
            assert w.labware.type.max_vol >= w.vol, 'Add one more replica for '+ w.reagent.name

    def autoselect(self, maxTips=1, offset=None, replicas = None):
        # todo revise !!!!!!!!! we know the wells = Replicas
        return self.labware.autoselect(offset or self.pos, maxTips, len(self.Replicas) if offset is None else 1)

    def select_all(self):
        return self.labware.selectOnly([w.offset for w in self.Replicas])


class NoReagentFound(Exception):
    def __init__(self, reagent_name: str, error: str):
        self.reagent_name = reagent_name
        Exception.__init__(self, "No reagent named " + str(reagent_name) + error)  # todo redaction


class Reaction(Reagent):
    """
    todo: make this a Mix, with diluent too ?
    """
    def __init__(self,
                 name,
                 labware,
                 components: [Reagent] = None,
                 track_sample=None, # just one more component?
                 pos=None,
                 num_of_aliquots=1,
                 def_liq_class=None,
                 excess=None,
                 initial_vol=0):

        Reagent.__init__(self,
                         name,
                         labware,
                         single_use=0,
                         wells=pos,
                         num_of_aliquots=num_of_aliquots,
                         def_liq_class=def_liq_class,
                         excess=excess,
                         initial_vol=initial_vol)
        self.track_sample = track_sample


class MixComponent:
    """
    Represent abstract information, like an item in some table summarizing components of some Mix.
    todo: introduce diluent? - final_conc == None ? final_conc == init_conc ?
    """

    def __init__(self,
                 id_: str,
                 name: str,
                 init_conc: float,
                 final_conc: float):
        """

        :param id_:
        :param name:
        :param init_conc:  todo Really??
        :param final_conc:
        """
        self.id = id_
        self.name = name
        self.init_conc = init_conc
        self.final_conc = final_conc

    def __str__(self):
        return self.name

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.id or '-') + ']'


class Mix(Reagent):
    """
    A Reagent composed of other Reagents, that the robot may prepare.
    """

    def __init__(self,
                 name          : str,  # todo introduce abstract info class Mix and rename this MixReagent?
                 labware       : (lab.Labware, str, [])    = None,
                 wells         : (int, [int], [lab.Well])  = None,
                 components    : [Reagent]                 = None,
                 num_of_aliquots: int                      = None,
                 minimize_aliquots: bool                   = None,
                 def_liq_class : (str, (str, str))         = None,
                 excess        : float                     = None,
                 initial_vol   : float                     = 0.0,
                 min_vol       : float                     = 0.0,
                 fill_limit_aliq : float                   = 100,
                 concentration : float                     = None
                 ):
        """

        :param name:
        :param labware:
        :param wells:
        :param components:
        :param num_of_aliquots:
        :param minimize_aliquots:
        :param def_liq_class:
        :param excess:
        :param initial_vol:
        :param min_vol:
        :param fill_limit_aliq:
        :param concentration:
        """
        ex = def_mix_excess if excess is None else excess
        vol = 0.0
        for reagent in components:
            vol += reagent.volpersample
            reagent.excess += ex/100.0      # todo revise! best to calculate at the moment of making?
            reagent.put_min_vol()

        if initial_vol is None:
            initial_vol = 0.0

        Reagent.__init__(self, name,
                         labware,
                         volpersample= vol,
                         wells= wells,
                         num_of_aliquots= num_of_aliquots,
                         def_liq_class = def_liq_class,
                         excess = ex,
                         initial_vol = initial_vol,
                         fill_limit_aliq= fill_limit_aliq)

        self.components = components  #: list of reagent components
        # self.init_vol()

    def __str__(self):  # todo ?
        return "{name:s}".format(name=self.name)

    def __repr__(self):  # todo ?
        return (self.name or '-') + '[' + str(self.Replicas or '-') + ']'

    def make(self, protocol, volume=None):      # todo deprecate?
        if self.Replicas[0].vol is None:   # ????
            self.put_min_vol(volume)
            assert False
        protocol.make_mix(self, volume)


class Dilution(Mix):
    pass


class PreMixComponent(MixComponent):
    """
    Represent abstract information, like an item in some table summarizing components of some PreMix.
    An special case of MixComponent, for which volume is calculated on the basis of "number of samples"
    and volume_per_sample
    """

    def __init__(self,
                 id_: str,
                 name: str,
                 init_conc: float,
                 final_conc: float,
                 volpersample: float = 0.0):
        """

        :param id_:
        :param name:
        :param init_conc:  todo Really??
        :param final_conc:
        """
        self.volpersample = volpersample
        self.id = id_
        self.name = name
        self.init_conc = init_conc
        self.final_conc = final_conc

        MixComponent.__init__(self,
                              id_= id_,
                              name= name,
                              init_conc= init_conc,
                              final_conc= final_conc)

    def __str__(self):
        return self.name

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.id or '-') + ']'


class PreMix(Mix):
    """
    A pre-Mix of otherwise independent reagents to be pippeted together for convenience,
    but that could be pippeted separately.
    todo: make this a special case of Mix, for which everything ? is calculated on the basis of "number of samples"
    todo: introduce diluent? - final_conc == None ? final_conc == init_conc ?
    """

    def __init__(self,
                 name,
                 labware: (lab.Labware, list),
                 components,
                 pos = None,
                 num_of_aliquots = None,
                 initial_vol = None,
                 def_liq_class = None,
                 excess = None,
                 fill_limit_aliq =None,
                 num_of_samples = None  # todo here?
                 ):
        """

        :param name:
        :param labware:
        :param components: list of reagent components
        :param pos:
        :param num_of_aliquots:
        :param initial_vol:
        :param def_liq_class:
        :param excess:
        :param fill_limit_aliq:
        :param num_of_samples:
        """
        ex = def_mix_excess if excess is None else excess
        vol = 0.0
        for reagent in components:
            vol += reagent.volpersample
            reagent.excess += ex/100.0      # todo revise! best to calculate at the moment of making?
            reagent.put_min_vol(num_of_samples)

        if initial_vol is None:
            initial_vol = 0.0

        Reagent.__init__(self, name,
                         labware,
                         volpersample= vol,
                         wells= pos,
                         num_of_aliquots= num_of_aliquots,
                         def_liq_class = def_liq_class,
                         excess = ex,
                         initial_vol = initial_vol,
                         fill_limit_aliq= fill_limit_aliq,
                         num_of_samples = num_of_samples)

        self.components = components  #: list of reagent components
        # self.init_vol()

    def init_vol(self, NumSamples=None, initial_vol=None):
        if self.components:
            self.volpersample = 0
            for reagent in self.components:
                self.volpersample += reagent.volpersample
            Reagent.init_vol(self, NumSamples=0, initial_vol=initial_vol)
        pass
        # put volume in num_of_aliquots only at the moment of making  !!
        # Reagent.init_vol(self, num_samples)
        # self.put_min_vol(num_samples)

    def make(self, protocol, NumSamples=None):      # todo deprecate?
        if self.Replicas[0].vol is None:   # ????
            self.put_min_vol(NumSamples)
            assert False
        protocol.make_pre_mix(self, NumSamples)

    def compVol(self,index, NumSamples=None):
        NumSamples = NumSamples or Reagent.current_protocol.num_of_samples
        return self.components[index].min_vol(NumSamples)


class Primer:
    """
    Represent abstract information, like an item in some table summarizing primer sequences, synthesis, etc.
    """

    ids = {}  #: connect each existing Primer ID with the corresponding Primer
    seqs = {}  #: connect each existing Primer sequence with the corresponding list of Primer
    names = {}  #: connect each existing Primer name with the corresponding list of Primer
    key_words = {}  #: connect each existing Primer key_word with the corresponding list of Primer
    ids_synt = {}  #: connect each existing Primer synthesis ID with the corresponding Primer

    next_internal_id = 0

    def __init__(self,
                 name: str,
                 seq: str,
                 proposed_stock_conc: float=100,  # uM
                 id_: str=None,
                 prepared: float=None,
                 mass: float=None,  # ug
                 moles: float=None,  # nmoles
                 molec_w: float=None,  # g/mol
                 mod_5p: str=None,
                 mod_3p: str=None,
                 id_synt: str=None,
                 kws: list=None,
                 diluent: str='TE 1x'):
        """

        :param name:
        :param seq:
        :param proposed_stock_conc:
        :param id_:
        :param prepared:
        :param mass:
        :param moles:
        :param molec_w:
        :param mod_5p:
        :param mod_3p:
        :param id_synt:
        :param kws:
        :param diluent:
        """
        self.diluent = diluent
        self.prepared = prepared
        self.proposed_stock_conc = proposed_stock_conc
        self.mass = mass
        self.moles = moles
        self.molec_w = molec_w
        self.mod_5p = mod_5p
        self.mod_3p = mod_3p
        self.id_synt = id_synt
        self.name = name
        self.seq = seq
        self.id = id_
        self._internal_id = Primer.next_internal_id
        Primer.next_internal_id += 1
        Primer.names.setdefault(name, []).append(self)

        if id_ and id_ in Primer.ids:
            wrn = 'Duplicate primer ID: ' + str(id_)
            logging.warning(wrn)
            # raise Warning(wrn)
        Primer.ids.setdefault(id_, []).append(self)

        if not id_synt:
            id_synt = 'FakeID-' + str(self._internal_id)
        if id_synt in Primer.ids_synt:
            err = 'Duplicate primer synthesis ID: ' + str(id_synt)
            logging.error(err)
            raise Exception(err)
        Primer.ids_synt[id_synt] = self

        Primer.seqs.setdefault(seq, []).append(self)
        if isinstance(kws, list):
            for kw in kws:
                Primer.key_words.setdefault(kw, []).append(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.id or '-') + ']'

    @staticmethod
    def load_excel_list(file_name: Path = None):
        col = {'conc': 0,
               'id': 2,
               'prepared': 4,
               'name': 5,
               'moles': 7,
               'mass': 8,
               'seq': 15,
               'mol_w': 11,
               'mod_5p': 19,
               'mod_3p': 20,
               'ido': 22,
               'virus': 25,
               'diluent': 1
               }
        logging.debug("opening excel")
        import openpyxl

        if not file_name:
            file_name = Path('C:\Prog\exp\PCR fli.xlsx')

        if not file_name:
            from tkinter import filedialog
            file_name = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsm"), ("All files", "*.*")),
                                                   defaultextension='fas',
                                                   title='Select HEV isolate subtyping deta')
            if not file_name:
                return

        logging.debug(file_name)

        wb = openpyxl.load_workbook(str(file_name))
        logging.debug(wb.sheetnames)

        ws = wb['PCR fli-oligos']
        first = True
        p = None
        for r in ws.iter_rows() :
            if first:
                diluent = r[col['diluent']].value
                first = False
            else:
                p=Primer(name=r[col['name']].value,
                         seq=r[col['seq']].value,
                         prepared=r[col['prepared']].value,
                         proposed_stock_conc=r[col['conc']].value,
                         id_=r[col['id']].value,
                         mass=r[col['mass']].value,
                         moles=r[col['moles']].value,
                         molec_w=r[col['mol_w']].value,
                         mod_5p=r[col['mod_5p']].value,
                         mod_3p=r[col['mod_3p']].value,
                         id_synt=r[col['ido']].value,
                         kws=[r[col['virus']].value],
                         diluent=diluent
                         )
        return p


class PrimerReagent (Reagent):
    """
    Manipulate a Primer Reagent on a robot.
    """
    excess = def_mix_excess

    def __init__(self,
                 primer: Primer,
                 primer_rack: (lab.Labware, list),
                 pos=None,
                 initial_vol=None,
                 PCR_conc=0.8,
                 stk_conc=100,
                 def_liq_class=None,
                 fill_limit_aliq=None,
                 excess=None):
        """
        Construct a robot-usable PrimerReagent from an abstract Primer.
        You can reuse "old" aliquots by passing primer.prepared volume > 0.
        If no  primer.prepared volume is passed, it will be prepared.

        :param primer:
        :param primer_rack:
        :param pos:
        :param initial_vol:
        :param PCR_conc:
        :param stk_conc:
        :param def_liq_class:
        :param fill_limit_aliq:
        :param excess:
        """

        self.stk_conc = stk_conc
        self.primer = primer

        Reagent.__init__(self,
                         name=primer.name,
                         labware=primer_rack or lab.stock,
                         wells=pos,
                         initial_vol=initial_vol or primer.prepared,
                         excess=excess or PrimerReagent.excess,
                         fill_limit_aliq=fill_limit_aliq,
                         def_liq_class=def_liq_class)

        # todo prepare unprepared Primers  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def __str__(self):
        return self.primer.name

    def __repr__(self):
        return (self.primer.name or '-') + '[' + str(self.primer.id or '-') + ']'


class PrimerMixComponent(MixComponent):
    """
    Represent abstract information, like an item in a table describing Primer Mixes for some PCRs.
    It can be a primer, another primer mix or the diluent
    """

    def __init__(self,
                 id_ = None,
                 name = None,
                 init_conc = None,
                 final_conc = None,
                 super_mix: bool = False):
        """

        :param id_:
        :param name:
        :param init_conc:
        :param final_conc:
        :param super_mix:
        """
        MixComponent.__init__(self, id_, name, init_conc, final_conc)
        self.super_mix = super_mix


class PrimerMix:
    """
    Represent abstract information, like a table describing Primer Mixes for some PCRs
    """

    ids = {}  #: connect each existing Primer mix ID with the corresponding PrimerMix
    names = {}  #: connect each existing Primer mix name with the corresponding list of PrimerMix
    key_words = {}  #: connect each existing Primer mix key_word with the corresponding list of PrimerMix
    super_mix = True

    next_internal_id = 0

    def __init__(self,
                 name,
                 id_ = None,
                 conc = 10.0,
                 prepared=None,
                 components = None,
                 ref_vol = None,
                 diluent = None,
                 kws = None,
                 super_mix = False):
        """

        :param name:
        :param id_:
        :param conc:
        :param prepared:
        :param components:
        :param ref_vol:
        :param diluent:
        :param kws:
        :param super_mix:
        """
        self.prepared = prepared
        self.super_mix = super_mix
        self.diluent = diluent
        self.name = name
        self.id = id_
        self.conc = conc
        self.components = components
        self.ref_vol = ref_vol

        self._internal_id = PrimerMix.next_internal_id
        PrimerMix.next_internal_id += 1

        PrimerMix.names.setdefault(name, []).append(self)
        PrimerMix.ids.setdefault(id_, []).append(self)
        if isinstance(kws, list):
            for kw in kws:
                PrimerMix.key_words.setdefault(kw, []).append(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.id or '-') + ']'

    @staticmethod
    def load_excel_list(file_name: Path = None):
        col = {'conc': 2,
               'id': 0,
               'name': 1,
               'vol': 2,
               'prepared': 4,
               'final': 6,
               'virus': 13,
               'super_mix': 1
               }
        logging.debug("opening excel")
        import openpyxl

        if not file_name:
            file_name = Path('C:\Prog\exp\PCR fli.xlsx')

        if not file_name:
            from tkinter import filedialog
            file_name = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsm"), ("All files", "*.*")),
                                                   defaultextension='fas',
                                                   title='Select HEV isolate subtyping deta')
            if not file_name:
                return

        logging.debug(file_name)

        wb = openpyxl.load_workbook(str(file_name))
        logging.debug(wb.sheetnames)

        ws = wb['Primer mix']  # todo argument

        # todo another dic
        no_l, header, name_l, vol_l, sep_l, table_h_l, primer_l, diluter_l = 0, 1, 2, 3, 4, 5, 6, 7

        line = no_l
        components = []

        diluent = 'TE 0,1 x'  # todo ????

        pmix = None
        id_ = None
        name = None
        conc = None
        ref_vol = None
        kws = None
        super_mix = False
        prepared = None

        for r in ws.iter_rows():

            if line == no_l:
                line += 1

            elif line == header:
                id_ = r[col['id']].value
                kws = [r[col['virus']].value]
                superm = r[col['super_mix']].value
                super_mix = ('SuperMix' == superm)
                line += 1

            elif line == name_l:
                # assert id == r[col['id']].value
                name = r[col['name']].value
                conc= r[col['conc']].value
                line += 1

            elif line == vol_l:
                ref_vol = r[col['vol']].value
                prepared = r[col['prepared']].value
                line += 1

            elif line == sep_l:
                line += 1

            elif line == table_h_l:
                line += 1

            elif line == primer_l:
                comp = PrimerMixComponent(id_ = r[col['id']].value,
                                          name = r[col['name']].value,
                                          init_conc = r[col['conc']].value,
                                          final_conc = r[col['final']].value,
                                          super_mix = ('"x"' == r[col['conc'] + 1].value))

                if comp.name == diluent:  # todo diluent always last?
                    components.append(comp)
                    pmix = PrimerMix(name=name,
                                     id_=id_,
                                     conc=conc,
                                     ref_vol=ref_vol,
                                     prepared=prepared,
                                     kws=kws,
                                     components=components,
                                     diluent=comp,
                                     super_mix=super_mix
                                     )
                    line = no_l
                    components = []

                    id_ = None
                    name = None
                    conc = None
                    ref_vol = None
                    kws = None
                    super_mix = False
                    prepared = None

                elif comp.final_conc and (comp.id or comp.name):
                    components += [comp]

        return pmix


class PrimerMixReagent(PreMix):
    """
    Manipulate a Primer-Mix Reagent on a robot.
    """

    excess = def_mix_excess

    def __init__(self,
                 primer_mix: PrimerMix,
                 primer_mix_rack: (lab.Labware, list),
                 pos=None,
                 num_of_aliquots=None,
                 initial_vol=None,
                 def_liq_class=None,
                 excess=None,
                 fill_limit_aliq=None,
                 primer_rack: (lab.Labware, list) = None):
        """
        Construct a robot-usable PrimerMixReagent from an abstract PrimerMix.
        You can reuse "old" aliquots by passing primer_mix.prepared volume > 0.
        If no  primer_mix.prepared volume is passed, or if it is not sufficient,
        a set of primer reagents will be created.


        :param primer_mix:
        :param primer_mix_rack:
        :param pos:
        :param num_of_aliquots:
        :param initial_vol:
        :param def_liq_class:
        :param excess:
        :param fill_limit_aliq:
        :param primer_rack:
        """
        self.primer_mix = primer_mix

        initial_vol = initial_vol or self.primer_mix.prepared

        components = []
        vol = 0
        lw = primer_mix_rack[0] if isinstance(primer_mix_rack, list) else primer_mix_rack
        reagents = lw.location.worktable.reagents
        diluent_vol = self.primer_mix.ref_vol             # todo ??

        for component in self.primer_mix.components:
            assert isinstance(component, PrimerMixComponent)
            if component is self.primer_mix.diluent:
                vol_per_mix = diluent_vol
            else:
                vol_per_mix = self.primer_mix.ref_vol * component.final_conc / float(component.init_conc)
                diluent_vol -= vol_per_mix
            if component.name in reagents:  # for example an existing primer
                component_r = reagents[component.name]
                assert isinstance(component_r, Reagent)
                # if not abs(component_r.volpersample - vol_per_reaction) < 0.05:
                #    assert False
                # component_r.put_min_vol()
            else:
                if component.name in PrimerMix.names:

                    for prmx in PrimerMix.names[component.name]:
                        assert isinstance(prmx, PrimerMix)
                        if component.id == prmx.id:
                            c_primer_mix = prmx
                            break
                    else:
                        raise NoReagentFound(component.name, " as primer mix with ID:" + str(component.id)
                                                             + ". Alternatives are: " + str(PrimerMix.names[component.name]))

                    component_r = PrimerMixReagent(c_primer_mix,
                                                   primer_mix_rack=primer_mix_rack,
                                                   primer_rack=primer_rack)
                elif component.name in Primer.names:

                    for pr in Primer.names[component.name]:
                        assert isinstance(pr, Primer)
                        if component.id == pr.id:
                            c_primer = pr
                            break
                    else:
                        raise NoReagentFound(component.name, " as primer with ID:" + str(component.id)
                                                             + ". Alternatives are: " + str(Primer.names[component.name]))

                    component_r = PrimerReagent(c_primer,
                                                primer_rack=primer_rack)

            components.append(component_r)

        PreMix.__init__(self,
                        primer_mix.name,
                        primer_mix_rack,
                        pos,
                        components,
                        num_of_aliquots=num_of_aliquots,
                        initial_vol=initial_vol,
                        excess=excess or PrimerMix.excess)


class ExpSheet:
    def __init__(self,
                 file_name: Path,
                 page,
                 cell_rows,
                 sample_line,
                 num_col=12,
                 num_row=8,
                 ):

        self.file_name = file_name
        self.page = page
        self.num_col = num_col
        self.num_row = num_row
        self.cell_rows = cell_rows
        self.sample_line = sample_line
        name = Path(file_name).stem.split('.')
        self.id = name[0]
        self.title = '.'.join(name[1:])


class PCRMasterMix:
    """
    Represent abstract information, like an item in some table summarizing PCR Master Mixes for some PCR experiment
    """

    ids = {}  #: connect each existing PCR master mix ID with the corresponding PCRMasterMix
    names = {}  #: connect each existing PCR master mix name with the corresponding PCRMasterMix
    next_internal_id = 0

    def __init__(self,
                 name,
                 id_=None,
                 reaction_vol=25,  #: in uL
                 sample_vol=5,  #: in  uL
                 components=None,
                 diluent=None,
                 title=None):
        """

        :param name:
        :param id_:
        :param reaction_vol:
        :param sample_vol:
        :param components:
        :param title:
        """
        self.diluent = diluent
        self.name = name
        self.id = id_
        self.reaction_vol = reaction_vol
        self.sample_vol = sample_vol
        self.title = title
        self.components = components
        self._internal_id = PCRMasterMix.next_internal_id
        PCRMasterMix.next_internal_id += 1
        assert name not in PCRMasterMix.names
        PCRMasterMix.names[name] = self
        assert id_ not in PCRMasterMix.ids
        PCRMasterMix.ids[id_] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.id or '-') + ']'

    @staticmethod
    def load_excel_list(exp_sheet: ExpSheet, ws=None):
        col = {'conc': 16,
               'id': 14,
               'name': 14,
               'vol': 16,
               'final': 18,
               'sample_v': 16,
               'title': 15,
               'comp_name': 15
               }

        if ws is None:
            logging.debug("opening excel file")
            import openpyxl

            if not exp_sheet.file_name:        # deprecate
                file_name = Path('C:\Prog\exp\PCR fli.xlsx')

            if not exp_sheet.file_name:       # deprecate
                from tkinter import filedialog       # deprecate
                file_name = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsm"), ("All files", "*.*")),
                                                       defaultextension='fas',
                                                       title='Select HEV isolate subtyping deta')
                if not file_name:
                    return

            logging.debug(exp_sheet.file_name)

            wb = openpyxl.load_workbook(str(exp_sheet.file_name))
            logging.debug(wb.sheetnames)

            ws = wb[exp_sheet.page or 'Druken']       # deprecate

        no_l, header, name_l, vol_l, sampl_l, table_h_l, comp_l, diluent_l = 0, 0, 0, 1, 2, 5, 6, 7
        diluent = 'H2O'   # ?
        line = no_l
        pmix = None
        id = None
        name = None
        vol_per_reaction = 25
        components = []
        sample_vol = 5  # uL
        title = None
        to_skeep = 1 + exp_sheet.num_row * exp_sheet.cell_rows
        skeeped = 0

        for r in ws.iter_rows():

            if skeeped < to_skeep:
                skeeped += 1
                continue

            if line <= name_l:
                name = r[col['name']].value
                if name:
                    title = r[col['title']].value
                    line += 1

            elif line == vol_l:
                id = r[col['id']].value
                vol_per_reaction = r[col['vol']].value
                line += 1

            elif line == sampl_l:
                sample_vol = r[col['sample_v']].value
                line += 1

            else:
                component = MixComponent(id_=r[col['id']].value,
                                         name=r[col['comp_name']].value,
                                         init_conc=r[col['conc']].value,
                                         final_conc=r[col['final']].value)
                if component.name == diluent:
                    components.append(component)
                    pmix = PCRMasterMix(name=name,
                                        id_=id,
                                        reaction_vol=vol_per_reaction,
                                        sample_vol=sample_vol,
                                        title=title,
                                        components=components,
                                        diluent=component
                                        )
                    line = no_l
                    id = None
                    name = None
                    vol_per_reaction = 25
                    components = []
                    sample_vol = 5  # uL
                    title = None

                elif component.final_conc and (component.id or component.name):
                        components.append(component)

        return pmix


class PCRMasterMixReagent(PreMix):
    """
    Manipulate a PCR Master-Mix Reagent on a robot.
    """

    excess = def_mix_excess

    def __init__(self,
                 pcr_mix: PCRMasterMix,
                 mmix_rack: (lab.Labware, list),
                 pos=None,
                 num_of_aliquots=None,
                 initial_vol=None,
                 def_liq_class=None,
                 excess=None,
                 fill_limit_aliq=None,
                 kit_rack: (lab.Labware, list) = None,
                 primer_mix_rack: (lab.Labware, list) = None,
                 primer_rack: (lab.Labware, list) = None):
        """
        Construct a robot-usable PCRMasterMixReagent from an abstract PCRMasterMix.
        It is always constructed - no reuse of old aliquots: contains instable components.

        :param primer_mix_rack:
        :param primer_rack:
        :param pos:
        :param num_of_aliquots:
        :param initial_vol:
        :param def_liq_class:
        :param fill_limit_aliq:
        :param pcr_mix:
        :param mmix_rack:
        :param kit_rack:
        :param excess:
        """
        self.pcr_mix = pcr_mix
        components = []
        vol = 0
        lw = mmix_rack[0] if isinstance(mmix_rack, list) else mmix_rack
        reagents = lw.location.worktable.reagents
        diluent_vol = pcr_mix.reaction_vol - pcr_mix.sample_vol
        # num_samples = len(exp.mixes[pcr_mix])
        for component in pcr_mix.components:
            assert isinstance(component, MixComponent)
            if component is pcr_mix.diluent:
                vol_per_reaction = diluent_vol
            else:
                vol_per_reaction = pcr_mix.reaction_vol * component.final_conc / float(component.init_conc)
                diluent_vol -= vol_per_reaction
            if component.name in reagents:
                component_r = reagents[component.name]
                assert isinstance(component_r, Reagent)
                # if not abs(component_r.volpersample - vol_per_reaction) < 0.05:
                #    assert False
                # component_r.put_min_vol()
            else:
                if component.name in PrimerMix.names:

                    for prmx in PrimerMix.names[component.name]:
                        assert isinstance(prmx, PrimerMix)
                        if component.id == prmx.id:
                            primer_mix = prmx
                            break
                    else:
                        raise NoReagentFound(component.name, " as primer mix with ID:" + str(component.id)
                                             + ". Alternatives are: " + str(PrimerMix.names[component.name]))

                    component_r = PrimerMixReagent(primer_mix,
                                                   primer_mix_rack=primer_mix_rack,
                                                   primer_rack=primer_rack)

                else:  # todo for now let consider this a kit component - but it could be a Primer  !!!!
                    component_r = Reagent(component.name,
                                          labware=kit_rack,
                                          volpersample=vol_per_reaction,
                                          num_of_samples=0)
            components.append(component_r)

        PreMix.__init__(self,
                        pcr_mix.name + "-PCRMMix",
                        mmix_rack,
                        components,
                        pos=pos,
                        num_of_aliquots=num_of_aliquots,
                        initial_vol=initial_vol,
                        def_liq_class=def_liq_class,
                        excess=excess or PCRMasterMixReagent.excess,
                        fill_limit_aliq=fill_limit_aliq)


class PCReaction:
    """
    Represent abstract information, like an item in some table summarizing reactions in a PCR experiment
    """

    empty = 0
    ntc = 1
    pos = 2
    std = 3
    unk = 4

    rol = {'':empty, None:empty, 'NTC':ntc, 'Pos':pos, 'Unk':unk, 'Std':std}

    def __init__(self,
                 rol,
                 sample=None,
                 targets=None,
                 mix: PCRMasterMix=None,
                 replica=None,
                 row=None,
                 col=None,
                 vol=None):
        self.col = col
        self.row = row
        self.rol = rol
        self.sample = sample
        self.targets = targets or []
        self.mix = mix
        if not mix:
            for target in self.targets:
                if target in PCRMasterMix.names:
                    self.mix = PCRMasterMix.names[target]
                    break
            else:
                assert not self.rol
        self.req_vol = vol or mix
        self.replica = replica

    @staticmethod
    def get_rol(rol):
        rol, replica = rol.split('-')  # todo improve to parse replicas
        return rol in PCReaction.rol, rol, replica

    def __str__(self):
        return self.sample

    def __repr__(self):
        return (self.sample or '-') + '[' + str(self.targets[0] or '-') + ']'


class PCReactionReagent(Reaction):
    vol = 25
    vol_sample = 5

    def __init__(self,
                 pcr_reaction: PCReaction,
                 plate: lab.Labware):
        """

        :param pcr_reaction:
        :param plates:
        """

        pos = plate.Position(pcr_reaction.row, pcr_reaction.col)
        Reaction.__init__(self,
                          name=pcr_reaction.sample + ".PCR" + str(pos),
                          labware=plate,
                          track_sample=pcr_reaction.sample,
                          pos=pos)
        self.pcr_reaction = pcr_reaction
        self.plate = plate


class PCRexperiment:
    """
    Represent abstract information, like an item in some table summarizing PCR experiments
    """

    def __init__(self,
                 id_ = None,
                 name = None,
                 ncol = 0,
                 nrow = 0):
        """
        A linear rack have just one roe and many columns

        :param id_:
        :param name:
        :param ncol:
        :param nrow:
        """
        self.id = id_
        self.name = name
        self.pcr_reactions = [[PCReaction(PCReaction.empty)]*ncol]*nrow  #: list of PCRReaction to create organized in rows with columns
        self.targets = {}  #: connect each target with a list of PCR reactions well
        self.mixes = {}  #: connect each PCR master mix with a list of well reactions
        self.samples = {}  #: connect each sample with a list of well reactions
        # self.vol = PCReaction.vol
        # self.vol_sample = PCReaction.vol_sample

    def add_reaction(self, pcr_reaction: PCReaction):
        self.pcr_reactions[pcr_reaction.row-1][pcr_reaction.col-1] = pcr_reaction
        self.samples.setdefault(pcr_reaction.sample, []).append(pcr_reaction)
        for target in pcr_reaction.targets:
            self.targets.setdefault(target, []).append(pcr_reaction)
            if target in PCRMasterMix.names:
                mmix = PCRMasterMix.names[target]
                if pcr_reaction.mix:
                    assert pcr_reaction.mix is mmix
                else:
                    pcr_reaction.mix = mmix
        self.mixes.setdefault(pcr_reaction.mix, []).append(pcr_reaction)
        pass

    def load_excel_list(self, exp_sheet: ExpSheet, load_PCRmix: bool = True):
        if self.id is None:
            self.id = exp_sheet.id
        if self.name is None:
            self.name = exp_sheet.title

        col = {'conc': 16,
               'id': 14,
               'name': 14,
               'vol': 16,
               'final': 18,
               'sample_v': 16,
               'title': 15,
               'comp_name': 15
               }
        logging.debug("opening excel")
        import openpyxl

        if not exp_sheet.file_name:
            exp_sheet.file_name = Path('C:\Prog\exp\PCR fli.xlsx')

        if not exp_sheet.file_name:
            from tkinter import filedialog
            exp_sheet.file_name = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsm"), ("All files", "*.*")),
                                                   defaultextension='fas',
                                                   title='Select HEV isolate subtyping deta')
            if not exp_sheet.file_name:
                return

        if load_PCRmix:
            PCRMasterMix(exp_sheet)

        logging.debug(exp_sheet.file_name)

        wb = openpyxl.load_workbook(str(exp_sheet.file_name))

        logging.debug(wb.sheetnames)

        ws = wb[exp_sheet.page or 'Druken']

        if load_PCRmix:
            PCRMasterMix.load_excel_list(exp_sheet, ws)

        ncol = exp_sheet.num_col
        row = 0
        cell_rows = exp_sheet.cell_rows
        sample_line = exp_sheet.sample_line
        line = 0
        reactions = None

        for r in ws.iter_rows():

            if line == 0:
                line += 1

            elif line == 1:
                reactions = [PCReaction(PCReaction.empty, row=row + 1, col=col + 1) for col in range(ncol)]
                for rx in reactions:
                    rx.rol = PCReaction.rol[r[rx.col].value]
                line += 1

            elif line < sample_line:
                for rx in reactions:
                    target = r[rx.col].value
                    if target:
                        assert rx.rol
                        rx.targets.append(target)
                line += 1
                continue

            elif line == sample_line:
                for rx in reactions:
                    sample = r[rx.col].value
                    if sample:
                        assert rx.rol
                        rx.sample = sample
                line += 1

            elif line <= cell_rows:
                # read cell line
                line += 1

            if line >= cell_rows:  # last cell line
                row += 1
                if len(self.pcr_reactions) < row:
                    self.pcr_reactions += [[None]*ncol]
                for rx in reactions:
                    self.add_reaction(rx)
                line = 1
                if row == exp_sheet.num_row:
                    break

        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return (self.name or '-') + '[' + str(self.id or '-') + ']'


class PCRexperimentRtic:
    """
    Organize a PCR setup on a robot.
    """

    def __init__(self,
                 pcr_exp: (PCRexperiment, list),
                 plates: (lab.Labware, list),
                 kit_rack: (lab.Labware, list),
                 mmix_rack: (lab.Labware, list) = None,
                 primer_mix_rack:  (lab.Labware, list) = None,
                 primer_rack: (lab.Labware, list) = None,
                 protocol=None):

        logging.debug("Creating a PCRexperimentRtic from " + repr(pcr_exp))
        self.pcr_exp = pcr_exp if isinstance(pcr_exp, list) else [pcr_exp]  #: abstract info
        self.plates = plates if isinstance(plates, list) else [plates]
        assert len(self.pcr_exp) <= len(self.plates)
        self.protocol = protocol
        self.mixes = {}  #: connect each PCRMasterMix in the experiment with the PCR wells into which will be pippeted

        for exp, plate in zip(self.pcr_exp, self.plates):  # iterate each PCR plate for which we have PCR mixes declared
            assert isinstance(exp, PCRexperiment)

            for pcr_mix, pcr_reactions in exp.mixes.items():  # visit each PCR mix with corresponding list of reactions
                if not pcr_mix:             # empty reaction wells are market with None mix.
                    continue
                assert isinstance(pcr_mix, PCRMasterMix)

                mix = PCRMasterMixReagent(pcr_mix=pcr_mix,
                                          mmix_rack=mmix_rack,
                                          primer_mix_rack=primer_mix_rack,
                                          kit_rack=kit_rack,
                                          primer_rack=primer_rack)  # todo: it could be reused from another plate !!???????

                sv = pcr_mix.sample_vol  # all reactions prepared with this mix have the same reaction and sample volume
                nw = len(pcr_reactions)
                react_wells = []
                for rx in pcr_reactions:
                    r = PCReactionReagent(rx, plate)
                    react_wells.extend(r.Replicas)
                    mix.need_vol += mix.volpersample              # ?? num_aliq
                self.mixes.setdefault(mix, []).extend(react_wells)                     # just samples?
                pass

        pass

    def pippete_mix(self):
        pass

    def pippete_samples(self):
        pass

    def vol (self, vol, vol_sample):
        self.vol = vol
        self.vol_sample = vol_sample

    def __str__(self):
        return "PCR Exp " + str(self.pcr_exp)

    def __repr__(self):
        return str(self)  # todo review


if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(10)

    primers = Primer.load_excel_list()
    primermixes = PrimerMix.load_excel_list()

    sheet0 = ExpSheet(file_name=Path('K:\AG RealtimePCR\Ariel\Exp 424. WESSV.MID.NewRNAbis-4. AVRvsSAfr.PanFlav-224.Ute.xlsx'),
                      page='Druken (2)',
                      cell_rows=3,
                      sample_line=3)

    sheet1 = ExpSheet(file_name=Path('C:\\Users\\Ariel\\Documents\\Exp\\PCR\\Exp 308. WNV.ZKU.10-1 10-10. WN-INNT-133, WN.Hoff, PanFlav.116.pltd.xlsx'),
                      page='Druken (3)',
                      cell_rows=6,
                      sample_line=6)
    # pcrmixes = PCRMasterMix.load_excel_list(sheet)
    exp = PCRexperiment().load_excel_list(sheet0)

    pass

