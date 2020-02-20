# Standard library imports
import random

# Local application imports
from backend import external_api
from backend.derivatex_models import DecisionTreeNode, Label, Derivative, Action, ActionType, Features


def growTrees():
    """Grow decision trees from the current data.

    This function will grow a number of decision trees from the
    erroneous data in the database.
    """

    trainingData, testData = compileData()
    potentialNodeCriteria = generatePotentialNodeCriteria()

    rootNode, rootTrueSplit, rootFalseSplit = growNode(potentialNodeCriteria, trainingData)
    childTrueNode, childTrueTrueSplit, childTrueFalseSplit = growNode(potentialNodeCriteria, rootTrueSplit)
    childFalseNode, childFalseTrueSplit, childFalseFalseSplit = growNode(potentialNodeCriteria, rootFalseSplit)

    childTrueLabelTrue, childTrueLabelFalse = getNodeLabel(childTrueTrueSplit, childTrueFalseSplit)
    childFalseLabelTrue, childFalseLabelFalse = getNodeLabel(childFalseTrueSplit, childFalseFalseSplit)

    print(f"If {rootNode.feature} == {rootNode.criteria}:")
    print(f"\tIf {childTrueNode.feature} == {childTrueNode.criteria}:")
    print(f"\t\t{childTrueLabelTrue}")
    print(f"\tElse:")
    print(f"\t\t{childTrueLabelFalse}")
    print(f"Else:")
    print(f"\tIf {childFalseNode.feature} == {childFalseNode.criteria}:")
    print(f"\t\t{childFalseLabelTrue}")
    print(f"\tElse:")
    print(f"\t\t{childFalseLabelFalse}")
    print()
    print()

    return 1

def getNodeLabel(trueSplit, falseSplit):
    trueValid = len([x for x in trueSplit if x['label'] == Label.VALID])
    trueErroneous = len([x for x in trueSplit if x['label'] == Label.ERRONEOUS])
    if trueValid > trueErroneous:
        trueLabel = Label.VALID
    else:
        trueLabel = Label.ERRONEOUS

    falseValid = len([x for x in falseSplit if x['label'] == Label.VALID])
    falseErroneous = len([x for x in falseSplit if x['label'] == Label.ERRONEOUS])
    if falseValid > falseErroneous:
        falseLabel = Label.VALID
    else:
        falseLabel = Label.ERRONEOUS

    return trueLabel, falseLabel

def growNode(potentialNodeCriteria, trainingData):
    bestNode = None
    bestImpurity = 1.1
    for nodeCriteria in potentialNodeCriteria:
        potentialNode = DecisionTreeNode(feature = nodeCriteria[0],
                                         criteria = nodeCriteria[1])

        trueSplit, falseSplit = potentialNode.split(trainingData)
        impurity = calculateGiniImpurity(trueSplit, falseSplit)
        if impurity < bestImpurity:
            bestImpurity = impurity
            bestNode = potentialNode

    trueSplit, falseSplit = bestNode.split(trainingData)
    return bestNode, trueSplit, falseSplit

def calculateGiniImpurity(trueSplit, falseSplit):
    alpha = len(trueSplit) / (len(trueSplit) + len(falseSplit))

    trueSplitValidData = list(filter(lambda x: x['label'] == Label.VALID, trueSplit))
    trueSplitErroneousData = list(filter(lambda x: x['label'] == Label.ERRONEOUS, trueSplit))
    if len(trueSplitValidData) > 0 and len(trueSplitErroneousData) > 0:
        trueP = len(trueSplitValidData) / (len(trueSplitValidData) + len(trueSplitErroneousData))
    else:
        trueP = 0
    trueImpurity = 2 * trueP * (1 - trueP)

    falseSplitValidData = list(filter(lambda x: x['label'] == Label.VALID, falseSplit))
    falseSplitErroneousData = list(filter(lambda x: x['label'] == Label.ERRONEOUS, falseSplit))
    if len(falseSplitValidData) > 0 and len(falseSplitErroneousData) > 0:
        falseP = len(falseSplitValidData) / (len(falseSplitValidData) + len(falseSplitErroneousData))
    else:
        falseP = 0
    falseImpurity = 2 * falseP * (1 - falseP)

    impurity = alpha * trueImpurity + (1 - alpha) * falseImpurity
    return impurity

def generatePotentialNodeCriteria():
    statisticalCriteria = ['less_than_mean', 'more_than_mean', '0_to_1_std', '1_to_2_std', '2_to_3_std', '3_to_inf_std']

    potentialNodes =  [(Features.BUYING_PARTY, x.id) for x in external_api.getAllCompanies()]
    potentialNodes += [(Features.SELLING_PARTY, x.id) for x in external_api.getAllCompanies()]
    potentialNodes += [(Features.ASSET, x.name) for x in external_api.getAllProducts()]
    potentialNodes += [(Features.QUANTITY, x) for x in statisticalCriteria]
    potentialNodes += [(Features.STRIKE_PRICE, x) for x in statisticalCriteria]
    return potentialNodes

def compileData():
    # Get all of the data
    derivatives = Derivative.query.filter(Derivative.id <= 50000, Derivative.deleted == False).all()

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
