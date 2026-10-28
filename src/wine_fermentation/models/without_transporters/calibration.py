from ...shared.optimization import fit
MODEL='without_transporters'
def calibrate(root,batches):return fit(root,MODEL,batches)
