from pondpy4tljh import (
    BeamSizeError,
    JoistSizeError,
    InvalidSupportError,
    TextColor,
    create_pondpy_models,
    package_input,
    validate_input,
)

def analyze_roof_bays(**kwargs):
    '''
    Performs the analysis of all roof bays specified by the user.

    Parameters
    ----------
    kwargs : key, value pair
        key, value pair to be entered into the dictionary
        
    Returns
    -------
    pondpy_models : list
        list of pondpy.PondPyModel objects representing each roof bay
    '''
    # Package up input from the user using the package_input() helper function
    print(TextColor.DARKCYAN+TextColor.BOLD+'Packing up the user input...'+TextColor.END)
    user_input = package_input(**kwargs)

    # Validate the user input using the validate_input() helper function
    print(TextColor.DARKCYAN+TextColor.BOLD+'Validating the input...'+TextColor.END)
    try:
        input_valid = validate_input(user_input)
    except KeyError as e:
        print(TextColor.RED+TextColor.BOLD+f'Validation failed!\nExpected {e} as input key but did not receive it. Please check your inputs.')
    except TypeError as e:
        print(TextColor.RED+TextColor.BOLD+f'Validation failed!\nAn error occurred: {e}.\nPlease check your inputs.'+TextColor.END)
    except BeamSizeError as e:
        print(TextColor.RED+TextColor.BOLD+f'Validation failed!\nBeam size {e} is not a valid size.\nIt is either not yet available, or does not exist.'+TextColor.END)
    except JoistSizeError as e:
        print(TextColor.RED+TextColor.BOLD+f'Validation failed!\nJoist size {e} is not a valid size.\nIt is either not yet available, or does not exist.'+TextColor.END)
    except InvalidSupportError as e:
        print(TextColor.RED+TextColor.BOLD+f'Validation failed!\n{e} is not a valid support type.'+TextColor.END)
    else:
        print(TextColor.GREEN+TextColor.BOLD+'Input successfully validated!'+TextColor.END)

    # Create the pondpy models
    if input_valid:
        print(TextColor.DARKCYAN+TextColor.BOLD+f'Creating the PondPyModel objects for {user_input['n_roof_bays']} roof bays...'+TextColor.END)

        pondpy_models = create_pondpy_models(user_input=user_input)

        print(TextColor.GREEN+TextColor.BOLD+f'Successfully created the PondPyModel objects for {user_input['n_roof_bays']} roof bays!'+TextColor.END)

        for bay in range(user_input['n_roof_bays']):
            print(TextColor.DARKCYAN+TextColor.BOLD+f'Analyzing the PondPyModel object for roof bay {bay+1}...'+TextColor.END)

            pondpy_models[bay].perform_analysis()

            print(TextColor.GREEN+TextColor.BOLD+f'Successfully analyzed roof bay {bay+1}!'+TextColor.END)

    return pondpy_models
