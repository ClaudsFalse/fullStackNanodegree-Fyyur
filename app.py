#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from sqlalchemy import literal
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import  db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)
db.init_app(app)
#-----------------------------#
# Create tables in the db from models
#-----------------------------#

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

  # query all tables and filter by show occurring previous than today's date, to get data for past shows
  # individual venue query to show venues with no shows
  venue = Venue.query.get_or_404(venue_id)

  # this will run only if there are shows assigned to the venue 
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': str(show.start_time)
        }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
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
  # set the FlaskForm 
  form = VenueForm(request.form, meta={'csrf': False})

  # validate the fields
  if form.validate():

    # prepare for transaction with try/catch block 
    try:
      new_venue = Venue(name=form.name.data, 
                  city = form.city.data, 
                  state = form.state.data,
                  address = form.address.data,
                  phone = form.phone.data,
                  genres = form.genres.data,
                  facebook_link = form.facebook_link.data,
                  image_link = form.image_link.data,
                  website = form.website_link.data,
                  # the following will return y rather than True (or False) so casting the value to needed boolean
                  seeking_talent = True if 'seeking_talent' in request.form else False,
                  seeking_description = request.form['seeking_description']
                  )
      print(form.genres.data)
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + form.name.data + ' was created successfully ⭐')
    except ValueError as e:
      print(e)
      db.session.rollback()
      print(sys.exc_info())
      print(sys.exc_info())
    finally:
      db.session.close()

  # if there are errors in the form and could not be validated     
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + "|".join(err))
    flash('🛑 Errors' + str(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')
    
  
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
  
  for result in results:
    num_upcoming_shows = 0
    upcoming_shows = Show.query.filter_by(artist_id=result.id).all()
    for show in upcoming_shows:
      if show.start_time >= datetime.now():
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
  artist = Artist.query.get_or_404(artist_id)
  upcoming_shows = []
  past_shows = []
  data = vars(artist)

  for show in artist.shows: 
    print("venues", show.venue.genres)
    print("artist", show.artist.genres)

  for show in joined_query_all_shows:
    shows_dic = {
      "venue_id":show.venue.id,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    # assign upcoming shows to variable
    if show.start_time >= datetime.now():
      upcoming_shows.append(shows_dic)
    else:
      past_shows.append(shows_dic)

  data["past_shows"] = past_shows    
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_shows)
  data["upcoming_shows_count"] = len(upcoming_shows)

  print(data["genres"])
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
  form = ArtistForm(request.form, meta={'csrf': False})

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # set the FlaskForm 
  form = ArtistForm(request.form, meta={'csrf': False})

  # validate the fields
  if form.validate():

    # prepare for transaction with try/catch block 
    try:
      new_artist = Artist(name=form.name.data, 
                  city = form.city.data, 
                  state = form.state.data,
                  phone = form.phone.data,
                  genres = form.genres.data,
                  facebook_link = form.facebook_link.data,
                  image_link = form.image_link.data,
                  website = form.website_link.data,
                  # the following will return y rather than True (or False) so casting the value to needed boolean
                  seeking_venue = True if 'seeking_venue' in request.form else False,
                  seeking_description = request.form['seeking_description']
                  )
      print(form.genres.data)
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' successfuly created ⭐')
    except ValueError as e:
      print(e)
      db.session.rollback()
      print(sys.exc_info())
      print(sys.exc_info())
    finally:
      db.session.close()

  # if there are errors in the form and could not be validated     
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + "|".join(err))
    flash('🛑 Errors:' + str(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html')
  

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
        "start_time": str(show.start_time)
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
    start_time = form.start_time.data
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
