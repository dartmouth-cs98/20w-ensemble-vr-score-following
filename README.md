# 20w-ensemble-vr-score-following
Score following algorithms component for ensemble

# Training Model
* While taking a deeper look into the details of the HSMM algorithm provided by Nakamura, et. al. (2015), we found that 
some parameters such as inner-outer-onset time were not easily measured using empirical tools. To simplify the model, we
may integrate parts of Rao's (2018) findings which does not use a specific measure for onset time probability. The model 
described instead uses a forward HMM model to train on a given data set and a decoding algorithm to follow a real-time 
performance. This involves calculations of four normal/ghost state pair probabilities, each derived recursively. This 
may be significantly different from the HSMM proposed by Nakamura et al. Another consideration would be to deviate from 
HMM approach and implement a reinforcement learning model for score following. Henkel et al. provide a strong base of 
code we may adapt to purposes of automatic accompaniment. Having observed a demo of the work provided by Henkel et al.,
we may pivot to their implementation as the HSMM and HMM approaches have proven overly abstract.

# Citations
* Initial inspiration and model: https://hal.inria.fr/hal-01183820/document
* Table 5 distribution for pitch probabilities: https://arxiv.org/pdf/1404.2313.pdf
* For Cauchy distribution calculations: https://arxiv.org/pdf/1404.2314.pdf
* Alternative HMM approach with four-factor calculation: https://arxiv.org/pdf/1803.09033.pdf
* Reinforcement learning approach: https://transactions.ismir.net/articles/10.5334/tismir.31/
