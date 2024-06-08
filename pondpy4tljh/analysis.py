from pondpy4tljh import (
    BeamSizeError,
    JoistSizeError,
    InvalidSupportError,
    TextColor,
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
        validate_input(user_input)
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
        print(TextColor.GREEN+TextColor.BOLD+'Input successfully validated!'+TextColor.BOLD)