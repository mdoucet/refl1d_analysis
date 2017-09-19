import sys
sys.path.append('../src')

from refl1d_model import ReflectivityProblem

def test_parser():
    filepath = 'data/model152both'
    
    model = ReflectivityProblem(filepath)
    model.replace(range(24))

    assert model.model_list['T300'].layers['MGN_1']['MGN_1  interfaceM above'] == 0
    assert model.model_list['T300'].layers['MGN_2']['MGN_2 thickness'] == 21
    assert model.model_list['T050'].layers['MGN_2']['MGN_2 thickness'] == 21
