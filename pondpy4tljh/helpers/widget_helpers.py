from ipywidgets import (
    Button,
    Dropdown,
    HBox,
    Output,
    VBox,
)

from matplotlib import pyplot as plt

def get_model_index(options, value):
    '''
    Determines the index for the model selected in the roof_bayW dropdown.
    '''
    for i_option, option in enumerate(options):
        if value == option:
            return i_option

def create_plot_widget(analysis_summary, models):
    '''
    Creates the dropdowns for creating the plots selected by the user.

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

