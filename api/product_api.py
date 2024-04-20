import flask
from data import db_session
from data.products import Product

blueprint = flask.Blueprint(
    'product_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/products')
def get_products():
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).all()
    return flask.jsonify(
        {
            'prod':
                [item.to_dict(
                    only=('id', 'name', 'type', 'price', 'description'))
                 for item in prod]
        }
    )


@blueprint.route('/api/products/<int:id>', methods=['GET'])
def get_one_job(id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).get(id)
    if not prod:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify(
        {
            'prod': prod.to_dict(only=(
                'id', 'name', 'type', 'price', 'description'
            ))
        }
    )

