from cs261.modules import DerivativeManagement


def testAddDerivative():
    newDerivative = {'id': 1, 'name': 'name'}
    DerivativeManagementModule = DerivativeManagement.DerivativeManagement()
    result = DerivativeManagementModule.addDerivative(newDerivative)
    assert result == newDerivative


def testGetDerivative():
    newDerivative = {'id': 1, 'name': 'name'}
    DerivativeManagementModule = DerivativeManagement.DerivativeManagement()
    DerivativeManagementModule.addDerivative(newDerivative)
    result = DerivativeManagementModule.getDerviative(newDerivative['id'])
    assert result == newDerivative
