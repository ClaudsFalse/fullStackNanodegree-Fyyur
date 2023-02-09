from app import db
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    num_upcoming_shows = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref="venue", lazy="joined")


    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}>'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue= db.Column(db.Boolean)
    website = db.Column(db.String(500))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artists", lazy="joined")

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # define foreign keys that map to the primary keys in the respective parent tables
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    starting_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Show ID: {self.id}, artist id: {self.artist_id}, venue id: {self.venue_id}>'
