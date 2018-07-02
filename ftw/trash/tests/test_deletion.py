from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.testbrowser.pages import plone
from ftw.trash.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName


class TestDeletion(FunctionalTestCase):

    @browsing
    def test_deleted_content_is_marked_with_IRestorable(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Manager')

        folder = create(Builder('folder').within(create(Builder('folder'))))
        subfolder = create(Builder('folder').within(folder))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(3, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals(
            'Do you really want to delete this folder and all its contents?'
            ' (This will delete a total of 2 items.)',
            plone.first_heading())

        browser.click_on('Delete')
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(3, len(catalog.unrestrictedSearchResults()))
        self.assertTrue(IRestorable.providedBy(folder), 'Folder should provide IRestorable')
        self.assertTrue(ITrashed.providedBy(folder), 'Folder should provide ITrashed')
        self.assertFalse(IRestorable.providedBy(subfolder),
                         'Subfolder should not provide IRestorable')
        self.assertTrue(ITrashed.providedBy(subfolder), 'Subfolder should provide ITrashed')

    @browsing
    def test_children_of_site_root_are_trashed_instead_of_deleted(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Manager')

        folder = create(Builder('folder'))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')

        self.assertEquals('Do you really want to delete this folder and all its contents?',
                          plone.first_heading())
        browser.click_on('Delete')
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))
        self.assertTrue(IRestorable.providedBy(folder), 'Folder should provide IRestorable')
        self.assertTrue(ITrashed.providedBy(folder), 'Folder should provide ITrashed')
