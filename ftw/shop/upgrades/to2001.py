from plone.app.upgrade.utils import loadMigrationProfile


def to_2001(context):
    loadMigrationProfile(context, 'profile-ftw.shop.upgrades:2001')
