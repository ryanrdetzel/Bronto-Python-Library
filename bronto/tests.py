import unittest
from bronto import *
from configobj import ConfigObj

class Test(unittest.TestCase):
    def setUp(self):
        conf = ConfigObj('settings.ini')
        self.test_email = 'ryan+1@tester.com'
        self.bronto = Bronto(conf['token'])

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
