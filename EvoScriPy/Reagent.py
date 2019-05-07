# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'qPCR4vir'


import EvoScriPy.Labware as Lab
# from Robot import current
from EvoScriPy.Instruction_Base import def_liquidClass

def_react_excess =  4
def_mix_excess   =  8
NumOfSamples     = None    # TODO revise this !!! Eliminate this GLOBAL ??????


class Reagent:

    Reagents = None           # todo move to normal member of class protocol ??

    def __init__(self,
                 name,
                 labware: Lab.Labware,           # ??
                 volpersample   = 0,
                 single_use     = None,
                 pos            = None,
                 replicas : int = None,
                 defLiqClass    = None,
                 excess         = None,
                 initial_vol    = None,
                 maxFull: float = None,
                 num_of_samples = None):
        """
        Put a reactive into labware wells, possible with replicates and set the amount to be used for each sample

        :param name: str; Reagent name. Ex: "Buffer 1", "forward primer", "IC MS2"
        :param labware: Labware;
        :param volpersample: float; in uL
        :param pos: [wells] or offset to begging to put replica. If None will try to assign consecutive wells
        :param replicas: int; def min_num_of_replica(), number of replicas
        :param defLiqClass: str;
        :param excess: float; in %
        :param initial_vol: float; is set for each replica. If default (=None) is calculated als minimum.
        """
        assert isinstance(labware, Lab.Labware)             # ??

        assert isinstance(labware.location.worktable, Lab.WorkTable) # todo temporal
        if (isinstance(labware, Lab.Labware) and
            isinstance(labware.location, Lab.WorkTable.Location) and
            isinstance(labware.location.worktable, Lab.WorkTable) ):
          labware.location.worktable.Reactives.append(self)
        else:
          if (Reagent.Reagents): Reagent.Reagents.Reactives.append(self) # todo temporal

        ex= def_react_excess if excess is None else excess

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
                            ": this is a single use-reactive. Please, don't set any volume per sample."
            assert len(self.Replicas) == 1, "Temporally use only one vial for " + str(name)
            self.volpersample = single_use
            self.init_vol(NumSamples=1)
        else:
            self.init_vol(num_of_samples)                           # put the minimal initial volumen ?

    def min_num_of_replica(self, NumSamples: int=None)->int:
        return int (self.minVol(NumSamples) / (self.labware.type.maxVol*self.maxFull)) +1

    @staticmethod
    def SetReactiveList(protocol):
        Reagent.Reagents = protocol                    # ??

    @staticmethod
    def StopReactiveList():
        Reagent.Reagents = None

    def __str__(self):
        return "{name:s}".format(name=self.name)

    def minVol(self, NumSamples=None)->float:
        NumSamples = NumSamples or NumOfSamples or 0
        return self.volpersample * NumSamples * self.excess

    def init_vol(self, NumSamples=None):
        self.put_min_vol(NumSamples)

    def put_min_vol(self, NumSamples=None):          # todo create replicas if needed !!!!
        """
        Force you to put an initial volume of reactive that can be used to spread into samples,
        aspiring equal number of complete doses for each sample from each replica,
        exept the firsts replicas that can be used to aspire one more dose for the last/rest of samples.
        That is: all replica have equal volumen (number) of doses or the firsts have one more dose
        :param NumSamples:
        :return:
        """
        NumSamples = NumSamples or NumOfSamples
        V_per_sample = self.volpersample * self.excess
        replicas=len(self.Replicas)
        for i, w in enumerate(self.Replicas):
            v = V_per_sample * (NumSamples + replicas - (i+1))//replicas
            if v > w.vol:  w.vol += (v-w.vol)
            assert w.labware.type.maxVol >= w.vol, 'Add one more replica for '+ w.reagent.name

    def autoselect(self, maxTips=1, offset=None, replicas = None):

        return self.labware.autoselect(offset or self.pos, maxTips, len(self.Replicas) if offset is None else 1)

class Primer (Reagent):
    IDs ={}
    SEQs={}
    Names={}
    KWs ={}
    Excess = def_mix_excess


    def __init__(self,
                 name,
                 seq,
                 ID         =None,
                 modif      = None,
                 stk_conc   =100,
                 PCR_conc   =0.8,
                 KW         =None,
                 labware    =None,
                 pos        =None,
                 initial_vol=None ):

        Reagent.__init__(self, name, labware or Lab.stock, pos=pos, initial_vol=initial_vol, excess=Primer.Excess)

        self.seq = seq
        self.ID  = ID
        Primer.Names [name]=self   # check duplicate
        Primer.IDs   [ID  ]=self   # check duplicate
        Primer.SEQs  [seq ]=self   # check duplicate  ??
        Primer.SEQs.setdefault(seq, []).append(self)
        for kw in KW:
            Primer.KWs.setdefault(kw,[]).append(self)



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
        for react in components:
            vol += react.volpersample
            react.excess +=  ex/100.0      # todo revise! best to calculate at the moment of making?
            react.put_min_vol(num_of_samples)

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
            for react in self.components:
                self.volpersample += react.volpersample
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
        NumSamples = NumSamples or NumOfSamples
        return self.components[index].minVol(NumSamples)


class PrimerMix(preMix):
    IDs={}
    Names={}
    KWs={}
    Excess = def_mix_excess


    def __init__(self, name, labware,  ID=None, conc=10.0, pos=None, components=None, replicas=1, initial_vol=None, excess=None):
        preMix.__init__(self, name, labware or Lab.stock, pos, components, replicas=replicas, initial_vol=initial_vol, excess=excess or PrimerMix.Excess)
        vol=0.0
        for react in components:
            vol += react.volpersample
            react.excess +=  ex/100.0      # todo revise! best to calculate at the moment of making?
            react.put_min_vol()

        if initial_vol is None: initial_vol = 0.0

        Reagent.__init__(self, name, labware, vol, pos=pos, replicas=replicas,
                         defLiqClass=defLiqClass, excess=ex, initial_vol=initial_vol)
        self.components = components
        #self.init_vol()


class PCRMasterMix(preMix):
    IDs={}
    Names={}
    KWs={}
    Excess = def_mix_excess


    def __init__(self,
                 name,
                 labware,
                 conc       =10.0,
                 pos        =None,
                 components =None,
                 replicas   =1,
                 initial_vol=None,
                 excess     =None):

        preMix.__init__(self, name, labware or Lab.stock, pos, components, replicas=replicas, initial_vol=initial_vol, excess=excess or PrimerMix.Excess)
        vol=0.0
        for react in components:
            vol += react.volpersample
            react.excess +=  ex/100.0      # todo revise! best to calculate at the moment of making?
            react.put_min_vol()

        if initial_vol is None: initial_vol = 0.0

        Reagent.__init__(self, name, labware, vol, pos=pos, replicas=replicas,
                         defLiqClass=defLiqClass, excess=ex, initial_vol=initial_vol)
        self.components = components
        #self.init_vol()

class PCRMix (preMix):
    pass

class PCReaction (Reaction):
    vol = 25
    vol_sample = 5
    pass

class PCRexperiment:
    def __init__(self, ID, name):
        self.PCReactions = []   # list of PCRReaction to create
        self.PCRmixes = []
        self.samples = []
        self.vol = PCReaction.vol
        self.vol_sample = PCReaction.vol_sample

    def addReactions(self, PCRmix: PCRMix, samples, labware: object) -> list:  # of PCRReaction
        pass
    def pippete_mix(self):
        pass
    def pippete_samples(self):
        pass
    def vol (self, vol, vol_sample):
        self.vol = vol
        self.vol_sample = vol_sample


