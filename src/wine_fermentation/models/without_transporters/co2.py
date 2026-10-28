"""Model-specific entry point; shared transfer, model-specific chemical production."""
from ...shared.gas import simulate as _simulate
MODEL='without_transporters'
def simulate(batch,parameters,core,gas_parameters,volume):
    return _simulate(MODEL,batch,parameters,core,gas_parameters,volume)
