# 20W Ensemble-VR Score-Following

[![dartmouth-cs98](https://circleci.com/gh/dartmouth-cs98/20w-ensemble-vr-score-following.svg?style=shield)](https://app.circleci.com/pipelines/github/dartmouth-cs98/20w-ensemble-vr-score-following)

This repository contains the score-following component of **EnsembleVR**. Please check out the [github wiki](https://github.com/dartmouth-cs98/20w-ensemble-vr-score-following/wiki) for documentation regarding implementation/design choices.

**EnsembleVR** is a virtual reality application built using `Unity3D` for the Oculus Quest. Performing in front of a live audience on-stage is completely different from practicing alone in your own home. For music that requires accompaniment / other musicians, it's often difficult to play with the full accompaniment. For example, unless you're a famous musician, an average casual musician would never have the chance to solo with a live, full orchestra. You could play along to a recording, but that's not nearly as satisfying as playing with a live orchestra that adapts to you.

The goal of this project is to attempt to simulate, as realistically as possible, the experience of _performing_. This repo/wiki is primarily focused on answering the question:

**How do we generate musical accompaniment in real-time according to a player's musical interpretations?**

The system, at minimum, must be able to play accompaniment while adhering to the following.
1. Speed up and slow down according to a player's tempo
2. Allow for and handle intonation/pitch errors 
3. If a player skips or repeats a section, the system must be able to quickly determine the player's new location in the score and follow along.

## Setup

```
pip install -r requirements.txt
```

## Usage

Begin by moving into the scripts directory
```
cd src/scripts
```
Depending on your use case, use the following commands. These commands assume `python3`

**With Oculus headset and accompanying Unity3D app**

In one terminal window, begin the websockets server
```
python start_server.py <local_ip> <port>
```
In another terminal window, run
```
python follow_headset.py <local_ip> <port>
```

* `local_ip` - If you're on a mac, open up System Preferences > Network. Your local IP should be stated there.

* `port` - Pick a port that you want to use. _i.e. 4000_

**Without Oculus Headset**
```
python follow.py <piece> <tempo>
```

* `piece` - Name of the piece you want to follow

* `tempo` - Beats per minute. _i.e. 60_

## Tests

```
pytest test
```

## Credits

The techniques used in this project are my interpretation/implementation of the methods and ideas from the following papers.

* Nakamura, Tomohiko, et al. “Real-Time Audio-to-Score Alignment of Music Performances Containing Errors and Arbitrary Repeats and Skips.” IEEE/ACM Transactions on Audio, Speech, and Language Processing, vol. 24, no. 2, Feb. 2016, pp. 329–39. arXiv.org, doi:10.1109/TASLP.2015.2507862., https://arxiv.org/pdf/1512.07748.pdf
* Nakamura, Eita, et al. Autoregressive Hidden Semi-Markov Model of Symbolic Music Performance for Score Following. 2015. hal.inria.fr, https://hal.inria.fr/hal-01183820.
* Rao, Anyi, and Francis Lau. “Automatic Music Accompanist.” ArXiv:1803.09033 [Cs, Eess], Mar. 2018. arXiv.org, http://arxiv.org/abs/1803.09033.
