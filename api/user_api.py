import flask
from data import db_session
from data.users import User

blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    user = db_sess.query(User).all()
    return flask.jsonify(
        {
            'user':
                [item.to_dict(
                    only=('id', 'surname', 'name', 'patronymic', 'age', 'email', 'modified_date', 'contact_phone',
                          'address', 'flat', 'photo'))
                    for item in user]
        }
    )


@blueprint.route('/api/users/<int:id>', methods=['GET'])
def get_one_user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    if not user:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify(
        {
            'user': user.to_dict(only=(
                'id', 'surname', 'name', 'patronymic', 'age', 'email', 'modified_date', 'contact_phone',
                'address', 'flat', 'photo'
            ))
        }
    )
