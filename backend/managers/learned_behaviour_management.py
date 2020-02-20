# Standard library imports
import random

# Local application imports
from backend.derivatex_models import DecisionTreeNode, Label, Derivative, Action, ActionType


def growTrees():
    """Grow decision trees from the current data.

    This function will grow a number of decision trees from the
    erroneous data in the database.
    """

    trainingData, testData = compileData()

    testNode = DecisionTreeNode.query.get(1)
    return testNode.split(derivatives)

    return data

def compileData():
    # Get all of the data
    derivatives = Derivative.query.filter(Derivative.id <= 50, Derivative.deleted is False).all()

    # Calculate the features and label of each derivative
    validData = []
    erroneousData = []
    for derivative in derivatives:
        if len(derivative.associated_actions) > 1:
            history = [derivative.__dict__]
            history[0].pop('_sa_instance_state')
            actions = derivative.associated_actions
            actions.reverse()
            for actionId in actions:
                action = Action.query.get(actionId)
                if action.type == ActionType.UPDATE:
                    historicalDerivative = history[-1].copy()
                    historicalDerivative[action.update_log['attribute']] = action.update_log['old_value']
                    history.append(historicalDerivative)
            validData.append({
                'label': Label.VALID,
                'derivative': history[0]
            })
            for historicalDerivative in history[1:]:
                erroneousData.append({
                    'label': Label.ERRONEOUS,
                    'derivative': historicalDerivative
                })
        else:
            derivativeDict = derivative.__dict__
            derivativeDict.pop('_sa_instance_state')
            validData.append({
                'label': Label.VALID,
                'derivative': derivativeDict
            })

    # Split data into training and test data
    trainingData = []
    testData = []
    for item in validData:
        if random.random() > 0.2:
            testData.append(item)
        else:
            trainingData.append(item)
    for item in erroneousData:
        if random.random() > 0.2:
            testData.append(item)
        else:
            trainingData.append(item)

    # Return the data
    return trainingData, testData
