import os
from flask import Flask, render_template, request, Response
from dotenv import load_dotenv
import folium
from peewee import *
import datetime
from playhouse.shortcuts import model_to_dict
from data import landing_data

load_dotenv()
app = Flask(__name__)

mydb = None
if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
              user=os.getenv("MYSQL_USER"),
              password=os.getenv("MYSQL_PASSWORD"),
              host=os.getenv("MYSQL_HOST"),
              port=3306)
print(mydb)

# Build ORM model for timeline post.
class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb

mydb.connect()
mydb.create_tables([TimelinePost])

hobbyImageDir = os.path.join('img')
img = os.path.join('static', 'img')

# Build interactive map.
def build_map():
    my_map = folium.Map()

    for p in landing_data['places']:
        folium.Marker(p["coord"], popup = p["name"], icon=folium.Icon(icon="circle", prefix="fa")).add_to(my_map)

    my_map = my_map._repr_html_()
    return my_map

# Home page.
@app.route('/')
def index():
    my_map = build_map()
    intro_message = "Welcome to our page!"
    map_title = "A map of all the places that we have been to:"
    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"), landing_data=landing_data, intro_message=intro_message, my_map=my_map, map_title=map_title)

# About page.
@app.route('/about')
def fellowPage():
    return render_template('aboutMePage.html', name=landing_data["name"], img=landing_data['img'], about_me=landing_data['about_me'])

# Experience page.
@app.route('/experience')
def experiencePage():
    return render_template('experiencePage.html', name=landing_data['name'], experiences=landing_data['experiences'])

# Hobbies page.
@app.route('/hobbies')
def hobbiesPage():
    return render_template('hobbiesPage.html', hobbies=landing_data["hobbies"])

# Education page.
@app.route('/education')
def education():
    return render_template('education.html', education=landing_data["education"])

# Timeline page POST endpoint.
@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    keys = request.form.keys()

    if "name" not in keys:
        return Response("Invalid name", status=400)
    name = request.form['name']
    if not name:
        return Response("Invalid name", status=400)

    if "email" not in keys:
        return Response("Invalid email", status=400)
    email = request.form['email']
    if not email or email.count("@") != 1:
        return Response("Invalid email",status=400)
    
    if "content" not in keys:
        return Response("Invalid content", status=400)
    content = request.form['content']
    if not content:
        return Response("Invalid content", status=400)
    
    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return model_to_dict(timeline_post)

# Timeline page GET endpoint.
@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }

# Timeline page.
@app.route('/timeline')
def timeline():
    timeline_posts = get_time_line_post()['timeline_posts']
    return render_template('timeline.html', title="Timeline", timeline_posts=timeline_posts)

# `read-form` endpoint
@app.route('/read-form', methods=['POST'])
def read_form():
    # Get the form data as Python ImmutableDict datatype
    # data = request.form

    # Send the form input to the database
    post_time_line_post()

    # Update timeline page
    return timeline()
