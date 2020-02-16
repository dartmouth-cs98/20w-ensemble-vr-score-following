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
* We have decided to implement a hybrid of the Nakamura and Rao models. The pitch probability calculations are derived 
from Nakamura's design while onset timing considerations are implemented using Rao's methodology. This yields a simpler
version of the HSMM described in Nakamura et al., one that does not consider ornamental and repeating events such as 
trills. 
* We are prioritizing pitch detection implementation before continuing work on score-following. If our final product 
cannot detect polyphonic audio in real-time, there might as well not be a score-following element since not everyone 
owns a MIDI instrument. We look to X. Li (2018) for guidance in developing a reliable neural network approach to this 
problem. We will be using an approacch involving convolutional NN using audio spectrograms as input. This follows from 
work done by Carl Thomé.

# Citations
* Initial inspiration and model: https://hal.inria.fr/hal-01183820/document
* Table 5 distribution for pitch probabilities: https://arxiv.org/pdf/1404.2313.pdf
* For Cauchy distribution calculations: https://arxiv.org/pdf/1404.2314.pdf
* Alternative HMM approach with four-factor calculation: https://arxiv.org/pdf/1803.09033.pdf
* Reinforcement learning approach: https://transactions.ismir.net/articles/10.5334/tismir.31/
* Multipitch Estimation Model: https://link.springer.com/article/10.1186/s13636-018-0132-x
