# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'qPCR4vir'


import EvoScriPy.Labware as Lab
# from Robot import current
from EvoScriPy.Instruction_Base import def_liquidClass

def_reagent_excess =  4
def_mix_excess   =  8


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

    current_protocol = None           # to register a list of reagents todo  ??

    def __init__(self,
                 name           : str,
                 labware        : Lab.Labware,
                 volpersample   : float         = 0,
                 single_use     : float         = None,
                 pos            : [Lab.Well]    = None,
                 replicas       : int           = None,
                 defLiqClass    : str           = None,
                 excess         : float         = None,
                 initial_vol    : float         = None,
                 maxFull        : float         = None,
                 num_of_samples = None):
        """
        Put a reagent into labware wells, possible with replicates and set the amount to be used for each sample.
        This reagent is automatically added to the list of reagents of the worktable were the labware is.
        The specified excess in % will be calculated/expected. A default excess of 4% will be assumed
        if not explicitly indicated.

        :param name:            Reagent name. Ex: "Buffer 1", "forward primer", "IC MS2"
        :param labware:         Labware;
        :param volpersample:    in uL
        :param single_use;      Not a "per sample" multiple use? Set then here the volume for one single use
        :param pos:             or offset to begging to put replica. If None will try to assign consecutive wells
        :param replicas;        def min_num_of_replica(), number of replicas
        :param defLiqClass;
        :param excess;          in %
        :param initial_vol;     is set for each replica. If default (=None) is calculated als minimum.
        """
        assert isinstance(labware, Lab.Labware)             # ??
                                                # add self to the list of reagents of the worktable were the labware is.
        assert isinstance(labware.location.worktable, Lab.WorkTable)                                    # todo temporal
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
        self.components = []
        self.minNumRep  = self.min_num_of_replica (num_of_samples)
        if isinstance(initial_vol, list):
            if replicas is None:
                replicas = len(initial_vol)
            elif replicas < len(initial_vol):
                print("WARNING !! putting more replica of " + name + " to fit the initial volume list provided")
                replicas = len(initial_vol)
            else:
                print("WARNING !! The provided initial volume list of "+ name + " will be filled only to first replicas")

        self.Replicas   = labware.put(self, pos, replicas)                            # list of the wells used
        self.pos        = self.Replicas[0].offset                                     # ??

        if isinstance(initial_vol, (int, float)):
            for w in  self.Replicas:
                 w.vol += initial_vol   # ?? add initial_vol to each replica
        elif isinstance(initial_vol, list):
            for w,v in zip(self.Replicas, ):
                w.vol += v

        if single_use:                                 # todo revise !!!
            assert not volpersample, str(name) + \
                            ": this is a single use-reagent. Please, don't set any volume per sample."
            assert len(self.Replicas) == 1, "Temporally use only one vial for " + str(name)
            self.volpersample = single_use
            self.init_vol(NumSamples=1)
        else:
            self.init_vol(num_of_samples)                           # put the minimal initial volumen ?

    def min_num_of_replica(self, NumSamples: int=None)->int:
        return int (self.minVol(NumSamples) / (self.labware.type.maxVol*self.maxFull)) +1

    @staticmethod
    def SetReagentList(protocol):
        Reagent.current_protocol = protocol                    # ??

    @staticmethod
    def StopReagentList():
        Reagent.current_protocol = None

    def __str__(self):
        return "{name:s}".format(name=self.name)

    def minVol(self, NumSamples=None)->float:
        NumSamples = NumSamples or Reagent.current_protocol.NumOfSamples or 0
        return self.volpersample * NumSamples * self.excess

    def init_vol(self, NumSamples=None):
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
        NumSamples = NumSamples or Reagent.current_protocol.NumOfSamples
        V_per_sample = self.volpersample * self.excess
        replicas=len(self.Replicas)
        for i, w in enumerate(self.Replicas):
            v = V_per_sample * (NumSamples + replicas - (i+1))//replicas
            if v > w.vol:  w.vol += (v-w.vol)
            assert w.labware.type.maxVol >= w.vol, 'Add one more replica for '+ w.reagent.name

    def autoselect(self, maxTips=1, offset=None, replicas = None):

        return self.labware.autoselect(offset or self.pos, maxTips, len(self.Replicas) if offset is None else 1)

    def select_all(self):
        return self.labware.selectOnly([w.offset for w in self.Replicas])


class Reaction(Reagent):
    def __init__(self, name, track_sample, labware,
                 pos=None, replicas=None, defLiqClass=None, excess=None, initial_vol=None):
        Reagent.__init__(self, name, labware, single_use=0,
                         pos=pos, replicas=replicas, defLiqClass=defLiqClass, excess=excess, initial_vol=initial_vol)
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
                         pos           = pos,
                         replicas      = replicas,
                         defLiqClass   = defLiqClass,
                         excess        = ex,
                         initial_vol   = initial_vol,
                         maxFull       = maxFull,
                         num_of_samples = num_of_samples)

        self.components = components
        #self.init_vol()

    def init_vol(self, NumSamples=None):
        if self.components:
            self.volpersample = 0
            for reagent in self.components:
                self.volpersample += reagent.volpersample
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
        NumSamples = NumSamples or Reagent.current_protocol.NumOfSamples
        return self.components[index].minVol(NumSamples)
