import pandas as pd

from pondpy import (
    SteelBeamDesign,
    SteelJoistDesign,
)

from pondpy4tljh import (
    BeamSizeError,
    JoistSizeError,
    InvalidSupportError,
    TextColor,
    package_input,
    validate_input,
)

def show_analysis_summary(models, **kwargs):
    '''
    Takes the analyzed pondpy.PondPyModel objects and reports the analysis/
    design summary in a pandas DataFrame object.

    Parameters
    ----------
    models : list
        list of analyzed pondpy.PondPyModel objects
    user_input : dict
        dictionary containing the user input created by the package_input
        helper function

    Returns
    -------
    analysis_summary : pandas.DataFrame
    '''
    user_input = package_input(**kwargs)

    try:
        # Validate the user input using the validate_input() helper function
        validate_input(user_input)

        columns = [
            'Description',
            'Member',
            'Member Size',
            'Max Moment (k-ft)',
            'Moment Capacity (k-ft)',
            'Max Shear (k)',
            'Shear Capacity (k)',
            'Deflection (in)',
            'L/d',
        ]
        calc_descs = []
        members = []
        member_size = []
        max_moment = []
        cap_moment = []
        max_shear = []
        cap_shear = []
        max_defl = []
        l_over_defl = []


        for i_model, model in enumerate(models):
            try:
                if user_input['calc_description'][i_model] == '':
                    cur_desc = f'Roof Bay {i_model+1}'
                else:
                    cur_desc = user_input['calc_description'][i_model]
            except IndexError:
                cur_desc = f'Roof Bay {i_model+1}'

            for i_pmodel, p_model in enumerate(model.roof_bay_model.primary_models):
                cur_max_moment = p_model.plot_bmd()[1][0]
                cur_max_shear = p_model.plot_sfd()[1][0]
                cur_max_defl = p_model.plot_deflected_shape()[1][0]

                cur_l_over_defl = int(round(abs(p_model.beam.length/cur_max_defl), 0))

                if p_model.beam.size.section_type == 'AISC':
                    cur_cap_moment = round(SteelBeamDesign(section=p_model.beam.size.properties, unbraced_length=0).get_moment_capacity(), 1)
                    cur_cap_shear = round(SteelBeamDesign(section=p_model.beam.size.properties, unbraced_length=0).get_shear_capacity(), 1)
                elif p_model.beam.size.section_type == 'SJI':
                    cur_cap_moment = round(SteelJoistDesign(designation=p_model.beam.size.properties, span=p_model.beam.length).get_moment_capacity(), 1)
                    cur_cap_shear = round(SteelJoistDesign(designation=p_model.beam.size.properties, span=p_model.beam.length).get_shear_capacity()[1], 1)

                calc_descs.append(cur_desc)
                members.append(f'P-{i_pmodel+1}')
                member_size.append(p_model.beam.size.name)
                max_moment.append(cur_max_moment)
                cap_moment.append(cur_cap_moment)
                max_shear.append(cur_max_shear)
                cap_shear.append(cur_cap_shear)
                max_defl.append(cur_max_defl)
                l_over_defl.append(cur_l_over_defl)
            
            for i_smodel, s_model in enumerate(model.roof_bay_model.secondary_models):
                cur_max_moment = s_model.plot_bmd()[1][0]
                cur_max_shear = s_model.plot_sfd()[1][0]
                cur_max_defl = s_model.plot_deflected_shape()[1][0]

                cur_l_over_defl = int(round(abs(s_model.beam.length/cur_max_defl), 0))

                if s_model.beam.size.section_type == 'AISC':
                    cur_cap_moment = round(SteelBeamDesign(section=s_model.beam.size.properties, unbraced_length=0).get_moment_capacity(), 1)
                    cur_cap_shear = round(SteelBeamDesign(section=s_model.beam.size.properties, unbraced_length=0).get_shear_capacity(), 1)
                elif s_model.beam.size.section_type == 'SJI':
                    cur_cap_moment = round(SteelJoistDesign(designation=s_model.beam.size.properties, span=s_model.beam.length).get_moment_capacity(), 1)
                    cur_cap_shear = round(SteelJoistDesign(designation=s_model.beam.size.properties, span=s_model.beam.length).get_shear_capacity()[1], 1)

                calc_descs.append(cur_desc)
                members.append(f'S-{i_smodel+1}')
                member_size.append(s_model.beam.size.name)
                max_moment.append(cur_max_moment)
                cap_moment.append(cur_cap_moment)
                max_shear.append(cur_max_shear)
                cap_shear.append(cur_cap_shear)
                max_defl.append(cur_max_defl)
                l_over_defl.append(cur_l_over_defl)

        df_list = list(zip(
            calc_descs,
            members,
            member_size,
            max_moment,
            cap_moment,
            max_shear,
            cap_shear,
            max_defl,
            l_over_defl,
        ))
        analysis_summary = pd.DataFrame(
            df_list, columns=columns
        )

        return analysis_summary

    except KeyError as e:
        print(TextColor.RED+TextColor.BOLD+f"Validation failed!\nExpected {e} as input key but did not receive it. Please check your inputs.")
    #except TypeError as e:
        #print(TextColor.RED+TextColor.BOLD+f"Validation failed!\nAn error occurred: {e}.\nPlease check your inputs."+TextColor.END)
    except BeamSizeError as e:
        print(TextColor.RED+TextColor.BOLD+f"Validation failed!\nBeam size {e} is not a valid size.\nIt is either not yet available, or does not exist."+TextColor.END)
    except JoistSizeError as e:
        print(TextColor.RED+TextColor.BOLD+f"Validation failed!\nJoist size {e} is not a valid size.\nIt is either not yet available, or does not exist."+TextColor.END)
    except InvalidSupportError as e:
        print(TextColor.RED+TextColor.BOLD+f"Validation failed!\n{e} is not a valid support type."+TextColor.END)   