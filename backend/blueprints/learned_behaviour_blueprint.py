# Third party imports
from flask import Blueprint, jsonify

# Local application imports
from backend.managers import learned_behaviour_management

# Instantiate new blueprint
LearnedBehaviourBlueprint = Blueprint('learnedBehaviourManagement',
                                      __name__,
                                      url_prefix='/learned-behaviour')


# Routes
@LearnedBehaviourBlueprint.route('/grow-trees')
def growTrees():
    # Grow some trees
    result = learned_behaviour_management.growTrees()

    # Return the result
    return jsonify(result=result)
