# Pie : Prototyping Inference Engine #

Pie is an [inference engine](https://en.wikipedia.org/wiki/Inference_engine) library that allows to easily builds software prototypes. The goal is to allow to build quickly any software prototype which needs an inference engine. 
This library will support existential rules (which are [Datalog](https://en.wikipedia.org/wiki/Datalog) rules with existentially quantified variables in the conclusion), [forward chaining](https://en.wikipedia.org/wiki/Forward_chaining), [backward chaining](https://en.wikipedia.org/wiki/Backward_chaining) and heterogeneous sources of data.

** Warning : this library is still in its infancy and big modifications of its interfaces could still be done. **

# Progression #

+ *API*: 80% done
+ *Dlgp Parser*: 75% done
+ *Homomorphism*: 0%
+ *Backward chaining*: 0%
+ *Forward chaining*: 0%

# Packages #
## API ##

The API comprises the essential classes of the library : terms, atoms, atom sets, fact bases, ontologies, queries and so on.

## Parser ##

There is, for now, one parser : the dlgp parser, which supports the [dlgp 2.1 format](https://graphik-team.github.io/graal/doc/dlgp).