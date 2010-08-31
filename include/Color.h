#ifndef COLOR_H
#define COLOR_H


#include "Prereqs.h"

#include <QColor>


class Color {
public:
    Color();
    Color(int r, int g, int b, QString name);

    const QString& readableName() const;
    const QColor& qcolor() const;

    static const QMap<QString, Color>& naubinoColors();
    static const QList<Color>& possibleNaubColors();

    static Color randomNaub();

protected:
    QString name_;
    QColor qcolor_;
};


#endif // COLOR_H

