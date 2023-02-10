#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import literal
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy.exc import SQLAlchemyError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#-----------------------------#
# Create tables in the db from models
#-----------------------------#
from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')

def venues():
  data = []

  # create a data structure to hold the venues data 
  # so that data is a list of dictionaries, that lets us group the data by city, 
  # and the key "venues" is associated 
  # to a dicitonary as its values. 
  for city in Venue.query.distinct(Venue.city).order_by(Venue.city).all():
    cities_dic = {}
    cities_dic["city"] = city.city
    cities_dic["state"] = city.state
    cities_dic["venues"] = []
    data.append(cities_dic)

  # populate the venues list for each city 
  venues = [venue for venue in Venue.query.all()]
  for venue in venues:
    for sub in data:
      if sub["city"] == venue.city:
        sub_dic = {}
        sub_dic["id"] = venue.id
        sub_dic["name"] = venue.name
        sub_dic["num_upcoming_shows"] = venue.num_upcoming_shows
        sub["venues"].append(sub_dic)
   
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  response = {}
  data = []
  search_term = request.form.get('search_term', '')
  results = [venue for venue in Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()]
  for result in results:
    res_dic = {}
    res_dic["id"] = result.id
    res_dic["name"] = result.name
    res_dic["num_upcoming_shows"] = result.num_upcoming_shows
    data.append(res_dic)
    
  response["count"] = len(results)
  response["data"] = data

  # search our database for records containing the search term 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # creating data dictionary extracting from database
  past_shows = []
  upcoming_shows = []
  future_shows_count = 0
  past_shows_count = 0
  data = {}
  # query all tables and filter by show occurring previous than today's date, to get data for past shows
  joined_query_all_shows=db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()

  # individual venue query to show venues with no shows
  venue = Venue.query.get(venue_id)

  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue.genres
  data['address']= venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link

  # this will run only if there are shows assigned to the venue 
  for show in joined_query_all_shows:
    shows_dic = {
    "artist_id" : show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.starting_time)
    }
    
    # check if the shows are future or due to happen today 
    if show.starting_time >= datetime.now():
      future_shows_count += 1
      upcoming_shows.append(shows_dic)
      data["upcoming_shows"] = upcoming_shows

    # else it means the shows are in the past
    else:
      past_shows_count += 1
      past_shows.append(shows_dic)
      data["past_shows"] = past_shows
  
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = future_shows_count
  print(data)
  ## handle error if no venue is returned. 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form, meta={'csrf': False})
  

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate_on_submit():
    new_venue = Venue(name=request.form['name'], 
                  city = request.form['city'], 
                  state = request.form['state'],
                  address = request.form['address'],
                  phone = request.form['phone'],
                  genres = request.form['genres'],
                  facebook_link = request.form['facebook_link'],
                  image_link = request.form['image_link'],
                  website = request.form['website_link'],
                  # the following will return y rather than True (or False) so casting the value to needed boolean
                  seeking_talent = True if 'seeking_talent' in request.form else False,
                  seeking_description = request.form['seeking_description']
                  )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' created successfully!')

  else:
    db.session.rollback()
    print(sys.exc_info())
    print(form.errors)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. Please See below for errors')  
    for error in form.errors:
      if error == 'phone':
        flash('You entered an invalid phone number. It should only contain digits')
      if error == 'facebook_link':
        flash('You entered an invalid facebook link')
      if error == 'website_link':
        flash('You entered an invalid website link')
  
  return render_template('pages/home.html', form=form)
  
@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. The venue could not be deleted')
  finally:
      db.session.close()
      
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id":artist.id,
      "name":artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  data = []
  search_term = request.form.get('search_term', '')
  results = [artist for artist in Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()]
  
  # if show.starting_time >= datetime.now()
  for result in results:
    num_upcoming_shows = 0
    upcoming_shows = Show.query.filter_by(artist_id=result.id).all()
    for show in upcoming_shows:
      if show.starting_time >= datetime.now():
        num_upcoming_shows += 1
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows":num_upcoming_shows
    })
   
  response["count"] = len(results)
  response["data"] = data

  # search our database for records containing the search term 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  joined_query_all_shows=db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).all()
  artist = Artist.query.get(artist_id)
  upcoming_shows = []
  past_shows = []
  upcoming_shows_count = 0
  past_shows_count = 0

  data = {
  "id": artist.id,
  "name": artist.name,
  "genres": artist.genres,
  "city": artist.city,
  "state": artist.state,
  "phone": artist.phone,
  "website": artist.website,
  "facebook_link": artist.facebook_link,
  "seeking_venue": artist.seeking_venue,
  "seeking_description": artist.seeking_description,
  "image_link": artist.image_link}

  for show in joined_query_all_shows:
    shows_dic = {
      "venue_id":show.venue.id,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.starting_time)
    }
    # assign upcoming shows to variable
    if show.starting_time >= datetime.now():
      upcoming_shows_count += 1
      upcoming_shows.append(shows_dic)
      data["upcoming_shows"] = upcoming_shows
    else:
      past_shows_count += 1
      past_shows.append(shows_dic)
      data["past_shows"] = past_shows

  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False 
  artist = Artist.query.get(artist_id)
  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()

  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist could not be edited.')
  if not error: 
    flash('Artist was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False 
  venue = Venue.query.get(venue_id)
  
  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()

  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue could not be edited.')
  if not error: 
    flash('Venue was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate_on_submit():
    new_artist = Artist(name=request.form['name'], 
                city = request.form['city'], 
                state = request.form['state'],
                phone = request.form['phone'],
                genres = request.form['genres'],
                facebook_link = request.form['facebook_link'],
                image_link = request.form['image_link'],
                website = request.form['website_link'],
                # the following will return y rather than True (or False) so casting the value to needed boolean
                seeking_venue = True if 'seeking_venue' in request.form else False,
                seeking_description = request.form['seeking_description']
                )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' created successfully!')
  else:
    db.session.rollback()
    print(sys.exc_info())
    print(form.errors)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed. Please See below for errors')  
    for error in form.errors:
      if error == 'phone':
        flash('You entered an invalid phone number. It should only contain digits')
      if error == 'facebook_link':
        flash('You entered an invalid facebook link')
      if error == 'website_link':
        flash('You entered an invalid website link')

  return render_template('pages/home.html', form=form)
#   error = False

#   # obtain the data posted via the form and catch error if any 
#   try:
#     new_artist = Artist(name=request.form['name'], 
#                 city = request.form['city'], 
#                 state = request.form['state'],
#                 phone = request.form['phone'],
#                 genres = request.form['genres'],
#                 facebook_link = request.form['facebook_link'],
#                 image_link = request.form['image_link'],
#                 website = request.form['website_link'],
#                 # the following will return y rather than True (or False) so casting the value to needed boolean
#                 seeking_venue = True if 'seeking_venue' in request.form else False,
#                 seeking_description = request.form['seeking_description']
#                 )
#     db.session.add(new_artist)
#     db.session.commit()
#   except: 
#     error = True
#     db.session.rollback()
#     print(sys.exc_info())
#   finally: 
#     db.session.close()
#   if error:
#     flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
#   if not error: 
#     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
#   return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  joined_query_all_shows=db.session.query(Show).join(Artist, Venue).all()  
  data = []
  for show in joined_query_all_shows:
    data.append(
      {
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.starting_time)
      }
    )

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  # obtain the data posted via the form and catch error if any 
  form = ShowForm()
  try:
    new_show = Show(artist_id = form.artist_id.data,
    venue_id = form.venue_id.data,
    starting_time = form.start_time.data
    )
    db.session.add(new_show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  if not error: 
    flash('Show was successfully listed!')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
