#ifndef NAUB_H
#define NAUB_H


#include "Prereqs.h"

#include <QMap>

#include <Box2D/Box2D.h>

#include "Color.h"
#include "Vec.h"

class CenterJoint;
class NaubJoint;
class QNaub;
class PointerJoint;

class Pointer;


class Naub {
public:
    Naub(b2World *world);
    ~Naub();

    void update();

    void setPos(const Vec& pos);
    void setColor(const Color& color);

    b2World& world();
    const b2World& world() const;

    Vec pos() const;
    float rot() const;
    float radius() const;
    const Color& color() const;
    b2Body& body();
    const b2Body& body() const;

    void setQNaub(QNaub*);

    CenterJoint *centerJoint();
    void setCenterJoint(CenterJoint *);


    QMap<Naub *, NaubJoint *>& jointNaubs();
    QMap<Pointer *, PointerJoint *>& pointerJoints();

private:
    void setupPhysics();

    b2World *_world;
    b2Body *_body;
    float _radius, _friction, _density, _restitution;
    Color _color;

    QNaub *_qnaub;

    CenterJoint *_centerJoint;

    QMap<Naub *, NaubJoint *> _jointNaubs;
    QMap<Pointer *, PointerJoint *> _pointersJoints;
};


#endif // NAUB_H

