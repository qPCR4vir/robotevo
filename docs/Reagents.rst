`Reagent` - a fundamental concept
=================================

A `Reagent` is a fundamental concept in RobotEvo programming. It makes possible to define a protocol in a natural way, matching what a normal laboratory's protocol indicates.
Defines a named homogeneous liquid solution, the wells it occupy, the initial amount needed to run the protocol (auto calculated), and how much is needed per sample, if applicable. It is also used to define samples, intermediate reactions and products. It makes possible a robust tracking of all actions and a logical error detection, while significantly simplifying the  programming of non trivial protocols.



.. automodule:: reagents
   :members:
   :undoc-members:
   :show-inheritance:


## Reagents
 - Reagent
 - preMix
------------------------

### Reagent Constructor
         Reagent(self,
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
                                Itr.def_liquidClass if None
        :param excess;          in %
        :param initial_vol;     is set for each replica. If default (=None) is calculated als minimum.
        :param maxFull;         maximo allowed volume in % of the wells capacity
        :param num_of_samples;  if None, the number of samples of the current protocol will be assumed
        :param minimize_aliquots;  use minimal number of aliquots? Defaults to `Reagent.use_minimal_number_of_aliquots`,
                                   This default value can be temporally change by setting that global.


