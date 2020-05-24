# 20W Ensemble-VR Score-Following

This repository contains the score-following component of EnsembleVR. Please check out the github wiki for documentation regarding implementation/design choices.

EnsembleVR is a virtual reality application built using Unity3D for the Oculus Quest. One issue that most, if not all, musicians face is the fact that performing in front of a live audience on-stage is a completely different experience compared to practicing alone in ones own room. Additionally, for musicians whose performances often include accompaniment and or involve other musicians, it's often difficult or sometimes even impossible to have the opportunity to play a piece as it was intended -- with the full accompaniment. For example, many classical concertos involve a complete orchestra, but for the average casual musician, one might never have the chance to solo alongside a professional orchestra. Of course, one could simply play a recording of the accompaniment part and play along to that, but this is no where near as satisfying as playing alongside a live orchestra which speeds up, slows down, and follows your expressive interpretations/nuances.

The goal of this project is to attempt to simulate, as realistically as possible, the experience of _performing_. This repo/wiki is primarily focused on answering the question:

**How do we generate musical accompaniment in real-time according to a player's musical interpretations?**

The system, at minimum, must be able to play accompaniment while adhering to the following.
1. Speed up and slow down according to a player's tempo
2. Handle intonation/pitch errors 
3. If a player skips or repeats a section, the system must be able to quickly determine the player's new location in the score.

## Setup

```
pip install -r requirements.txt
```

## Usage

With Oculus headset and accompanying Unity3D app
```
python3 src/scripts/follow_headset.py
```

Without Oculus Headset
```
python3 src/scripts/follow.py
```

## Tests

Will write soon :/

## Credits

The techniques used in this project are largely a reimplementation of the methods discussed in the following papers.

* Nakamura, Tomohiko, et al. “Real-Time Audio-to-Score Alignment of Music Performances Containing Errors and Arbitrary Repeats and Skips.” IEEE/ACM Transactions on Audio, Speech, and Language Processing, vol. 24, no. 2, Feb. 2016, pp. 329–39. arXiv.org, doi:10.1109/TASLP.2015.2507862., https://arxiv.org/pdf/1512.07748.pdf
* Rao, Anyi, and Francis Lau. “Automatic Music Accompanist.” ArXiv:1803.09033 [Cs, Eess], Mar. 2018. arXiv.org, http://arxiv.org/abs/1803.09033.
* Nakamura, Eita, et al. Autoregressive Hidden Semi-Markov Model of Symbolic Music Performance for Score Following. 2015. hal.inria.fr, https://hal.inria.fr/hal-01183820.
