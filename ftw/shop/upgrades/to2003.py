from plone.app.upgrade.utils import loadMigrationProfile


def to_2003(context):
    loadMigrationProfile(context, 'profile-ftw.shop.upgrades:2003')
