#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    website_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), default=[])
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120), default='')
    website_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String(500), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    venue_state_and_city = ''
    data = []

    for venue in venues:
        upcoming_shows = venue.shows.filter(
            Show.start_time > current_time).all()
        if venue_state_and_city == venue.city + venue.state:
            data[len(data) - 1]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
            })
        else:
            venue_state_and_city == venue.city + venue.state
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(upcoming_shows)
                }]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(result),
        "data": result
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_description = ''
    seeking_talent = False
    if 'seeking_venue' in request.form:
        seeking_talent = request.form['seeking_talent'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']
    venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        image_link=image_link,
        genres=genres,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description
    )
    try:
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    deleted = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')
        deleted = True
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
        deleted = False
    finally:
        db.session.close()
    if deleted:
        return redirect(url_for('index'))
    else:
        return None


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(artists),
        "data": artists
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website_link
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.genres.data = artist.genres
        form.image_link.data = artist.image_link
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_venue = False
    seeking_description = ''
    if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

    try:
        artist = Artist.query.get(artist_id)
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.image_link = image_link
        artist.genres = genres
        artist.facebook_link = facebook_link
        artist.website_link = website_link
        artist.seeking_venue = seeking_venue
        artist.seeking_description = seeking_description
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_description = ''
    seeking_talent = False
    if 'seeking_venue' in request.form:
        seeking_talent = request.form['seeking_talent'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state = state
    venue.phone = phone
    venue.image_link = image_link
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.website_link = website_link
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    venue.address = address

    try:
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_venue = False
    seeking_description = ''
    if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']

    artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        image_link=image_link,
        genres=genres,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description
    )

    try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    print(error)
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    print(error)
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
