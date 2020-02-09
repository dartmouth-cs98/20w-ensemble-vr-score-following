# 20w-ensemble-vr-score-following
Score following algorithms component for ensemble

# Training Model
* While taking a deeper look into the details of the HSMM algorithm provided by Nakamura, et. al. (2015), we found that 
some parameters such as inner-outer-onset time were not easily measured using empirical tools. To simplify the model, we
are integrating parts of Rao's (2018) findings which does not use a specific measure for onset time probability.

# Citations
* Initial inspiration and model https://hal.inria.fr/hal-01183820/document
* Table 5 distribution for pitch probabilities https://arxiv.org/pdf/1404.2313.pdf
* For Cauchy distribution calculations https://arxiv.org/pdf/1404.2314.pdf

