# Surrogate generation strategies in de-identification
Substitution strategies in de-identification combining security and utility.  A method that integrates differential privacy (more precisely d-privacy) with the Laplace mechanism and the exponential mechanism.

### Location data with health characteristics: Region Bourgogne Franche Comté (France)
#### Features
1. Overall population 
1. Cancer Incidence Rate
1. Stroke

Substitution strategies for entities: ***Date & Age*** and ***Location*** in a medical document

### Example of a sequence in a medical document: 
---

```
Mr. Durand born in Dijon, 40 years old, was
admitted to the hospital from 02/12/2020 to 02/26/2020
following a road accident in Dijon
```
## Strategies
* Date & Ages ⟹ ϵ-d.privacy + Laplace Mechanism 
* Location ⟹ ϵ-d.privacy + Exponential mechanism

Read paper for more details [here](https://)

To test this implementation, please go to the gist corresponding to the notebook of this repository - [here](https://gist.github.com/yakine8/d68a548b4abec5cacb5609511e837848). 
You will need the dataset (paper-data.pkl) and the files (date, location, dp of this repository) : Import them in your google colab space

