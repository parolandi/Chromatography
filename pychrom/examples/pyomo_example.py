from pychrom.core.chromatograpy_model import GRModel
from pychrom.core.section import Section
from pychrom.core.unit_operation import Inlet, Column, Outlet
from pychrom.core.binding_model import SMABinding
from pychrom.modeling.pyomo_modeler import PyomoModeler
import matplotlib.pyplot as plt

comps = ['salt',
         'lysozyme',
         'cytochrome',
         'ribonuclease']

GRM = GRModel(components=comps)

# create sections
GRM.load = Section(components=comps)
for cname in comps:
    GRM.load.set_a0(cname, 1.0)
GRM.load.set_a0('salt', 50.0)
GRM.load.start_time_sec = 0.0
"""
GRM.wash = Section(components=comps)
GRM.wash.set_a0('salt', 50.0)
GRM.wash.start_time_sec = 10.0

GRM.elute = Section(components=comps)
GRM.elute.set_a0('salt', 100.0)
GRM.elute.set_a1('salt', 0.2)
GRM.elute.start_time_sec = 90.0
"""
# create inlet
GRM.inlet = Inlet(components=comps)
GRM.inlet.add_section('load')
#GRM.inlet.add_section('wash')
#GRM.inlet.add_section('elute')

# create binding
GRM.salt = 'salt'
GRM.binding = SMABinding(data="sma.yml")
GRM.binding.is_kinetic = True

# create column
GRM.column = Column(data="column.yml")

# create outlet
GRM.outlet = Outlet(components=comps)

# connect units
GRM.connect_unit_operations('inlet', 'column')
GRM.connect_unit_operations('column', 'outlet')
for c, nu in enumerate(range(1, 4)):

    # ajusta nus
    for name in GRM.list_components():
        GRM.column.binding_model.set_nu(name, nu)

    # create a modeler
    modeler = PyomoModeler(GRM)
    tspan = [0.0, 500, 1500.0]
    q_scale = {'salt': 1200.0}
    c_scale = {'salt': 50.0}
    modeler.build_ideal_model(tspan,
                              q_scale=q_scale,
                              c_scale=c_scale)

    print("done building")
    modeler.discretize_space_ideal_model()
    print("done discretizing space")
    modeler.discretize_time_ideal_model()
    print("done discretizing time")
    if c == 0:
        modeler.initialize_variables_ideal_model()
    else:
        modeler.initialize_variables_ideal_model(results)
    results = modeler.run_sim(solver_opts={'halt_on_ampl_error':'yes'})

    if c == 2:
        for cname in results.components:
            to_plot = results.C.sel(component=cname)
            to_plot.plot()
            plt.show()

