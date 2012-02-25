from suds.client import Client
from suds import WebFault

class BrontoError(Exception):
    def __init__(self,code,string):
        self.code = code
        self.string = string
    def __str__(self):
        return "(%s) %s" % (self.code,self.string)

class LoginError(BrontoError):
    pass

class SaveContactFailed(BrontoError):
    pass

 
class Bronto(object):
    '''
        Base Bronto class, accepts only the api key as an init arg
    '''
    def __init__(self,token):
        BRONTO_WSDL = 'https://api.bronto.com/v4?wsdl'
        self.api = Client(BRONTO_WSDL)
        try:
            self.session_id = self.api.service.login(token)
        except WebFault, e:
            print e
            raise LoginError

        self.session_header = self.api.factory.create("sessionHeader")
        self.session_header.sessionId = self.session_id
        self.api.set_options(soapheaders=self.session_header)

    def save(self,obj):
        return obj.save(self)

    def delete(self,obj):
        return obj.delete(self)

    def __buildContactFilter(self,email):
        stringValue = self.api.factory.create('stringValue')
        filterOperator = self.api.factory.create('filterOperator')
        filterType = self.api.factory.create('filterType')
        filter = self.api.factory.create('contactFilter')

        stringValue.value = email
        stringValue.operator = filterOperator.EqualTo

        filter.email = stringValue
        filter.type = filterType.AND
        
        return filter

    def getContact(self,email):
        filter = self.__buildContactFilter(email) 
        contact = self.api.service.readContacts(filter,includeLists=True)
        return BrontoContact(contact[0])

    def contactList(self):
        filter = self.api.factory.create('contactFilter')
        filterType = self.api.factory.create('filterType') 
        filter.type = filterType.AND

        contacts = []
        for contact in self.api.service.readContacts(filter, includeLists = True, pageNumber = 1):
            contacts.append(BrontoContact(contact))

        return contacts

class BrontoContact(object):
    ''' Basic Bronto contact '''
    def __init__(self,data):
        self.listIds = ''  # cant be empty from api
        self.fields = []
        if type(data) is dict:
            for obj,val in data.items():
                setattr(self,obj,val)
        else:
            for obj,val in data:
                setattr(self,obj,val)

    def delete(self,bronto):
        contact = bronto.api.factory.create('contactObject')
        contact.email = self.email
        delete_contact = bronto.api.service.deleteContacts(contact)
        if delete_contact.results[0].isError == True:
            raise SaveContactFailed(
                delete_contact.results[0]['errorCode'],
                delete_contact.results[0]['errorString'])
        else:
            ## Clear out the id so if we save it adds not updates
            self.id = None 
        return self

    def save(self,bronto):
        ''' If it's a new contact create it otherwise update '''
        if hasattr(self,'id') and self.id is not None:
            ''' update '''
            c = bronto.api.factory.create('contactObject')
            c.id = self.id
            c.email = self.email
            c.status = self.status
            c.msgPref = self.msgPref
            c.source = self.source
            c.customSource = self.customSource
            c.listIds = self.listIds
            c.fields = self.fields
            bronto.api.service.updateContacts([c])
            return self
        else:
            ''' create '''   
            contact = bronto.api.factory.create('contactObject')
            contact.email = self.email
            add_contact = bronto.api.service.addContacts(contact)
            if add_contact.results[0].isError == True:
                raise SaveContactFailed(
                    add_contact.results[0]['errorCode'],
                    add_contact.results[0]['errorString'])
            else:
                self.id = add_contact.results[0].id
            return self 
