#ifndef EVENT_H
#define EVENT_H

#include <QtCore>
#include <Box2D.h>

class Naubino;

class Event
{
public:
    Event(Naubino *naubino);
    Naubino *naubino;
    virtual bool filter(b2Contact *contact, const b2ContactImpulse *impulse);
    virtual void handle();
};

#endif // EVENT_H
