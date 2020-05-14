#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from datetime import datetime
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
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

    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(50)))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship(
        'Show', backref='venue', cascade='all,delete,delete-orphan')

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artist')


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id', ondelete='CASCADE'),
        nullable=False
    )
    venue_id = db.Column(
        db.Integer,
        db.ForeignKey('Venue.id', ondelete='CASCADE'),
        nullable=False
    )

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


#----------------------------------------------------------------------------#
# Helper functions.
#----------------------------------------------------------------------------#

def get_past_or_future_shows(shows, is_future):
    if is_future:
        return_shows = [
            show for show in shows if date_is_in_future(show.start_time)
        ]
    else:
        return_shows = [
            show for show in shows if not date_is_in_future(show.start_time)
        ]

    return return_shows


def date_is_in_future(date):
    return date > datetime.utcnow()


def convert_datetime_to_string(datetime_obj):
    return datetime.strftime(datetime_obj, '%Y-%m-%dT%H:%M:%S.%fZ')


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

    city_states = db.session.query(Venue.city, Venue.state).distinct().all()
    for city_state_pair in city_states:
        matching_venues = Venue.query.filter(
            Venue.city == city_state_pair[0], Venue.state == city_state_pair[1]
        ).all()

        city_data = {
            'city': city_state_pair[0],
            'state': city_state_pair[1],
            'venues': [{
                'id': x.id,
                'name': x.name,
                'num_upcoming_shows': len(x.shows)
            } for x in matching_venues]
        }
        data.append(city_data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    matches = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(matches),
        "data": [{
            "id": x.id,
            "name": x.name,
            "num_upcoming_shows": len(x.shows)
        } for x in matches]
    }

    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.get(venue_id)

    if not venue:
        return abort(404)

    future_shows = get_past_or_future_shows(venue.shows, is_future=True)
    past_shows = get_past_or_future_shows(venue.shows, is_future=False)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [{
            "artist_id": x.artist_id,
            "artist_name": x.artist.name,
            "artist_image_link": x.artist.image_link,
            "start_time": convert_datetime_to_string(x.start_time)
        } for x in past_shows],
        "upcoming_shows": [{
            "artist_id": x.artist_id,
            "artist_name": x.artist.name,
            "artist_image_link": x.artist.image_link,
            "start_time": convert_datetime_to_string(x.start_time)
        } for x in future_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(future_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)
    if form.validate():
        name = form.name.data
        venue = Venue(
            name=name,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website.data,
            image_link=form.image_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        try:
            db.session.add(venue)
            db.session.commit()

            # on successful db insert, flash success
            flash(f'Venue {name} was successfully listed!')
        except:
            db.session.rollback()

            # on failed db insert, flash error
            logging.exception(f'Unable to create venue {name}')
            flash(f'An error occured. Venue {name} could not be listed.')
        finally:
            db.session.close()
    else:
        logging.error(form.errors)
        flash(f'An error occured. Venue could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
    except:
        error = True
        logging.exception('Could not delete venue')
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'ERROR'}), 500

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

    artists = Artist.query.all()
    data = [{
        "id": x.id,
        "name": x.name
    } for x in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    matches = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')
    ).all()
    response = {
        "count": len(matches),
        "data": [{
            "id": x.id,
            "name": x.name,
            "num_upcoming_shows": len(x.shows)
        } for x in matches]
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist = Artist.query.get(artist_id)
    if not artist:
        return abort(404)

    future_shows = get_past_or_future_shows(artist.shows, is_future=True)
    past_shows = get_past_or_future_shows(artist.shows, is_future=False)

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
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": x.venue_id,
            "venue_name": x.venue.name,
            "venue_image_link": x.venue.image_link,
            "start_time": convert_datetime_to_string(x.start_time)
        } for x in past_shows],
        "upcoming_shows": [{
            "venue_id": x.venue_id,
            "venue_name": x.venue.name,
            "venue_image_link": x.venue.image_link,
            "start_time": convert_datetime_to_string(x.start_time)
        } for x in future_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(future_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    if form.validate():
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.image_link = form.image_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        try:
            db.session.commit()
            flash('Artist details updated successfully')
        except:
            db.session.rollback()
            flash('Artist details were not able to be updated', 'error')
        finally:
            db.session.close()

    else:
        logging.error(form.errors)
        flash('Could not edit artist details')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    if form.validate():
        venue = Venue.query.get(venue_id)

        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        try:
            db.session.commit()
            flash(f'Venue updated successfully')
        except:
            db.session.rollback()
        finally:
            db.session.close()

    else:
        logging.error(form.errors)
        flash(f'Venue could not be updated.', 'error')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm(request.form)

    validation_success = form.validate()
    if validation_success:
        name = form.name.data
        artist = Artist(
            name=name,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website.data,
            image_link=form.image_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )

        try:
            db.session.add(artist)
            db.session.commit()

            # on successful db insert, flash success
            flash(f'Artist {artist.name} was successfully listed!')
        except Exception:
            db.session.rollback()

            logging.exception(f'Unable to create artist {name}')

            # on failure, flash error
            flash(f'Artist {name} could not be listed.', 'error')
        finally:
            db.session.close()
    else:
        logging.error(form.errors)

        # on failure, flash error
        flash(f'Artist could not be listed.', 'error')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = Show.query.all()
    data = [{
        'venue_id': x.venue_id,
        'venue_name': x.venue.name,
        'artist_id': x.artist_id,
        'artist_name': x.artist.name,
        'artist_image_link': x.artist.image_link,
        'start_time': convert_datetime_to_string(x.start_time)
    } for x in shows]

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)

    if form.validate():
        try:
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(new_show)
            db.session.commit()

            # on successful db insert, flash success
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            # on successful db insert, flash error
            flash('An error occured. Show could not be listed.', 'error')
        finally:
            db.session.close()
    else:
        logging.error(form.errors)
        # on form validation error, flash error
        flash('An error occured. Show could not be listed.', 'error')

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
