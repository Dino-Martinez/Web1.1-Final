from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/userDatabase"
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/databaseName') + "?retryWrites=false"
app.config["MONGO_URI"] = host
mongo = PyMongo(app)


@app.route('/')
def home():
    """Renders our home page template"""
    return render_template('home.html')


@app.route('/artists', methods=["GET", "POST"])
def artists():
    """Displays all of our artists with the ability to favorite them"""

    if request.method == "POST":
        # add new artist to database
        new_artist = {
            'name': request.form.get('name'),
            'alias': request.form.get('alias')
        }

        mongo.db.artists.insert_one(new_artist)
        return redirect(url_for('artists'))
    else:
        artists = list(mongo.db.artists.find({}))
        context = {
            'artists': artists
        }

        return render_template('artists.html', **context)


@app.route('/artists/<artist_id>', methods=["GET", "POST"])
def artist(artist_id):
    """Displays info about a single artist"""
    if request.method == "POST":
        # add album to artist
        new_album = {
            'title': request.form.get('title'),
            'release_date': request.form.get('release-date'),
            'genre': request.form.get('genre'),
            'artist_id': artist_id
        }

        mongo.db.albums.insert_one(new_album)
        return redirect(url_for('artist', artist_id=artist_id))
    else:
        artist = mongo.db.artists.find_one({"_id": ObjectId(artist_id)})
        albums = list(mongo.db.albums.find({"artist_id": artist_id}))
        context = {
            'artist': artist,
            'albums': albums
        }

        return render_template('one_artist.html', **context)


@app.route('/remove_album/<album_id>')
def remove_album(album_id):
    album = mongo.db.albums.find_one({'_id': ObjectId(album_id)})
    artist_id = album["artist_id"]
    mongo.db.albums.delete_one({'_id': ObjectId(album_id)})

    return redirect(url_for('artist', artist_id=artist_id))


@app.route('/remove_artist')
def list_artists_to_remove():
    """Display list of artists the user can remove.
       I added this intermediary page because removing an artist will also
       remove all of their albums, so I wanted to make it a two step process
       to avoid accidental deletions"""
    artists = mongo.db.artists.find({})
    context = {
        'artists': artists
    }
    return render_template('remove_artist.html', **context)


@app.route('/remove_artist/<artist_id>')
def remove_artist(artist_id):
    """Remove artist from our database, and all albums that they made"""
    mongo.db.artists.delete_one({"_id": ObjectId(artist_id)})
    mongo.db.albums.delete_many({"artist_id": artist_id})
    return redirect(url_for('artists'))


@app.route('/update_artist/<artist_id>', methods=["GET", "POST"])
def update_artist(artist_id):
    if request.method == 'POST':
        artist = {
            'name': request.form.get("name"),
            'alias': request.form.get("alias")
        }
        mongo.db.artists.update_one({"_id": ObjectId(artist_id)},
                                    {"$set": artist})
        return redirect(url_for('artist', artist_id=artist_id))
    else:
        artist = mongo.db.artists.find_one({"_id": ObjectId(artist_id)})

        context = {
            'artist': artist
        }

        print(artist)

        return render_template('update_artist.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
