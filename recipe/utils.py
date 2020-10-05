from base_backend.utils import generate_random_code


def generate_participant_code():
    code = ''
    for i in range(3):
        code += generate_random_code()

    return code
