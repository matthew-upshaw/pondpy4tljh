from ipywidgets import (
    Button,
    Dropdown,
    HBox,
    Output,
    VBox,
)

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

def get_model_index(options, value):
    '''
    Determines the index for the model selected in the roof_bayW dropdown.
    '''
    for i_option, option in enumerate(options):
        if value == option:
            return i_option
        
def plot_rain_depth(model):
    '''
    Plots the impounded rain depth for the selected pondpy.PondPyModel object
    as a 3D scatter plot.

    Parameters
    ----------
    model : pondpy.PondPyModel
        pondpy.PondPyModel object for which the impounded rain depth is to be
        plotted

    Returns
    -------
    fig : matplotlib.figure.Figure
        matplotlib.figure.Figure object containing the 3D scatter plot of the
        impounded rain depth for the selected plot
    '''
    x_values = []
    y_values = []
    z_values = []

    secondary_spacing = model.roof_bay.secondary_spacing/12

    for i_smodel, s_model in enumerate(model.roof_bay_model.secondary_models):
        cur_x_values = [x/12 for x in s_model.model_nodes]
        cur_y_values = [i_smodel*secondary_spacing]*len(cur_x_values)
        cur_z_values = [z for z in model.impounded_depth['Secondary'][i_smodel]]

        x_values.extend(cur_x_values)
        y_values.extend(cur_y_values)
        z_values.extend(cur_z_values)

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x_values, y_values, z_values)

    ax.set_title('Impounded Rain Depth (in)')
    ax.set_xlabel('Ls (ft)')
    ax.set_ylabel('Lp (ft)')

    plt.close()

    return fig


def create_plot_widget(analysis_summary, models):
    '''
    Creates the widget for creating the plots selected by the user.

    Parameters
    ----------
    analysis_summary : pd.DataFrame
        pandas DataFrame holding the analysis summary created by the
        show_analysis_summary() function
    models : list
        list of analyzed pondpy.PondPyModel objects
    '''
    roof_bayW = Dropdown(options=analysis_summary['Description'].unique().tolist())
    memberW = Dropdown(options=analysis_summary[analysis_summary['Description'] == roof_bayW.value]['Member'].to_list())
    plot_selectW = Dropdown(options=[
        'Deflection',
        'Shear Force',
        'Bending Moment',
    ])
    plot_buttonW = Button(description='Create Plot')
    outputW = Output()

    def get_member_options(*args):
        '''
        Updates the member options for the memberW dropdown based on the
        roof_bayW dropdown value
        '''
        memberW.options = analysis_summary[analysis_summary['Description'] == roof_bayW.value]['Member'].to_list()

    def plot_buttonW_callback(button):
        '''
        Prints the selected plot when the button is clicked.
        '''
        # Get the parameters for creating the plot selected by the user
        i_bay = get_model_index(options=roof_bayW.options, value=roof_bayW.value)
        type_member = memberW.value.split('-')[0]
        i_member = int(memberW.value.split('-')[1])-1
        type_plot = plot_selectW.value

        # Clear the output widget
        outputW.clear_output()

        # Get the selected model
        if type_member == 'P':
            model = models[i_bay].roof_bay_model.primary_models[i_member]
        elif type_member == 'S':
            model = models[i_bay].roof_bay_model.secondary_models[i_member]

        # Create the selected plot
        if type_plot == 'Deflection':
            selected_plot, _ = model.plot_deflected_shape()
        elif type_plot == 'Shear Force':
            selected_plot, _ = model.plot_sfd()
        elif type_plot == 'Bending Moment':
            selected_plot, _ = model.plot_bmd()

        with outputW:
            print(f'Roof Bay: {roof_bayW.value}, Member: {memberW.value}, Plot: {plot_selectW.value}')

            plt.figure(selected_plot)
            plt.show()

    roof_bayW.observe(get_member_options)
    plot_buttonW.on_click(plot_buttonW_callback)

    return VBox([HBox([roof_bayW, memberW, plot_selectW, plot_buttonW]), outputW])

def create_rain_plot_widget(analysis_summary, models):
    '''
    Creates the widget for creating the plots selected by the user.

    Parameters
    ----------
    analysis_summary : pd.DataFrame
        pandas DataFrame holding the analysis summary created by the
        show_analysis_summary() function
    models : list
        list of analyzed pondpy.PondPyModel objects    
    '''
    roof_bayW = Dropdown(options=analysis_summary['Description'].unique().tolist())
    plot_buttonW = Button(description='Create Plot')
    outputW = Output()

    def plot_buttonW_callback(button):
        '''
        Prints the selected plot when the button is clicked.
        '''
        # Get the parameters for creating the plot selected by the user
        i_bay = get_model_index(options=roof_bayW.options, value=roof_bayW.value)

        selected_plot = plot_rain_depth(models[i_bay])

        # Clear the output widget
        outputW.clear_output()

        with outputW:
            print(f'Impounded Rain Depth For: {roof_bayW.value}')

            plt.figure(selected_plot)
            plt.show()
    
    plot_buttonW.on_click(plot_buttonW_callback)

    return VBox([HBox([roof_bayW, plot_buttonW]), outputW])
