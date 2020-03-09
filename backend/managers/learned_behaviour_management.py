# flake8: noqa

# Standard library imports
import random
import datetime
from dateutil.relativedelta import *

# Local application imports
from backend.managers import external_management
from backend.db import db
from backend.derivatex_models import DecisionTreeNode, Label, Derivative, Action, ActionType, Features


def indexTrees():
    """Index all the decision trees.

    Returns:
        list: List of all DecisionTreeNodes.
    """
    rootNodes = DecisionTreeNode.query.filter(DecisionTreeNode.parent_id == None).all()

    return rootNodes


def getNode(node_id):
    """Get a given node.

    Args:
        node_id (int): The ID of the node to be retreived.
    Returns:
        DecisionTreeNode: The decision tree node with the given ID.
    """

    return DecisionTreeNode.query.get(node_id)


def getFlags(node_id):
    """Gets the flags for a give tree.

    Args:
        node_id (int): The ID of the tree to be ran.
    Returns:
        list: List of suspect derivatives.
    """

    return splitOnTree(getNode(node_id))[Label.ERRONEOUS]


def verifyDerivative(derivative):
    data = [{'derivative': derivative}]

    all_trees = DecisionTreeNode.query.filter(DecisionTreeNode.approved == 1).all()
    result = []

    for root_node in all_trees:
        results = splitOnNode(root_node, data)
        if len(results[Label.ERRONEOUS]) == 1:
            result.append(root_node)

    return result


def splitOnTree(root_node):
    # Gather data
    one_month_ago = datetime.date.today() - relativedelta(months=1)
    nonAbsoluteDerivatives = Derivative.query.filter(Derivative.date_of_trade >= one_month_ago).all()
    data = []
    for derivative in nonAbsoluteDerivatives:
        derivative = derivative.__dict__
        derivative.pop('_sa_instance_state')
        data.append({'derivative': derivative})

    # Split the data
    result = splitOnNode(root_node, data)

    # Update the last flag count
    root_node.last_flag_count = len(result[Label.ERRONEOUS])
    db.session.add(root_node)
    db.session.flush()

    return result


def splitOnNode(node, data):
    result = {
        Label.VALID: [],
        Label.ERRONEOUS: []
    }

    trueSplit, falseSplit = node.split(data)

    if node.true_label:
        result[node.true_label] = trueSplit
    else:
        trueChildResult = splitOnNode(node.true_node, trueSplit)
        result[Label.VALID] += trueChildResult[Label.VALID]
        result[Label.ERRONEOUS] += trueChildResult[Label.ERRONEOUS]

    if node.false_label:
        result[node.false_label] = falseSplit
    else:
        falseChildResult = splitOnNode(node.false_node, falseSplit)
        result[Label.VALID] += falseChildResult[Label.VALID]
        result[Label.ERRONEOUS] += falseChildResult[Label.ERRONEOUS]

    return result


def updateNode(node, updates):
    """ Updates the attributes of the given node with new values.

    Args:
        node (DecisionTreeNode): The node to be updated.
        updates (dict): A dictionary of node attribute, value pairs.

    Returns:
        None
    """

    # Apply all updates to the node
    for attribute, new_value in updates.items():
        # Restrict updatable attributes
        if not hasattr(node, attribute) or attribute not in ['description', 'approved', 'automated', 'suggested_value', 'suggested_feature']:
            continue

        # Perform update
        setattr(node, attribute, new_value)

    db.session.add(node)
    db.session.flush()

    # Return None
    return None


def indexNodeActions(tree_id):
    """Index all actions taken by a given tree.

    This function returns a list of all actions
    that have been taken by a tree of a given id
    """
    return Action.query.filter(Action.tree_id == tree_id).all()


def removeTree(root_node):
    all_nodes = []
    q = [root_node]
    all_nodes.append(root_node)
    while len(q) > 0:
        current_node = q.pop()
        if current_node.true_node_id:
            q.append(current_node.true_node)
            all_nodes.append(current_node.true_node)
        if current_node.false_node_id:
            q.append(current_node.false_node)
            all_nodes.append(current_node.false_node)

    for node in all_nodes:
        db.session.delete(node)
    db.session.flush()


def removeUnapprovedTrees():
    """Removes unapproved trees from the database
    """
    root_nodes = DecisionTreeNode.query.filter(DecisionTreeNode.approved == 0).filter(DecisionTreeNode.parent_id == None)
    for node in root_nodes:
        removeTree(node)
    db.session.commit()


def growTrees():
    """Grow decision trees from the current data.

    This function will grow a number of decision trees from the
    erroneous data in the database.
    """

    trainingData, testData = compileData()

    validTrainingData = [x for x in trainingData if x['label'] == Label.VALID]
    errorsLeftToFind = [x for x in trainingData if x['label'] == Label.ERRONEOUS]

    number_of_trees = 0
    total_starting_errors = len(errorsLeftToFind)
    finished = False

    while number_of_trees < 10 and not finished:
        number_of_trees += 1
        print(f"Training tree {number_of_trees}")
        print(f"{len(errorsLeftToFind)} errors left to find")
        trainingData = validTrainingData + errorsLeftToFind
        rootNode = growTree(trainingData)
        result = splitOnNode(rootNode, trainingData)
        truePositives = [x for x in result[Label.ERRONEOUS] if x['label'] == Label.ERRONEOUS]
        falsePositives = [x for x in result[Label.ERRONEOUS] if x['label'] == Label.VALID]
        print(len(truePositives))
        print((len(truePositives) + len(falsePositives)))
        rootNode.confidence = (len(truePositives) / (len(truePositives) + len(falsePositives))) * 100
        if len(truePositives) / total_starting_errors < 0.05:
            removeTree(rootNode)
        db.session.flush()
        errorsLeftToFind = [x for x in result[Label.VALID] if x['label'] == Label.ERRONEOUS]
        if len(errorsLeftToFind) / total_starting_errors < 0.1:
            finished = True

    db.session.commit()

    return 1


def growTree(trainingData):

    potentialNodeCriteria = generatePotentialNodeCriteria()
    q = []
    finished = False
    q.append(growNode(potentialNodeCriteria, trainingData))
    trueLabel, falseLabel = getNodeLabel(q[0][1], q[0][2])
    q[0][0].true_label = trueLabel
    q[0][0].false_label = falseLabel
    db.session.add(q[0][0])
    db.session.flush()
    rootNodeId = q[0][0].id
    while len(q) > 0 and not finished:
        currentNodeData = q.pop(0)
        currentNode = currentNodeData[0]
        trueData = currentNodeData[1]
        falseData = currentNodeData[2]
        # Check for the tree being complete

        trueNodeData = growNode(potentialNodeCriteria, trueData)
        trueLabel, falseLabel = getNodeLabel(trueNodeData[1], trueNodeData[2])
        impurity = calculateGiniImpurity(trueNodeData[1], trueNodeData[2])
        # print(f"trueNode: {trueNodeData[0]}")
        # print(f"truelabel: {trueLabel}")
        # print(f"falselabel: {falseLabel}")
        # print(f"impurity: {calculateGiniImpurity(trueNodeData[1], trueNodeData[2])}")
        # print()
        trueNodeData[0].parent_id = currentNode.id
        trueNodeData[0].true_label = trueLabel
        trueNodeData[0].false_label = falseLabel
        currentNode.true_label = None
        db.session.add(trueNodeData[0])
        currentNode.true_node_id = trueNodeData[0].id
        q.append(trueNodeData)

        if trueLabel == Label.ERRONEOUS or falseLabel == Label.ERRONEOUS:
            finished = True

        db.session.flush()
        currentNode.true_node_id = trueNodeData[0].id

        if not finished:
            falseNodeData = growNode(potentialNodeCriteria, falseData)
            trueLabel, falseLabel = getNodeLabel(falseNodeData[1], falseNodeData[2])
            # impurity = calculateGiniImpurity(falseNodeData[1], falseNodeData[2])
            # print(f"trueNode: {falseNodeData[0]}")
            # print(f"truelabel: {trueLabel}")
            # print(f"falselabel: {falseLabel}")
            # print(f"impurity: {calculateGiniImpurity(trueNodeData[1], trueNodeData[2])}")
            # print()
            falseNodeData[0].parent_id = currentNode.id
            falseNodeData[0].true_label = trueLabel
            falseNodeData[0].false_label = falseLabel
            currentNode.false_label = None
            db.session.add(falseNodeData[0])
            db.session.flush()
            currentNode.false_node_id = falseNodeData[0].id
            q.append(falseNodeData)

            if trueLabel == Label.ERRONEOUS or falseLabel == Label.ERRONEOUS:
                finished = True

        db.session.add(currentNode)
        db.session.flush()
        db.session.commit()

    # Prune the resulting tree
    pruneNode(getNode(rootNodeId))

    erroneous_split = splitOnNode(getNode(rootNodeId), trainingData)[Label.ERRONEOUS]
    correct_erroneous_split = [x for x in erroneous_split if x['label'] == Label.ERRONEOUS]

    suggested_features = {}
    for err in correct_erroneous_split:
        if err["erroneous_field"] not in suggested_features:
            suggested_features[err["erroneous_field"]] = 1
        else:
            suggested_features[err["erroneous_field"]] += 1

    for feature in suggested_features:
        if suggested_features[feature] / len(correct_erroneous_split) > 0.9:
            getNode(rootNodeId).suggested_feature = feature
            db.session.flush()

    if getNode(rootNodeId).suggested_feature:
        suggested_values = {}
        for err in correct_erroneous_split:
            if err["correction"] not in suggested_values:
                suggested_values[err["correction"]] = 1
            else:
                suggested_values[err["correction"]] += 1

        for value in suggested_values:
            if suggested_values[value] / len(correct_erroneous_split) > 0.9:
                getNode(rootNodeId).suggested_value = value
                db.session.flush()

    db.session.commit()
    return getNode(rootNodeId)


def pruneNode(node):
    if (node.true_node_id is not None):
        pruneNode(DecisionTreeNode.query.get(node.true_node_id))

    if (node.false_node_id is not None):
        pruneNode(DecisionTreeNode.query.get(node.false_node_id))

    if node.true_label is not None and node.false_label is not None:
        if node.true_label == node.false_label:
            parentNode = DecisionTreeNode.query.get(node.parent_id)
            isTrueNode = parentNode.true_node_id == node.id
            if isTrueNode:
                parentNode.true_label = node.true_label
                parentNode.true_node_id = None
            else:
                parentNode.false_label = node.false_label
                parentNode.false_node_id = None
            db.session.delete(node)

    db.session.flush()


def getNodeLabel(trueSplit, falseSplit):
    trueValid = len([x for x in trueSplit if x['label'] == Label.VALID])
    trueErroneous = len([x for x in trueSplit if x['label'] == Label.ERRONEOUS])
    if trueValid >= trueErroneous:
        trueLabel = Label.VALID
    else:
        trueLabel = Label.ERRONEOUS

    falseValid = len([x for x in falseSplit if x['label'] == Label.VALID])
    falseErroneous = len([x for x in falseSplit if x['label'] == Label.ERRONEOUS])
    if falseValid >= falseErroneous:
        falseLabel = Label.VALID
    else:
        falseLabel = Label.ERRONEOUS

    return trueLabel, falseLabel


def growNode(potentialNodeCriteria, trainingData):
    bestNode = None
    bestImpurity = 1.1
    for nodeCriteria in potentialNodeCriteria:
        potentialNode = DecisionTreeNode(feature=nodeCriteria[0],
                                         criteria=nodeCriteria[1])

        trueSplit, falseSplit = potentialNode.split(trainingData)
        impurity = calculateGiniImpurity(trueSplit, falseSplit)
        if impurity < bestImpurity:
            bestImpurity = impurity
            bestNode = potentialNode

    trueSplit, falseSplit = bestNode.split(trainingData)
    return bestNode, trueSplit, falseSplit


def calculateGiniImpurity(trueSplit, falseSplit):
    if (len(trueSplit) + len(falseSplit)) == 0:
        return 0
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

    potentialNodes = [(Features.BUYING_PARTY, x.id) for x in external_management.indexCompanies()]
    potentialNodes += [(Features.SELLING_PARTY, x.id) for x in external_management.indexCompanies()]
    potentialNodes += [(Features.ASSET, x) for x in external_management.indexAssets()]
    potentialNodes += [(Features.QUANTITY, x) for x in statisticalCriteria]
    potentialNodes += [(Features.STRIKE_PRICE, x) for x in statisticalCriteria]
    return potentialNodes


def compileData():
    # Get all of the data
    derivatives = Derivative.query.filter(Derivative.id <= 25000, Derivative.deleted == False).all() # noqa E712

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
                    erroneousData.append({
                        'label': Label.ERRONEOUS,
                        'derivative': historicalDerivative,
                        'erroneous_field': action.update_log['attribute'],
                        'correction': action.update_log['new_value']
                    })
            validData.append({
                'label': Label.VALID,
                'derivative': history[0],
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
        if random.random() > 0.5:
            testData.append(item)
        else:
            trainingData.append(item)
    for item in erroneousData:
        if random.random() > 0.5:
            testData.append(item)
        else:
            trainingData.append(item)

    # Return the data
    return trainingData, testData
