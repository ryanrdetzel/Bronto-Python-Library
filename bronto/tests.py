import unittest
from bronto import *

class Test(unittest.TestCase):
    def setUp(self):
        self.test_email = 'ryan+1@tester.com'
        self.bronto = Bronto('DD839FBA-E630-46E4-B726-5E15700C11D9')

    def testCreateContact(self):
        bronto = self.bronto
        test_email = self.test_email

        d = {
            'email':test_email,
            'msgPref':'text'
        }
        try:
            bronto.save(BrontoContact(d))
        except SaveContactFailed:
            fail("Contact already exists")

        me = bronto.getContact(test_email)
        self.assertEqual(me.email, test_email, "Emails did not match")

        bronto.delete(me) 
        self.assertEqual(me.id,None,"Failed to delete contact")

        bronto.save(me)
        self.assertNotEqual(me.id,None,"Failed to get new id for save")

        ## Cleanup 
        bronto.delete(me) 
        self.assertEqual(me.id,None,"Failed to delete contact")

if __name__ == '__main__':
    unittest.main()
