from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import db, Episode, Guest, Appearance

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lateshow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/episodes', methods=['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return jsonify([{
        'id': episode.id,
        'date': episode.date,
        'number': episode.number
    } for episode in episodes]), 200

@app.route('/episodes/<int:episode_id>', methods=['GET'])
def get_episode(episode_id):
    episode = Episode.query.get(episode_id)
    if episode:
        return jsonify({
            'id': episode.id,
            'date': episode.date,
            'number': episode.number,
            'appearances': [{
                'id': appearance.id,
                'rating': appearance.rating,
                'guest_id': appearance.guest_id,
                'episode_id': appearance.episode_id,
                'guest': {
                    'id': appearance.guest.id,
                    'name': appearance.guest.name,
                    'occupation': appearance.guest.occupation
                }
            } for appearance in episode.appearances]
        }), 200
    return jsonify({'error': 'Episode not found'}), 404

@app.route('/guests', methods=['GET'])
def get_guests():
    guests = Guest.query.all()
    return jsonify([{
        'id': guest.id,
        'name': guest.name,
        'occupation': guest.occupation
    } for guest in guests]), 200

@app.route('/appearances', methods=['POST'])
def create_appearance():
    data = request.get_json()
    try:
        Appearance.validate_rating(data['rating'])

        new_appearance = Appearance(
            rating=data['rating'],
            guest_id=data['guest_id'],
            episode_id=data['episode_id']
        )
        db.session.add(new_appearance)
        db.session.commit()

        appearance_data = {
            'id': new_appearance.id,
            'rating': new_appearance.rating,
            'guest_id': new_appearance.guest_id,
            'episode_id': new_appearance.episode_id,
            'episode': {
                'id': new_appearance.episode.id,
                'date': new_appearance.episode.date,
                'number': new_appearance.episode.number
            },
            'guest': {
                'id': new_appearance.guest.id,
                'name': new_appearance.guest.name,
                'occupation': new_appearance.guest.occupation
            }
        }
        return jsonify(appearance_data), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
if __name__ == '__main__':
    app.run(debug=True)


