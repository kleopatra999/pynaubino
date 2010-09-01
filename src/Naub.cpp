#include "Naub.h"

#include "QNaub.h"


Naub::Naub(b2World *world) : _world(world) {
    _centerJoint = 0;
    _qnaub = 0;

    _color = Color::randomNaub();

    setupPhysics();
}


Naub::~Naub() {
    _centerJoint = 0;
    _world = 0;
    _qnaub = 0;
}


void Naub::update() {
    if (_qnaub != 0) {
        _qnaub->naubChanged();
    }
}


void Naub::setupPhysics() {
    _radius = 0.15f;
    _friction = 0;
    _density = 1;
    _restitution = 0.4f;

    b2BodyDef def;
    def.type = b2_dynamicBody;
    b2Body *body = world().CreateBody(&def);
    body->SetUserData(this);
    b2CircleShape shape;
    shape.m_radius = _radius;
    b2FixtureDef fixtureDef;
    fixtureDef.shape = &shape;
    fixtureDef.friction = _friction;
    fixtureDef.restitution = _restitution;
    fixtureDef.density = _density;
    b2Fixture *fix = body->CreateFixture(&fixtureDef);
    fix->SetUserData(this);

    _body = body;
}


void Naub::setPos(const Vec& pos) { _body->SetTransform(pos, rot()); }
void Naub::setColor(const Color& color) { _color = color; }


b2World& Naub::world() { return *_world; }
const b2World& Naub::world() const { return *_world; }
Vec Naub::pos() const { return Vec(_body->GetWorldCenter()); }
float Naub::rot() const { return _body->GetAngle(); }
float Naub::radius() const { return _radius; }
const Color& Naub::color() const { return _color; }
b2Body& Naub::body() { return *_body; }
const b2Body& Naub::body() const { return *_body; }
void Naub::setQNaub(QNaub *n) { _qnaub = n; }
CenterJoint *Naub::centerJoint() { return _centerJoint; }
void Naub::setCenterJoint(CenterJoint *j) { _centerJoint = j; }
QMap<Naub *, NaubJoint *>& Naub::jointNaubs() { return _jointNaubs; }
QMap<Pointer *, PointerJoint *>& Naub::pointerJoints() { return _pointersJoints; }

