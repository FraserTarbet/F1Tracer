# F1 Tracer

![](assets/BelgiumDemo.mp4)

This is a simple project, animating F1 telemetry data. Data is sourced from the database created as part of the [F1Dash](https://github.com/FraserTarbet/F1Dash) project.

Animation is accomplished using [pyglet](https://pyglet.readthedocs.io/en/latest/index.html).

The source telemetry data is of a fairly low sample frequency and also contains a lot of jitter. Therefore this is more of an abstract visual project than it is a technical/analytical one.

Currently I have functions in place to animate given laps for any session so far this year, and I intend to experiment with additional animations such as overtake compilations.