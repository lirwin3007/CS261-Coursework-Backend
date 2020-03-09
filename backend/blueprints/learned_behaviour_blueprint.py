# Third party imports
from flask import Blueprint, jsonify, request, abort

# Local application imports
from backend.db import db

# Local application imports
from backend.managers import learned_behaviour_management

# Instantiate new blueprint
LearnedBehaviourBlueprint = Blueprint('learnedBehaviourManagement',
                                      __name__,
                                      url_prefix='/learned-behaviour')


# Routes
@LearnedBehaviourBlueprint.route('/grow-trees')
def growTrees():
    # Remove any unapproved trees
    learned_behaviour_management.removeUnapprovedTrees()

    # Grow some trees
    result = learned_behaviour_management.growTrees()

    # Return the result
    return jsonify(result=result)

@LearnedBehaviourBlueprint.route('/index-trees')
def indexTrees():
    # Index all trees
    trees = learned_behaviour_management.indexTrees()
    # Index all tree actions
    actions = {tree.id: learned_behaviour_management.indexNodeActions(tree.id) for tree in trees}

    # Return the result
    return jsonify(trees=trees, actions=actions)

@LearnedBehaviourBlueprint.route('/get-flags/<tree_id>')
def getFlags(tree_id):
    # Get flags
    flags = learned_behaviour_management.getFlags(tree_id)

    # Jsonify the flags
    if len(flags) > 100:
        flags = flags[:100]
    flags = [{'derivative': flag['derivative']} for flag in flags]

    # Return the result
    return {'flags': flags}

@LearnedBehaviourBlueprint.route('/verify-derivative', methods=['POST'])
def verifyDerivative():
    # Retreive json body from request
    body = request.get_json()

    # Obtain new derivative
    new_derivative = body.get('derivative')

    # Return the result of verifying the derivative
    return {'result': learned_behaviour_management.verifyDerivative(new_derivative)}


@LearnedBehaviourBlueprint.route('/update-tree/<tree_id>', methods=['POST'])
def updateTree(tree_id):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400, 'empty request body')

    # Retreive json body from request
    body = request.get_json()

    # Obtain updates
    updates = body.get('updates')

    # Retreive the specified node
    node = learned_behaviour_management.getNode(tree_id)

    # Verify node exists
    if node is None:
        return abort(404, f'node id {tree_id} does not exist')

    # Update the node
    learned_behaviour_management.updateNode(node, updates)

    # Commit the derivative updates to the database
    db.session.commit()

    # Make response
    return jsonify()
