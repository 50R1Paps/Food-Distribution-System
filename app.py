from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_distribution.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Models
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    fingerprint_id = db.Column(db.String(100), unique=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Person {self.first_name} {self.last_name}>'

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20))
    members = db.relationship('Person', backref='family', lazy=True)
    distributions = db.relationship('Distribution', backref='family', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Family {self.family_name}>'

class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    package_type = db.Column(db.String(50), nullable=False)
    distribution_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Distribution {self.id}>'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        family_name = request.form.get('family_name')
        address = request.form.get('address')
        contact_number = request.form.get('contact_number')
        
        # Create new family
        new_family = Family(
            family_name=family_name,
            address=address,
            contact_number=contact_number
        )
        
        try:
            db.session.add(new_family)
            db.session.commit()
            flash('Family registered successfully!', 'success')
            return redirect(url_for('register_member', family_id=new_family.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering family: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/register_member/<int:family_id>', methods=['GET', 'POST'])
def register_member(family_id):
    family = Family.query.get_or_404(family_id)
    
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d')
        fingerprint_id = request.form.get('fingerprint_id')
        
        # Create new person
        new_person = Person(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            fingerprint_id=fingerprint_id,
            family_id=family_id
        )
        
        try:
            db.session.add(new_person)
            db.session.commit()
            flash('Family member registered successfully!', 'success')
            
            # Check if "add another" was clicked
            if 'add_another' in request.form:
                return redirect(url_for('register_member', family_id=family_id))
            else:
                return redirect(url_for('family_details', family_id=family_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering family member: {str(e)}', 'danger')
    
    return render_template('register_member.html', family=family)

@app.route('/family/<int:family_id>')
def family_details(family_id):
    family = Family.query.get_or_404(family_id)
    return render_template('family_details.html', family=family)

@app.route('/distribute', methods=['GET', 'POST'])
def distribute():
    if request.method == 'POST':
        # Get form data
        fingerprint_id = request.form.get('fingerprint_id')
        package_type = request.form.get('package_type')
        notes = request.form.get('notes')
        
        # Find person by fingerprint ID
        person = Person.query.filter_by(fingerprint_id=fingerprint_id).first()
        
        if not person:
            flash('Person not found. Please register first.', 'danger')
            return redirect(url_for('distribute'))
        
        # Check if family has already received a package recently
        recent_distribution = Distribution.query.filter_by(family_id=person.family_id).order_by(Distribution.distribution_date.desc()).first()
        
        if recent_distribution and (datetime.utcnow() - recent_distribution.distribution_date).days < 30:
            flash(f'This family has already received a package on {recent_distribution.distribution_date.strftime("%Y-%m-%d")}', 'warning')
            return render_template('distribute.html', person=person, family=person.family, recent_distribution=recent_distribution)
        
        # Create new distribution record
        new_distribution = Distribution(
            family_id=person.family_id,
            person_id=person.id,
            package_type=package_type,
            notes=notes
        )
        
        try:
            db.session.add(new_distribution)
            db.session.commit()
            flash('Package distributed successfully!', 'success')
            return redirect(url_for('distribution_receipt', distribution_id=new_distribution.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error distributing package: {str(e)}', 'danger')
    
    return render_template('distribute.html')

@app.route('/distribution/<int:distribution_id>')
def distribution_receipt(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    return render_template('receipt.html', distribution=distribution)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        
        # Search for families
        families = Family.query.filter(Family.family_name.ilike(f'%{search_term}%')).all()
        
        # Search for persons
        persons = Person.query.filter(
            (Person.first_name.ilike(f'%{search_term}%')) | 
            (Person.last_name.ilike(f'%{search_term}%'))
        ).all()
        
        return render_template('search_results.html', families=families, persons=persons, search_term=search_term)
    
    return render_template('search.html')

@app.route('/api/verify_fingerprint', methods=['POST'])
def verify_fingerprint():
    data = request.get_json()
    fingerprint_id = data.get('fingerprint_id')
    
    person = Person.query.filter_by(fingerprint_id=fingerprint_id).first()
    
    if person:
        return jsonify({
            'found': True,
            'person': {
                'id': person.id,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'family_id': person.family_id
            }
        })
    else:
        return jsonify({'found': False})

@app.route('/export_data')
def export_data():
    # Export all data to JSON files for offline use
    families = Family.query.all()
    persons = Person.query.all()
    distributions = Distribution.query.all()
    
    families_data = [{
        'id': f.id,
        'family_name': f.family_name,
        'address': f.address,
        'contact_number': f.contact_number,
        'created_at': f.created_at.isoformat()
    } for f in families]
    
    persons_data = [{
        'id': p.id,
        'first_name': p.first_name,
        'last_name': p.last_name,
        'date_of_birth': p.date_of_birth.isoformat(),
        'fingerprint_id': p.fingerprint_id,
        'family_id': p.family_id,
        'created_at': p.created_at.isoformat()
    } for p in persons]
    
    distributions_data = [{
        'id': d.id,
        'family_id': d.family_id,
        'person_id': d.person_id,
        'package_type': d.package_type,
        'distribution_date': d.distribution_date.isoformat(),
        'notes': d.notes
    } for d in distributions]
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Write data to JSON files
    with open('data/families.json', 'w') as f:
        json.dump(families_data, f, indent=2)
    
    with open('data/persons.json', 'w') as f:
        json.dump(persons_data, f, indent=2)
    
    with open('data/distributions.json', 'w') as f:
        json.dump(distributions_data, f, indent=2)
    
    flash('Data exported successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/import_data')
def import_data():
    # Import data from JSON files
    try:
        # Read families data
        with open('data/families.json', 'r') as f:
            families_data = json.load(f)
        
        # Read persons data
        with open('data/persons.json', 'r') as f:
            persons_data = json.load(f)
        
        # Read distributions data
        with open('data/distributions.json', 'r') as f:
            distributions_data = json.load(f)
        
        # Clear existing data
        Distribution.query.delete()
        Person.query.delete()
        Family.query.delete()
        
        # Import families
        for f_data in families_data:
            family = Family(
                id=f_data['id'],
                family_name=f_data['family_name'],
                address=f_data['address'],
                contact_number=f_data['contact_number'],
                created_at=datetime.fromisoformat(f_data['created_at'])
            )
            db.session.add(family)
        
        # Import persons
        for p_data in persons_data:
            person = Person(
                id=p_data['id'],
                first_name=p_data['first_name'],
                last_name=p_data['last_name'],
                date_of_birth=datetime.fromisoformat(p_data['date_of_birth']),
                fingerprint_id=p_data['fingerprint_id'],
                family_id=p_data['family_id'],
                created_at=datetime.fromisoformat(p_data['created_at'])
            )
            db.session.add(person)
        
        # Import distributions
        for d_data in distributions_data:
            distribution = Distribution(
                id=d_data['id'],
                family_id=d_data['family_id'],
                person_id=d_data['person_id'],
                package_type=d_data['package_type'],
                distribution_date=datetime.fromisoformat(d_data['distribution_date']),
                notes=d_data['notes']
            )
            db.session.add(distribution)
        
        db.session.commit()
        flash('Data imported successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing data: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
