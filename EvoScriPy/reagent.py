# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'qPCR4vir'


import EvoScriPy.labware as Lab
# from Robot import current
from EvoScriPy.Instruction_Base import def_liquidClass

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
                 name           : str,
                 labware        : (Lab.Labware, str)        = None,
                 volpersample   : float                     = 0.0,
                 single_use     : float                     = None,
                 wells          : (int, [int], [Lab.Well])  = None,
                 replicas       : int                       = None,
                 defLiqClass    : (str,(str,str))           = None,
                 excess         : float                     = None,
                 initial_vol    : float                     = 0.0,
                 maxFull        : float                     = None,
                 num_of_samples : int                       = None,
                 minimize_aliquots : bool                   = None):
        """
        This is a named set of aliquots of an homogeneous solution.
        Put a reagent into labware wells, possible with replicates and set the amount to be used for each sample,
        if applicable.
        This reagent is automatically added to the list of reagents of the worktable were the labware is.
        The specified excess in % will be calculated/expected. A default excess of 4% will be assumed
        if not explicitly indicated.
        A minimal volume will be calculated based on either the number of samples
        and the volume per sample to use or the volume per single use.
        A minimal number of replicas (wells, aliquots) will be calculated based on the minimal volume,
        taking into account the maximum allowed volume per well and the excess specified.

        :param name:            Reagent name. Ex: "Buffer 1", "forward primer", "IC MS2"
        :param labware:         Labware or his label in the worktable; if None will be deduced from `wells`.
        :param volpersample:    how much is needed per sample, if applicable, in uL
        :param single_use;      Not a "per sample" multiple use? Set then here the volume for one single use
        :param wells:           or offset to begging to put replica. If None will try to assign consecutive wells
        :param replicas;        def min_num_of_replica(), number of replicas
        :param defLiqClass;     the name of the Liquid class, as it appears in your own EVOware database.
                                instr.def_liquidClass if None
        :param excess;          in %
        :param initial_vol;     is set for each replica. If default (=None) is calculated als minimum.
        :param maxFull;         maximo allowed volume in % of the wells capacity
        :param num_of_samples;  if None, the number of samples of the current protocol will be assumed
        :param minimize_aliquots;  use minimal number of aliquots? Defaults to `Reagent.use_minimal_number_of_aliquots`,
                                   This default value can be temporally change by setting that global.
        """
        if labware is None:
            if isinstance(wells, Lab.Well):
                labware = wells.labware
            elif isinstance(wells, list) and isinstance(wells[0], Lab.Well):
                labware = wells[0].labware
        if isinstance(labware, str):
            labware = Reagent.current_protocol.worktable.get_labware(label=labware)
        assert isinstance(labware, Lab.Labware), "No labware defined for Reagent " + name

        # add self to the list of reagents of the worktable were the labware is.
        assert isinstance(labware.location.worktable, Lab.WorkTable)                                   # todo temporal
        if (isinstance(labware,                     Lab.Labware) and
            isinstance(labware.location,            Lab.WorkTable.Location) and
            isinstance(labware.location.worktable,  Lab.WorkTable) ):
          labware.location.worktable.reagents.append(self)
        else:
          if (Reagent.current_protocol):
              Reagent.current_protocol.worktable.reagents.append(self)                                 # todo temporal

        ex= def_reagent_excess if excess is None else excess

        self.labware    = labware
        self.maxFull    = 1.0 if maxFull is None else maxFull/100.0
        self.excess     = 1.0 + ex/100.0
        self.defLiqClass = defLiqClass or def_liquidClass
        self.name       = name
        self.volpersample = volpersample
        self.components = []                                                            # todo reserved for future use
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

        self.minNumRep = self.min_num_of_replica(NumSamples=num_of_samples)

        # coordinate: minNumRep, wells, replicas, initial_vol. todo fine-tune warnings.
        if replicas is None:
            replicas = self.minNumRep
        assert replicas >= self.minNumRep, ("too few wells (" + str(len(wells)) + ") given for the minimum "
                                                + "number of replica needed (" + str(self.minNumRep) + " )" )

        if isinstance(wells, list):                         # use len(pos) to correct replicas
            assert len(wells) >= self.minNumRep, ("too few wells (" + str(len(wells)) + ") given for the minimum "
                                                + "number of replica needed (" + str(self.minNumRep) + " )" )
            if replicas < len(wells):
                print("WARNING !! putting more replica of " + name + " to fit the initial volume list provided")
                replicas = len(wells)
            assert not replicas > len(wells), ("too few wells (" + str(len(wells)) + ") given for the desired "
                                                + "number of replicas (" + str(replicas) + " )" )
            if isinstance(initial_vol, list):
                assert replicas == len(initial_vol)
            if replicas > self.minNumRep:                                    # todo revise !! for preMix components
                print("WARNING !! You may be putting more wells replicas (" + str(len(wells)) + ") of " + name
                      + " that the minimum you need("  + str(self.minNumRep) + " )")

        if not isinstance(initial_vol, list):
            initial_vol = [initial_vol]*replicas

        if replicas < len(initial_vol):
            print("WARNING !! putting more replica of " + name + " to fit the initial volume list provided")
            replicas = len(initial_vol)
            if replicas > self.minNumRep:                                      # todo revise !! for preMix components
                print("WARNING !! You may be putting more inital volumens values (" + str(replicas) + ") of " + name
                      + " that the minimum number of replicas you need("  + str(self.minNumRep) + " )")

        self.Replicas   = labware.put(self, wells, self.minNumRep if self.minimize_aliquots else replicas)
        self.pos        = self.Replicas[0].offset                                   # ??

        self.init_vol(NumSamples=num_of_samples, initial_vol=initial_vol)            # put the minimal initial volume

    def min_num_of_replica(self, NumSamples: int=None)->int:
        """
        A minimal number of replicas (wells, aliquots) will be calculated based on the minimal volume,
        taking into account the maximum allowed volume per well and the excess specified.
        :param NumSamples:
        :return:
        """
        return int (self.minVol(NumSamples) / (self.labware.type.maxVol*self.maxFull)) +1

    @staticmethod
    def set_reagent_list(protocol):
        Reagent.current_protocol = protocol                    # ??

    @staticmethod
    def StopReagentList():
        Reagent.current_protocol = None

    def __str__(self):
        return "{name:s}".format(name=self.name)

    def minVol(self, NumSamples=None)->float:
        """
        A minimal volume will be calculated based on either the number of samples
        and the volume per sample to use (todo or the volume per single use.)???
        :param NumSamples:
        :return:
        """
        NumSamples = NumSamples or Reagent.current_protocol.num_of_samples or 0
        return self.volpersample * NumSamples * self.excess

    def init_vol(self, NumSamples=None, initial_vol=None):
        if initial_vol is not None:
            assert isinstance(initial_vol, list)
            for w,v in zip(self.Replicas, initial_vol):
                w.vol = v
                assert w.labware.type.maxVol >= w.vol, 'Excess initial volume for '+ str(w)
        self.put_min_vol(NumSamples)

    def put_min_vol(self, NumSamples=None):          # todo create replicas if needed !!!!
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
            assert w.labware.type.maxVol >= w.vol, 'Add one more replica for '+ w.reagent.name

    def autoselect(self, maxTips=1, offset=None, replicas = None):
        # todo revise !!!!!!!!! we know the wells = Replicas
        return self.labware.autoselect(offset or self.pos, maxTips, len(self.Replicas) if offset is None else 1)

    def select_all(self):
        return self.labware.selectOnly([w.offset for w in self.Replicas])


class Reaction(Reagent):
    def __init__(self, name, track_sample, labware,
                 pos=None, replicas=None, defLiqClass=None, excess=None, initial_vol=None):
        Reagent.__init__(self, name, labware, single_use=0,
                         wells=pos, replicas=replicas, defLiqClass=defLiqClass, excess=excess, initial_vol=initial_vol)
        self.track_sample = track_sample


class preMix(Reagent):

    def __init__(self,
                 name,
                 labware,
                 components,
                 pos        =None,
                 replicas   =None,
                 initial_vol=None,
                 defLiqClass=None,
                 excess     =None,
                 maxFull    =None,
                 num_of_samples = None                  ):

        ex= def_mix_excess if excess is None else excess
        vol=0.0
        for reagent in components:
            vol += reagent.volpersample
            reagent.excess +=  ex/100.0      # todo revise! best to calculate at the moment of making?
            reagent.put_min_vol(num_of_samples)

        if initial_vol is None: initial_vol = 0.0

        Reagent.__init__(self, name,
                         labware,
                         vol,
                         wells= pos,
                         replicas      = replicas,
                         defLiqClass   = defLiqClass,
                         excess        = ex,
                         initial_vol   = initial_vol,
                         maxFull       = maxFull,
                         num_of_samples = num_of_samples)

        self.components = components
        #self.init_vol()

    def init_vol(self, NumSamples=None, initial_vol=None):
        if self.components:
            self.volpersample = 0
            for reagent in self.components:
                self.volpersample += reagent.volpersample
            Reagent.init_vol(self, NumSamples=0, initial_vol=initial_vol)
        pass
        # put volume in replicas only at the moment of making  !!
        # Reagent.init_vol(self, NumSamples)
        # self.put_min_vol(NumSamples)


    def make(self, NumSamples=None):      # todo deprecate?
        if self.Replicas[0].vol is None:   # ????
            self.put_min_vol(NumSamples)
            assert False
        from EvoScriPy.protocol_steps import makePreMix
        makePreMix(self, NumSamples)

    def compVol(self,index, NumSamples=None):
        NumSamples = NumSamples or Reagent.current_protocol.num_of_samples
        return self.components[index].minVol(NumSamples)
