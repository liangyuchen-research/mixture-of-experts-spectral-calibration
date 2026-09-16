# Missing shared runtime

The version-6 notebooks import the original `spice_moe.py` from this directory. That file was not present in the supplied research archive and was not found in the additional local searches performed during preparation.

Do not install an unrelated package with a similar name. Recover the matching research module before attempting model execution. It is expected to provide architecture, normalization constants, loss definitions, stochastic plan sampling, training loops, checkpoint handling, and evaluation utilities used by the notebooks.

No placeholder implementation is provided because reconstructing those functions from call sites would create a different model. The repository intentionally reports the missing dependency clearly.
