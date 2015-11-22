import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images

import webapp2
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

USER_EMAIL = ''

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'
# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.

def guestbook_key(social="default_user"):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('SocialGiving', social)
class Categories(ndb.Model):
    cat_name = ndb.StringProperty(indexed=True)
    cat_users = ndb.StringProperty(repeated=True)


class User(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    Firstname = ndb.StringProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)
    contact_no = ndb.StringProperty(indexed=False)
    desc = ndb.StringProperty(indexed=False)
    Emailid = ndb.StringProperty(indexed=True)
    profile_photo = ndb.BlobProperty()
    subscribe= ndb.StringProperty(repeated=True)

list_cat = ['Food','Books','Clothes','Furniture','Household','Electronics', 'Clear all']
for c in list_cat:
    cat = Categories();
    cat.cat_name = c
    cat.put()

class Post(ndb.Model):
    Category = ndb.StringProperty(indexed=False)
    item_name = ndb.StringProperty(indexed=False)
    receiver_id = ndb.StringProperty(indexed=False)
    item_location = ndb.StringProperty(indexed=False)
    item_photo = ndb.BlobProperty()

class MainPage(webapp2.RequestHandler):
	def get(self):
		values = {}
		template = JINJA_ENVIRONMENT.get_template('base.html')
		self.response.write(template.render(values))

class Signup(webapp2.RequestHandler):
    def get(self):    	
        if self.request.get('invalid') and self.request.get('invalid') == '1' : 
        	invalid=1
        	EmailId=self.request.get('Emailid')
        else:
        	invalid=0
        	EmailId=''
        values = {'invalid':invalid,'EmailId':EmailId}
        # Write the submission form and the footer of the page
        template = JINJA_ENVIRONMENT.get_template('signup.html')

        self.response.write(template.render(values))

class signupNext(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        CheckExisting = User.query(User.Emailid == self.request.get('user_email')).fetch()
        USER_EMAIL = self.request.get('user_email')
        #self.response.write(CheckExisting)
        if CheckExisting ==  []:
            current_user = User(parent=guestbook_key('default_user'))
            current_user.Firstname = self.request.get('user_name').split()[0] +' ' + self.request.get('user_name').split()[1]
            current_user.Emailid = self.request.get('user_email')
        """
	        current_user.Firstname = self.request.get('user_firstname')
	        current_user.address = self.request.get('user_address')
	        current_user.contact_no = self.request.get('user_contact')
	        current_user.Lastname = self.request.get('user_lastname')
	        current_user.Emailid = self.request.get('user_emailid')
	        current_user.Password = self.request.get('user_password')"""

        """ Users_query = User.query(
	            ancestor=guestbook_key('default_user'))
	        Users_query = Users_query.fetch(10)
	        for  users in Users_query:
	            self.response.write("<p>"+ users.Firstname + " " + users.Lastname+  " " + users.address + " " + users.contact_no + " " + users.Password +"</p>")

        else:
        	self.response.write(CheckExisting)
        	self.redirect('/signup?invalid=1&Emailid='+self.request.get('user_emailid'))"""
        user1 = User.query(User.Emailid == self.request.get('user_email')).fetch()[0]
        if user1.desc == 'None':
        	user1.desc = ''
        if user1.address == 'None':
        	user1.address = ''
        if user1.contact_no == 'None':
        	user1.contact_no = ''
        #list_cat = ['Food','Books','Clothes','Furniture','Household','Electronics']
        values={'Firstname': user1.Firstname, 'Address': user1.address, 'Contact':user1.contact_no, 'Description':user1.desc, 'image_url':user1.key.urlsafe(), 'user_email':user1.Emailid, 'list' :list_cat, 'user_list':user1.subscribe}
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(values=values))

    def get(self):
    	user1 = User.query(User.Emailid == self.request.get('user_email')).fetch()[0]
     	values={'Firstname': user1.Firstname, 'Address': user1.address, 'Contact':user1.contact_no, 'Description':user1.desc, 'image_url':user1.key.urlsafe(),'user_email':user1.Emailid, 'list' :list_cat, 'user_list':user1.subscribe}
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(values=values))


class verify(webapp2.RequestHandler):
	def get(self):
		values={}
		template = JINJA_ENVIRONMENT.get_template('google2480455ad030cc62.html')
		self.response.write(template.render(values))
class logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))
class update(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        user1 = User.query(User.Emailid == self.request.get('user_email')).fetch()[0]
        first = self.request.get('Firstname')
        email = self.request.get('user_email')
        self.response.write('<p>'+email+'</p>')
        add = self.request.get('Address')
        cont = self.request.get('Contact')
        des = self.request.get('Description')
        subs = self.request.get_all('subscribe')
        flag=0
        clear=0
        profile_photo = self.request.get('img')
        if profile_photo:
            profile_photo = images.resize(profile_photo, 200 ,200)
            user1.profile_photo = profile_photo
            flag=1
        if first and user1.Firstname != first:
            user1.Firstname = first
            flag = 1
        if add and user1.address != add:
            user1.address = add
            flag = 1
        if cont and user1.contact_no != cont:
            user1.contact_no = cont
            flag = 1
        if user1.desc != des:
            user1.desc = des
            flag = 1
        if subs:
            for s in subs:
                if(s=='Clear all'):
                    clear=1
                    break
                user1.subscribe.append(s)
                cat =  Categories.query(Categories.cat_name == s).fetch()[0]
                cat.cat_users.append(email)
                cat.put()
            if clear:
                for s in user1.subscribe:
                    cat =  Categories.query(Categories.cat_name == s).fetch()[0]
                    if email in cat.cat_users:
                        cat.cat_users.pop(cat.cat_users.index(email))
                        cat.put()
                user1.subscribe=[]

            flag=1
        if flag == 1 : 
        	user1.put()
        self.redirect('/signupNext?user_email='+ email)

class Image(webapp2.RequestHandler):
	def get(self):
		user_key = ndb.Key(urlsafe=self.request.get('img_id'))
		user = user_key.get()
		if  user.profile_photo: 
		    self.response.headers['Content-Type'] = 'image/png'
		    self.response.out.write(user.profile_photo)
		else:
			self.response.out.write('No Image')

class ImageItem(webapp2.RequestHandler):
    def get(self):
        post_key = ndb.key(urlsafe=self.request.get('image'))
        post = post_key.get()
        if post.item_photo:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(post.item_photo)
        else:
            self.response.out.write('No Image')

class postItem(webapp2.RequestHandler):
    def get(self):
        user1 = User.query(User.Emailid == self.request.get('user_email')).fetch()[0]
        values = { 'list' :list_cat[:-1],'Emailid':self.request.get('user_email')}
        template = JINJA_ENVIRONMENT.get_template('post.html')
        self.response.write(template.render(values=values))

class Category(webapp2.RequestHandler):
    def post(self):
        user1 = User.query(User.Emailid == self.request.get('Emailid')).fetch()[0] 
        current_post = Post(parent=user1.key)
        current_post.Category = self.request.get('Category')
        current_post.item_name = self.request.get('item_name')
        current_post.receiver_id = ''
        current_post.item_location = self.request.get('item_address')
        item_photo = self.request.get('image')
        current_post.item_photo = images.resize(item_photo,200,200)
        current_post.put()
        self.response.headers['Content-Type'] = 'image/png'

app = webapp2.WSGIApplication([	
	('/',MainPage),
    ('/signup', Signup),
    ('/signupNext', signupNext),
    ('/google2480455ad030cc62.html',verify),
    ('/logout',logout),
    ('/update',update),
    ('/img',Image),
    ('/post',postItem),
    ('/category',Category),
    ('/image',ImageItem),
], debug=True)
