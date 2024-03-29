import unittest

# import coverage
from flask.cli import FlaskGroup

from project import create_app
# from project.api.models import User   ## seeding

app = create_app()
cli = FlaskGroup(create_app=create_app)

# COV = coverage.coverage(
#     branch=True,
#     include='project/api/*',
#     omit=[
#         'project/api/tests/*',
#         'project/config/config.py',
#     ]
# )
# COV.start()

# @cli.command()
# def recreate_db():
#     db.drop_all()
#     db.create_all()
#     db.session.commit()

# @cli.command()
# def seed_db():
#     """Seeds the database."""
#     db.session.add(User(
#         username='michael',
#         email='michael@reallynotreal.com',
#         password='greaterthaneight'
#     ))
#     db.session.add(User(
#         username='michaelherman',
#         email='michael@mherman.org',
#         password='greaterthaneight'
#     ))
#     db.session.commit()


@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/api/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


# @cli.command()
# def cov():
#     """Runs the unit tests with coverage."""
#     tests = unittest.TestLoader().discover('project/api/tests')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         COV.stop()
#         COV.save()
#         print('Coverage Summary:')
#         COV.report()
#         COV.html_report()
#         COV.erase()
#         return 0
#     return 1

if __name__ == '__main__':
    cli()
