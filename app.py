from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///list.db'
db = SQLAlchemy(app)

# Tabel Player
class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    contract_duration = db.Column(db.Integer)
    
    def json(self):
        return {'id': self.id, 'name': self.name, 'position': self.position, 'club_id': self.club_id, 'contract_duration': self.contract_duration}

# Tabel Klub
class Club(db.Model):
    __tablename__ = 'club'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))

    def json(self):
        return {'id': self.id, 'name': self.name, 'country': self.country}

@app.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'GET':
        players = Player.query.all()
        return jsonify([player.json() for player in players])
    elif request.method == 'POST':
        data = request.json
        new_player = Player(name=data['name'], position=data.get('position'), club_id=data['club_id'], contract_duration=data.get('contract_duration'))
        db.session.add(new_player)
        db.session.commit()
        return jsonify(new_player.json()), 201

@app.route('/players/<int:player_id>', methods=['GET', 'PUT', 'DELETE'])
def player(player_id):
    player = Player.query.get_or_404(player_id)
    
    if request.method == 'GET':
        return jsonify(player.json())
    elif request.method == 'PUT':
        data = request.json
        player.name = data.get('name', player.name)
        player.position = data.get('position', player.position)
        new_club_id = data.get('club_id', player.club_id)
        player.contract_duration = data.get('contract_duration', player.contract_duration)

        club = Club.query.get(new_club_id)
        if not club:
            return jsonify({'error': 'Club does not exist'}), 400
        
        player.club_id = new_club_id
        db.session.commit()
        return jsonify(player.json())
    elif request.method == 'DELETE':
        db.session.delete(player)
        db.session.commit()
        return jsonify({'message': 'Player deleted'})

@app.route('/clubs', methods=['GET', 'POST'])
def clubs():
    if request.method == 'GET':
        clubs = Club.query.all()
        return jsonify([club.json() for club in clubs])
    elif request.method == 'POST':
        data = request.json
        new_club = Club(name=data['name'], country=data['country'])
        db.session.add(new_club)
        db.session.commit()
        return jsonify(new_club.json()), 201

@app.route('/clubs/<int:club_id>', methods=['GET', 'PUT', 'DELETE'])
def club(club_id):
    club = Club.query.get_or_404(club_id)
    
    if request.method == 'GET':
        return jsonify(club.json())
    elif request.method == 'PUT':
        data = request.json
        club.name = data.get('name', club.name)
        club.country = data.get('country', club.country)
        db.session.commit()
        return jsonify(club.json())
    elif request.method == 'DELETE':
        db.session.delete(club)
        db.session.commit()
        return jsonify({'message': 'Club deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
