#coding: utf-8
"""
tests for logger.py prior to coding

I'll fix docstring formatting, I promise.
I'll split this as soon as I fugure out how to do it.

We are testing the global Logger level, but this does not harm the
possibility of adding a log handler to a logger, with a specific log level.
However, most progress_* functions do bypass the traditional logging mechanism.

Test internals
==============
>>> from .. import core
>>> core.reset_newline()
>>> core.LAST_OUT == core.TEXT  # must be True on first import or after reset_newline
True

Creation of loggers
===================
>>> from .. import get_logger, PROGRESS
... # PROGRESS is a custom level (DEBUG + 5)
>>> from logging import DEBUG, INFO, WARNING
>>> verbose_logger = get_logger("ver",
... verbosity_offset=-10)
>>> verbose_logger.getEffectiveLevel()
5
>>> standard_logger = get_logger("std")
>>> PROGRESS
15
>>> standard_logger.getEffectiveLevel()
15
>>> laconic_logger = get_logger("lac",
... verbosity_offset=+10)

drop in replacement for print: msg
========================================

Always print if verbosity not specified
-------------------------------------
>>> verbose_logger.msg("Message must be displayed")
[ver] Message must be displayed
>>> standard_logger.msg("Message must be displayed")
[std] Message must be displayed
>>> laconic_logger.msg("Message must be displayed")
[lac] Message must be displayed

Print according to verbosity
-------------------------------------
- verbosity=False => DEBUG
- verbosity=True => always print
- verbosity=int => use int as verb level
Maybe this makes the case of “verbosity in (0, 1)” counter intuitive?

False
>>> verbose_logger.msg("Message must be displayed", verbosity=False)
[ver] Message must be displayed
>>> standard_logger.msg("Message must'nt be displayed", verbosity=False)
>>> laconic_logger.msg("Message must'nt be displayed", verbosity=False)

True
>>> verbose_logger.msg("Message must be displayed", verbosity=True)
[ver] Message must be displayed
>>> standard_logger.msg("Message must be displayed", verbosity=True)
[std] Message must be displayed
>>> laconic_logger.msg("Message must be displayed", verbosity=True)
[lac] Message must be displayed

0 (same for 1)
>>> verbose_logger.msg("Message mustn' be displayed", verbosity=0)
>>> standard_logger.msg("Message must'nt be displayed", verbosity=0)
>>> laconic_logger.msg("Message must'nt be displayed", verbosity=0)

DEBUG (10)
>>> verbose_logger.msg("Message must be displayed", verbosity=DEBUG)
[ver] Message must be displayed
>>> standard_logger.msg("Message must'nt be displayed", verbosity=DEBUG)
>>> laconic_logger.msg("Message must'nt be displayed", verbosity=DEBUG)

INFO (20)
>>> verbose_logger.msg("Message must be displayed", verbosity=INFO)
[ver] Message must be displayed
>>> standard_logger.msg("Message must be displayed", verbosity=INFO)
[std] Message must be displayed
>>> laconic_logger.msg("Message must'nt be displayed", verbosity=INFO)

WARN (30)
>>> verbose_logger.msg("Message must be displayed", verbosity=WARNING)
[ver] Message must be displayed
>>> standard_logger.msg("Message must be displayed", verbosity=WARNING)
[std] Message must be displayed
>>> laconic_logger.msg("Message must be displayed", verbosity=WARNING)
[lac] Message must be displayed

Play with verbosity offset
--------------------------
For absolute verbosity, use setLevel (see below).
>>> laconic_logger.msg("Message must'nt be displayed", verbosity=False)
>>> laconic_logger.set_offset(-10) # relative to general level which is INFO
>>> laconic_logger.msg("Message must be displayed", verbosity=False)
[lac] Message must be displayed
>>> laconic_logger.add_to_offset(20)
... #add_to_offset will get us back to the initial +10 value
>>> laconic_logger.msg("Message must'nt be displayed", verbosity=False)

traditional logging functions still work
========================================
>>> verbose_logger.debug("Message must be displayed")
[ver] Message must be displayed
>>> standard_logger.debug("Message mustn't be displayed")
>>> laconic_logger.debug("Message mustn't be displayed")

>>> verbose_logger.info("Message must be displayed")
[ver] Message must be displayed
>>> standard_logger.info("Message must be displayed")
[std] Message must be displayed
>>> laconic_logger.info("Message mustn't be displayed")

>>> verbose_logger.warning("Message must be displayed")
[ver] Message must be displayed
>>> standard_logger.warning("Message must be displayed")
[std] Message must be displayed
>>> laconic_logger.warning("Message must be displayed")
[lac] Message must be displayed

Play with verbosity (absolute)
------------------------------
>>> laconic_logger.setLevel(DEBUG)
>>> laconic_logger.debug("Message must be displayed")
[lac] Message must be displayed
>>> laconic_logger.setLevel(PROGRESS)
>>> laconic_logger.setLevel(WARNING)


progress
========

Initialization
>>> for logger in (verbose_logger, standard_logger, laconic_logger):
...    logger.progress_every(1000)
>>> for logger in (verbose_logger, standard_logger, laconic_logger):
...    logger.dot_every(10)

dot: Same semantic as msg
----------------------------------------

no verbosity: always output
>>> verbose_logger.dot() # doctest: +NORMALIZE_WHITESPACE
.
>>> standard_logger.dot() # doctest: +NORMALIZE_WHITESPACE
.
>>> laconic_logger.dot() # doctest: +NORMALIZE_WHITESPACE
.

verbosity=False -> DEBUG
>>> verbose_logger.dot(verbosity=False)
.
>>> standard_logger.dot(verbosity=False)
>>> laconic_logger.dot(verbosity=False)

verbosity=True -> always print
>>> verbose_logger.dot(verbosity=True)
.
>>> standard_logger.dot(verbosity=True)
.
>>> laconic_logger.dot(verbosity=True)
.

verbosity=PROGRESS for instance
>>> verbose_logger.dot(verbosity=PROGRESS)
.
>>> standard_logger.dot(verbosity=PROGRESS)
.
>>> laconic_logger.dot(verbosity=PROGRESS)

progress_step
-------------
>>> progress_logger = get_logger("progress")
>>> progress_logger.setLevel(PROGRESS)
>>> progress_logger.set_dot_char('x')

Testing dots alone
~~~~~~~~~~~~~~~~~~
>>> for count in range(10):
...     progress_logger.progress_step()
xxxxxxxxxx

>>> progress_logger.progress_reset()
>>> progress_logger.dot_every(10)

>>> for count in range(9):
...     progress_logger.progress_step()
>>> progress_logger.progress_step()
x

>>> for count in range(90):
...     progress_logger.progress_step()
xxxxxxxxx

>>> progress_logger.info('eat newline after xxxxxxxx')
<BLANKLINE>
[progress] eat newline after xxxxxxxx

Testing progress alone
~~~~~~~~~~~~~~~~~~~~~~~
>>> progress_logger.dot_every(0)
>>> for count in range(90):
...     progress_logger.progress_step()

>>> progress_logger.progress_reset()
>>> progress_logger.progress_every(1)
>>> for count in range(3):
...     progress_logger.progress_step()
[progress] Iteration 1 done
[progress] Iteration 2 done
[progress] Iteration 3 done

>>> progress_logger.progress_reset()
>>> progress_logger.progress_every(1000)
>>> for count in range(2000):
...     progress_logger.progress_step()
[progress] Iteration 1000 done
[progress] Iteration 2000 done

Testing progress AND dots
~~~~~~~~~~~~~~~~~~~~~~~~~
>>> progress_logger.progress_reset()
>>> progress_logger.dot_every(1)
>>> progress_logger.progress_every(1)
>>> progress_logger.progress_step()
x
[progress] Iteration 1 done

>>> progress_logger.progress_reset()
>>> for count in range(4):
...     progress_logger.progress_step()
x
[progress] Iteration 1 done
x
[progress] Iteration 2 done
x
[progress] Iteration 3 done
x
[progress] Iteration 4 done

>>> progress_logger.progress_reset()
>>> progress_logger.set_offset(+0)
>>> progress_logger.dot_every(100)
>>> progress_logger.progress_every(1000)
>>> for count in range(2000):
...     progress_logger.progress_step()
xxxxxxxxxx
[progress] Iteration 1000 done
xxxxxxxxxx
[progress] Iteration 2000 done

#Same, with a higher print offset
>>> progress_logger.progress_reset()
>>> progress_logger.set_offset(+10)
>>> for count in range(2000):
...     progress_logger.progress_step()
>>> progress_logger.progress_complete()
[progress] Successfully completed 2000 iterations
>>> standard_logger.percent_print_every(10)
... # every 10 percent, requires a target
>>> standard_logger.percent_target(1000) # the scale. rename function?
>>> standard_logger.dot_every(0)
>>> standard_logger.progress_every(0)
>>> for count in range(2000):
...     standard_logger.progress_step()
[std] 0%
[std] 10%
[std] 20%
[std] 30%
[std] 40%
[std] 50%
[std] 60%
[std] 70%
[std] 80%
[std] 90%
[std] 100%
[std] 110%
[std] 120%
[std] 130%
[std] 140%
[std] 150%
[std] 160%
[std] 170%
[std] 180%
[std] 190%
[std] 200%


"""
