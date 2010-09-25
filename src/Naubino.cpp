    #include "Naubino.h"
#include <Simulator.h>
#include <Naub.h>
#include <NaubJoint.h>
#include <Box2D/Dynamics/b2World.h>
#include <Box2D/Dynamics/b2Body.h>

Naubino::Naubino(QObject *parent) : QObject(parent) {
    sim = new Simulator(this);
    sim->start(50);
    connect(sim,
            SIGNAL(naubOnNaub(Naub*,Naub*)),
            SIGNAL(naubOnNaub(Naub*,Naub*)));

    b2BodyDef def;
    def.type = b2_kinematicBody;
    def.position = Vec();
    center = world().CreateBody(&def);
}

b2World& Naubino::world() const {
    return sim->world();
}

void Naubino::add(Joint *joint) {
    connect(joint,
            SIGNAL(removed(Joint*)),
            SLOT(remove(Joint*)));
    emit added(joint);
}

void Naubino::add(Naub *naub) {
    naub->setNaubino(*this);
    connect(naub,
            SIGNAL(removed(Naub*)),
            SLOT(remove(Naub*)));
    connect(naub,
            SIGNAL(added(Joint*)),
            SLOT(add(Joint*)));
    naub->connect(this,
                  SIGNAL(naubOnNaub(Naub*,Naub*)),
                  SLOT(touch(Naub*,Naub*)));
    emit added(naub);
}

void Naubino::remove(Naub *obj) {
    obj->deleteLater();
}

void Naubino::remove(Joint *obj) {
    obj->deleteLater();
}