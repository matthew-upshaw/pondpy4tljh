from joistpy import sji
from steelpy import aisc

from .exceptions import (
    BeamSizeError,
    JoistSizeError,
    InvalidSupportError,
)

AVAILABLE_BEAMS = aisc.profiles['W_shapes'].sections.keys()
AVAILABLE_JOISTS = sji.joist_type['K_Series'].designations.keys()
VALID_SUPPORTS = ['PINNED', 'ROLLER', 'FIXED']

def package_input(**kwargs):
    '''
    Packages the user input into a dictionary for quick and predictable access
    by other functions.

    Parameters
    ----------
    kwargs : key, value pair
        key, value pair to be entered into the dictionary

    Returns
    -------
    user_input : dict
        dictionary of all user input to be validated    
    '''

    user_input = {}
    for key, value in kwargs.items():
        user_input[key] = value

    return user_input

def validate_input(user_input):
    '''
    Validates the input from the user and raises exceptions as necessary.

    Parameters
    ----------
    user_input : dict
        dictionary of all user input to be validated

    Returns
    -------
    input_valid : bool
        bool indicating whether or not the user input is valid
    '''
    # Validate the input types
    if not isinstance(user_input['project_name'], str):
        raise TypeError('project_name must be a string')
    if not isinstance(user_input['project_number'], str):
        raise TypeError('project_number must be a string')
    if not isinstance(user_input['calc_description'], list):
        raise TypeError('calc_description must be a list')
    if not all(isinstance(desc, str) for desc in user_input['calc_description']):
        raise TypeError('each description in calc_description must be a string')
    if not isinstance(user_input['beam_sizes'], list):
        raise TypeError('beam_sizes must be a list')
    if not all(isinstance(size, str) for size in user_input['beam_sizes']):
        raise TypeError('each beam size in beam_sizes must be a string')
    if not isinstance(user_input['joist_sizes'], list):
        raise TypeError('joist_sizes must be a list')
    if not all(isinstance(size, str) for size in user_input['joist_sizes']):
        raise TypeError('each joist size in joist sizes must be a string')
    if not isinstance(user_input['n_roof_bays'], int) or user_input['n_roof_bays'] < 0:
        raise TypeError('n_roof_bays must be a non-negative integer')
    if not isinstance(user_input['primary_members_size'], list):
        raise TypeError('primary_members_size must be a list')
    if not isinstance(user_input['primary_members_length'], list):
        raise TypeError('primary_members_length msut be a list')
    if not isinstance(user_input['primary_members_support'], list):
        raise TypeError('primary_members_support must be a list')
    if not isinstance(user_input['secondary_members_size'], list):
        raise TypeError('secondary_members_size must be a list')
    if not isinstance(user_input['secondary_members_length'], list):
        raise TypeError('secondary_members_length must be a list')
    if not isinstance(user_input['secondary_members_support'], list):
        raise TypeError('secondary_members_support msut be a list')
    if not isinstance(user_input['roof_bay_mirrored'], list):
        raise TypeError('roof_bay_mirrored must be a list')
    if not isinstance(user_input['roof_slope'], list):
        raise TypeError('roof_slope must be a list')
    if not isinstance(user_input['dead_load_input'], list):
        raise TypeError('dead_load_input must be a list')
    if not all(isinstance(dl, (int, float)) for dl in user_input['dead_load_input']):
        raise TypeError('the surface dead load for each bay must be an integer or float')
    if not isinstance(user_input['rain_load_input'], list):
        raise TypeError('rain_load_input must be a list')
    if not all(isinstance(rl, tuple) for rl in user_input['rain_load_input']):
        raise TypeError('the rain load for each bay must be entered in a (static head, hydraulic head) pair')
    if not isinstance(user_input['include_self_weight'], bool):
        raise TypeError('include_self_weight must be either True or False')
    
    # Check that all input beam sizes are available
    for size in user_input['beam_sizes']:
        if size.upper() not in AVAILABLE_BEAMS:
            raise BeamSizeError(f'{size}')
        
    # Check that all input joist sizes are available
    for size in user_input['joist_sizes']:
        if ('K_'+size.upper()) not in AVAILABLE_JOISTS:
            raise JoistSizeError(f'{size}')
        
    # Check that all input primary support types are valid
    for bay in user_input['primary_members_support']:
        for mem in bay:
            for support in mem:
                if support[1].upper() not in VALID_SUPPORTS:
                    raise InvalidSupportError(f'{support[1]}')
                
    # Check that all input secondary support types are valid
    for bay in user_input['secondary_members_support']:
        for mem in bay:
            for support in mem:
                if support[1].upper() not in VALID_SUPPORTS:
                    raise InvalidSupportError(f'{support[1]}')
                
    # Check that the rain load input is valid
    for bay in user_input['rain_load_input']:
        if len(bay) != 2:
            raise TypeError('the rain load for each bay must be entered in a (static head, hydraulic head) pair')
        elif not all(isinstance(rl, (int, float)) or rl >= 0 for rl in bay):
            raise TypeError('the static and hydraulic head must be non-negative int or float')
