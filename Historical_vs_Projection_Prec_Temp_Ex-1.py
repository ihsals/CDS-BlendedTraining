# CDS Toolbox program to calculate historical and projected means (using RCP 8.5)
#    for visualization of difference between historical and projected data.
#    Historical time window: 1960-01 .. 1979-12 (preselected by indexes in cube.index_select)
#    Projection time window: 2030-01 .. 2049-12 (preselected by indexes in cube.index_select)
#    Contact: Alexander Los (los@ihs.nl) 


import cdstoolbox as ct

def retrieve_cmip5(model, variable, experiment, period):
    data = ct.catalogue.retrieve(
        'projections-cmip5-monthly-single-levels',
        {
            'ensemble_member':'r1i1p1',
            'format':'zip',
            'variable':variable,
            'model':model,
            'experiment':experiment,
            'period':period
        }
    )
    return data

layout = {
    'output_align': 'bottom'
}

models = {
    'ipsl_cm5a_lr':'IPSL-CM5A-LR (IPSL, France)',
    'ipsl_cm5a_mr':'IPSL-CM5A-MR (IPSL, France)',
    'ipsl_cm5b_lr':'IPSL-CM5B-LR (IPSL, France)',
    'mpi_esm_lr':'MPI-ESM-LR (MPI, Germany)',
    'mpi_esm_mr':'MPI-ESM-MR (MPI, Germany)',
    'noresm1_m':'NorESM1-M (NCC, Norway)'
    }

variables = {'mean_precipitation_flux':'Mean Precipitation Flux',
             '2m_temperature':'Near Surface Temperature'
            }

@ct.application(title='Difference between RCP8.5 and Historical expressed as percentage of Historical values.', layout=layout)

@ct.input.dropdown('model', label='Model', values=[{'label':l, 'value':v} for v, l in models.items()])

@ct.input.dropdown('variable', label='Variable', values=[{'label':l, 'value':v} for v, l in variables.items()])

@ct.output.figure()
@ct.output.dataarray()

def application(model, variable):
    plot_scale = 100 if variable == 'mean_precipitation_flux' else 1000
    select_8_5 = [288, 288 + 240]  # index: start and end of subset (in months)
    select_hist = [1320, 1320 + 240]  # index: start and end of subset (in months)
    period_8_5 = '200601-230012' if model == 'ipsl_cm5a_lr' else '200601-210012'
    period_hist = '185001-200512'

    model_8_5 = retrieve_cmip5(model, variable, 'rcp_8_5', period_8_5)
    model_8_5_selection = ct.cube.index_select(model_8_5, time=select_8_5)
    model_8_5_mean = ct.cube.average(model_8_5_selection, 'time')

    model_historical = retrieve_cmip5(model, variable, 'historical', period_hist)
    model_historical_selection = ct.cube.index_select(model_historical, time=select_hist)
    model_historical_mean = ct.cube.average(model_historical_selection, 'time')

    model_8_5_diff = (model_8_5_mean - model_historical_mean) / model_historical_mean * plot_scale

    fig = ct.cdsplot.geomap(
        model_8_5_diff, title=' Model: {}\nVariable: {}'.format(models[model], variables[variable]), 
        pcolormesh_kwargs={
            'vmin': -1*(100/plot_scale)*100, 'vmax': (100/plot_scale)*100, 
            'cmap': 'RdBu_r',
            'cbar_kwargs': {'label': ('%'), 'orientation': 'horizontal'}
        }
    )

    return fig, model_8_5_diff
