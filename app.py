from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///list.db'
db = SQLAlchemy(app)

# Table Player
class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    contract_duration = db.Column(db.Integer)
    
    def json(self):
        return {'id': self.id, 'name': self.name, 'position': self.position, 'club_id': self.club_id, 'contract_duration': self.contract_duration}

# Table Club
class Club(db.Model):
    __tablename__ = 'club'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))

    def json(self):
        return {'id': self.id, 'name': self.name, 'country': self.country}

@app.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        data = request.form
        new_player = Player(name=data['name'], position=data.get('position'), club_id=data['club_id'], contract_duration=data.get('contract_duration'))
        db.session.add(new_player)
        db.session.commit()
        return redirect(url_for('players'))
    players = Player.query.all()
    return render_template('player.html', players=players)

@app.route('/players/<int:player_id>', methods=['GET', 'POST'])
def player(player_id):
    player = Player.query.get_or_404(player_id)
    
    if request.method == 'POST':
        data = request.form
        player.name = data.get('name', player.name)
        player.position = data.get('position', player.position)
        new_club_id = data.get('club_id', player.club_id)
        player.contract_duration = data.get('contract_duration', player.contract_duration)

        club = Club.query.get(new_club_id)
        if not club:
            return jsonify({'error': 'Club does not exist'}), 400
        
        player.club_id = new_club_id
        db.session.commit()
        return redirect(url_for('players'))
    return render_template('edit_player.html', player=player)

@app.route('/players/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('players'))

@app.route('/clubs', methods=['GET', 'POST'])
def clubs():
    if request.method == 'POST':
        data = request.form
        new_club = Club(name=data['name'], country=data['country'])
        db.session.add(new_club)
        db.session.commit()
        return redirect(url_for('clubs'))
    clubs = Club.query.all()
    return render_template('club.html', clubs=clubs)

@app.route('/clubs/<int:club_id>', methods=['GET', 'POST'])
def club(club_id):
    club = Club.query.get_or_404(club_id)
    
    if request.method == 'POST':
        data = request.form
        club.name = data.get('name', club.name)
        club.country = data.get('country', club.country)
        db.session.commit()
        return redirect(url_for('clubs'))
    return render_template('edit_club.html', club=club)

@app.route('/clubs/delete/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    return redirect(url_for('clubs'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
