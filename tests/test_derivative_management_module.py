from cs261.modules import DerivativeManagement


def testAddDerivative():
    pass

def testGetDerivative():
    newDerivative = {'id': 1, 'name': 'name'}
    DerivativeManagement.addDerivative(newDerivative)
    result = DerivativeManagement.getDerviative(newDerivative['id'])
    assert result == newDerivative
