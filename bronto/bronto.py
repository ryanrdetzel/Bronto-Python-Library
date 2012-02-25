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

class DeleteContactFailed(BrontoError):
    pass

class SaveListFailed(BrontoError):
    pass
 
class DeleteListFailed(BrontoError):
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

    def getContacts(self,status=None,created=None,page=1):
        filter = self.api.factory.create('contactFilter')
        filterType = self.api.factory.create('filterType') 
        filter.type = filterType.AND

        if status:
            filter.status = status 

        contacts = []
        for contact in self.api.service.readContacts(filter, includeLists = True, pageNumber=page):
            contacts.append(BrontoContact(contact))

        return contacts

    def getLists(self,page=1):
        filter = self.api.factory.create('mailListFilter')
        filterType = self.api.factory.create('filterType')
        filter.type = filterType.AND
        
        lists = []
        for list in self.api.service.readLists(filter,pageNumber=page):
            lists.append(BrontoList(list))
        return lists

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
            raise DeleteContactFailed(
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
            ## Init all the required fields?
            add_contact = bronto.api.service.addContacts(contact)
            if add_contact.results[0].isError == True:
                raise SaveContactFailed(
                    add_contact.results[0]['errorCode'],
                    add_contact.results[0]['errorString'])
            else:
                self.id = add_contact.results[0].id
            return self 

class BrontoList(object):
    def __init__(self,data):
        if type(data) is dict:
            for obj,val in data.items():
                setattr(self,obj,val)
        else:
            for obj,val in data:
                setattr(self,obj,val)

        ## check to at least name and label

    def delete(self,bronto):
        if hasattr(self,'id') and self.id is not None:
            maillist = bronto.api.factory.create('mailListObject')
            maillist.id = self.id
            delete_list = bronto.api.service.deleteLists(maillist)
            if delete_list.results[0].isError == True:
                raise DeleteListFailed(
                    delete_list.results[0]['errorCode'],
                    delete_list.results[0]['errorString'])
            else:
                ## Clear out the id so if we save it adds not updates
                self.id = None
        else:
            ## Object is not on bronto server
            pass 
        return self

    def save(self,bronto):
        ''' If it's a new contact create it otherwise update '''
        if hasattr(self,'id') and self.id is not None:
            ''' update '''
            c = bronto.api.factory.create('mailListObject')
            c.id = self.id
            c.status = self.status
            c.label = self.label
            c.name = self.name
            c.activeCount = self.activeCount
            c.visibility = self.visibility
            bronto.api.service.updateLists([c])
            return self
        else:
            ''' create '''
            maillist = bronto.api.factory.create('mailListObject')
            maillist.name = self.name
            maillist.label = self.label
            #maillist.status = self.status
            #maillist.activeCount = self.activeCount
            #maillist.visibiliy = self.visibility
            maillists = bronto.api.service.addLists(maillist)
            if maillists.results[0].isError == True:
                raise SaveListFailed(
                    maillists.results[0]['errorCode'],
                    maillists.results[0]['errorString'])
            else:
                self.id = maillists.results[0].id
            return self
