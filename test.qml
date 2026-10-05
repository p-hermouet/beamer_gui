import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: appWin
    visible: true
    width: 600
    height: 500
    title: "TestApp"

    Text {
        anchors.centerIn: parent
        text: "Hello World"
        font.pixelSize: 24
    }

}
