import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

##### security methods
secret = 'fart'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

		
##### Common Methods
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

## Main Class, show all posts 
class MainPage(BlogHandler):
  def get(self):
      posts = greetings = Post.all().order('-created')
      self.render('front.html', posts=posts)


## DB Classes 	
class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
			
class Likes(db.Model):
    user = db.IntegerProperty(required=True)

class Comment(db.Model):
    author = db.ReferenceProperty(User, required=True)
    content = db.TextProperty(required=True)
	
	
## Blog Actions  
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    creator = db.IntegerProperty(required=True) 
    last_modified = db.DateTimeProperty(auto_now = True)

    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class NewPost(BlogHandler):
    def render_new(self, subject='', content='', error=''):
        self.render('new-post.html',
            subject=subject,
            content=content,
            error=error)

    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')
        creator = self.user.key().id()
        
        if subject and content:
            p = Post(subject = subject, content = content,creator=creator)
            p.put()
            path = '/' + str(p.key().id())
            self.redirect(path)
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


class PostPage(BlogHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        comments = Comment.all().ancestor(post)
        if not post:
            self.error(404)
            return
        if self.user:
            user_id = self.user.key().id()
            if Likes.all().ancestor(post).filter('user =', user_id).get():
                vote = 'unlike'
            else:
                vote = 'like'
            self.render('post.html', p=post, vote=vote, comments=comments)
        else:
            self.render('post.html', p=post, comments=comments)
    
    def post(self, id):
        if not self.user:
            return self.redirect('/login')

        post = Post.get_by_id(int(id))
        user_id = self.user.key().id()
        if user_id == post.creator:
            self.write('You are not allowed to like your own post!')
        else:
            l = Likes.all().ancestor(post).filter('user =', user_id).get()
            if l:
                l.delete()
            else:
                like = Likes(parent=post, user=user_id)
                like.put()
            self.redirect('/%s' % id)


class DeletePost(BlogHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        if not self.user:
            self.redirect("/login")
        elif not self.user.key().id() == post.creator:
            self.write('You are not allowed to delete this post')
        else:
            if (not self.user) or (not self.user.key().id() == post.creator):
                return self.redirect('/login')
            post.delete()
            self.write('Post deleted. <a href="/">Press Here to Go Back to the Home Page</a>')


class EditPost(BlogHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        if not self.user:
            self.redirect("/login")
        elif not self.user.key().id() == post.creator:
            self.write('You are not allowed to edit this post!')
        else:
            subject = post.subject
            content = post.content
            self.render(
                'newpost.html',
                subject=subject,
                content=content,
                post_id=id,
                edit=True)

    def post(self, id):
        post = Post.get_by_id(int(id))
        if (not self.user) or (not self.user.key().id() == post.creator):
            return self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post.get_by_id(int(id))
            p.subject = subject
            p.content = content
            p.put()
            self.redirect('/%s' % id)
        else:
            error = 'Please, enter both a subject and some content!'
            self.render(
                'new-post.html',
                subject=subject,
                content=content,
                error=error,
                id=id,
                edit=True)


class AddComment(BlogHandler):
    def get(self, post_id):
        if not self.user:
            self.redirect("/login")
        else:
            self.render('comment.html')

    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        content = self.request.get('content')

        if content:
            comment = Comment(
                parent=Post.get_by_id(int(post_id)),
                content=content,
                author=self.user)
            comment.put()
            self.redirect('/%s' % post_id)
        else:
            error = 'Please, enter some content!'
            self.render(
                'comment.html',
                content=content,
                error=error)


class EditComment(AddComment):
    def get(self, post_id, id):
        comment = Comment.get_by_id(int(id), Post.get_by_id(int(post_id)))
        if not self.user:
            self.redirect("/login")
        elif not self.user.key() == comment.author.key():
            self.write('You are not allowed to edit this comment')
        else:
            content = comment.content
            self.render(
                'comment.html',
                content=content,
                edit=True,
                post_id=post_id)

    def post(self, post_id, id):
        comment = Comment.get_by_id(int(id), Post.get_by_id(int(post_id)))
        if (not self.user) or (not self.user.key() == comment.author.key()):
            return self.redirect('/login')

        content = self.request.get('content')

        if content:
            c = Comment.get_by_id(int(id), Post.get_by_id(int(post_id)))
            c.content = content
            c.put()
            self.redirect('/%s' % post_id)
        else:
            error = 'Please, enter some content!'
            self.render(
                'comment.html',
                content=content,
                error=error,
                edit=True,
                post_id=post_id)


class DeleteComment(BlogHandler):
    def get(self, post_id, id):
        comment = Comment.get_by_id(int(id), Post.get_by_id(int(post_id)))
        if not self.user:
            self.redirect("/login")
        elif not self.user.key() == comment.author.key():
            self.write('You are not allowed to delete this comment')
        else:
            if (not self.user) or (not self.user.key() == comment.author.key()):
                return self.redirect('/')
            comment.delete()
            self.redirect('/%s' % post_id)


class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/([0-9]+)', PostPage),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/newpost', NewPost),
                               ('/([0-9]+)/delete', DeletePost),
                               ('/([0-9]+)/edit', EditPost),
                               ('/([0-9]+)/comment', AddComment),
                               ('/([0-9]+)/comment/([0-9]+)/edit', EditComment),
                               ('/([0-9]+)/comment/([0-9]+)/delete', DeleteComment) 
                               ],
                              debug=True)
