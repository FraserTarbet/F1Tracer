# F1 Tracer

This is a simple project, animating F1 telemetry data. Data is sourced from the database created as part of the [F1Dash](https://github.com/FraserTarbet/F1Dash) project.

https://user-images.githubusercontent.com/102040556/188687881-620fdfc6-dd58-48df-a76c-c6a9019186d0.mp4

Animation is accomplished using [pyglet](https://pyglet.readthedocs.io/en/latest/index.html).

The source telemetry data is of a fairly low sample frequency and also contains a lot of jitter. Therefore this is more of an abstract visual project than it is a technical/analytical one.

Currently I have functions in place to animate given laps for any session so far this year, and I intend to experiment with additional animations such as overtake compilations.
