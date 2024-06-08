import numpy as np
from joistpy import sji
from steelpy import aisc

from pondpy import (
    Loading,
    PrimaryFraming,
    PrimaryMember,
    PondPyModel,
    SecondaryFraming,
    SecondaryMember,
    SteelBeamSize,
    SteelJoistSize,
)

from .exceptions import (
    BeamSizeError,
    JoistSizeError,
    InvalidSupportError,
)

AVAILABLE_BEAMS = aisc.profiles['W_shapes'].sections.keys()
AVAILABLE_JOISTS = sji.joist_type['K_Series'].designations.keys()
CONV_PSF_TO_KSI = 1/144/1000
VALID_SUPPORTS = {
    'ROLLER':(0, 1, 0),
    'PINNED':(1, 1, 0),
    'FIXED':(1, 1, 1),
}

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
                if support[1].upper() not in VALID_SUPPORTS.keys():
                    raise InvalidSupportError(f'{support[1]}')
                
    # Check that all input secondary support types are valid
    for bay in user_input['secondary_members_support']:
        for mem in bay:
            for support in mem:
                if support[1].upper() not in VALID_SUPPORTS.keys():
                    raise InvalidSupportError(f'{support[1]}')
                
    # Check that the rain load input is valid
    for bay in user_input['rain_load_input']:
        if len(bay) != 2:
            raise TypeError('the rain load for each bay must be entered in a (static head, hydraulic head) pair')
        elif not all(isinstance(rl, (int, float)) or rl >= 0 for rl in bay):
            raise TypeError('the static and hydraulic head must be non-negative int or float')
    
    return True
        
def create_pondpy_models(user_input):
    '''
    Creates the SteelBeamSize adn SteelJoistSize objects for each beam and joist
    size in the user input

    Parameters
    ----------
    user_input : dict
        dictionary containing the user input created by the package_input
        helper function

    Returns
    ----------
    pondpy_models : list
        list of pondpy.PondPyModel objects created for each roof bay in the
        user input
    '''
    # Start by creating a dictionary of pondpy.SteelBeamSize and pondpy.SteelJoistSize
    # objects for each beam and joist size in the user input
    beams = { beam.upper():SteelBeamSize(name=beam.upper(), properties=aisc.W_shapes.sections[beam.upper()]) for beam in user_input['beam_sizes'] }
    joists = { joist.upper():SteelJoistSize(name=joist.upper(), properties=sji.K_Series.designations['K_'+joist.upper()]) for joist in user_input['joist_sizes'] }
    active_sizes = beams | joists
    
    # Next create the pondpy.PrimaryMember and primary.SecondaryMember objects
    # for each primary and secondary member in each roof bay
    primary_members = []
    secondary_members = []

    for bay in range(user_input['n_roof_bays']):
        cur_primary_members = []
        for mem in range(len(user_input['primary_members_size'][bay])):
            cur_supports = []
            cur_size = active_sizes[user_input['primary_members_size'][bay][mem].upper()]
            cur_length = user_input['primary_members_length'][bay][mem]*12
            for support in user_input['primary_members_support'][bay][mem]:
                cur_supports.append([support[0]*12, VALID_SUPPORTS[support[1].upper()]])
            
            cur_primary_members.append(PrimaryMember(
                length=cur_length,
                size=cur_size,
                supports=cur_supports
            ))

        cur_secondary_members = []
        for mem in range(len(user_input['secondary_members_size'][bay])):
            cur_supports = []
            cur_size = active_sizes[user_input['secondary_members_size'][bay][mem].upper()]
            cur_length = user_input['secondary_members_length'][bay][mem]*12
            for support in user_input['secondary_members_support'][bay][mem]:
                cur_supports.append([support[0]*12, VALID_SUPPORTS[support[1].upper()]])
            
            cur_secondary_members.append(SecondaryMember(
                length=cur_length,
                size=cur_size,
                supports=cur_supports
            ))

        primary_members.append(cur_primary_members)
        secondary_members.append(cur_secondary_members)

    # Next create the pondpy.PrimaryFraming and pondpy.SecondaryFraming
    # objects for each roof bay
    primary_framing = []
    secondary_framing = []
    
    for bay in range(user_input['n_roof_bays']):
        primary_framing.append(PrimaryFraming(primary_members=primary_members[bay]))
        secondary_framing.append(SecondaryFraming(secondary_members=secondary_members[bay], slope=user_input['roof_slope'][bay]))

    # Next create the pondpy.Loading object for each roof bay
    loading = []

    for bay in range(user_input['n_roof_bays']):
        dead_load = user_input['dead_load_input'][bay]*CONV_PSF_TO_KSI
        rain_load = np.array(user_input['rain_load_input'][bay]).sum()*5.2*CONV_PSF_TO_KSI

        loading.append(Loading(dead_load=dead_load, rain_load=rain_load, include_sw=user_input['include_self_weight']))

    # Finally create the pondpy.PondPyModel object for each roof bay
    pondpy_models = []

    for bay in range(user_input['n_roof_bays']):
        pondpy_models.append(PondPyModel(
            primary_framing=primary_framing[bay],
            secondary_framing=secondary_framing[bay],
            loading=loading[bay],
            mirrored_left=user_input['roof_bay_mirrored'][bay][0],
            mirrored_right=user_input['roof_bay_mirrored'][bay][1],
            show_results=False,
        ))

    return pondpy_models
