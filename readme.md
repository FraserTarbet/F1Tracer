# F1 Tracer

This is a simple project, animating F1 telemetry data. Data is sourced from the database created as part of the [F1Dash](https://github.com/FraserTarbet/F1Dash) project, which is originally gathered via [FastF1](https://github.com/theOehrly/Fast-F1). Animation is accomplished using [pyglet](https://pyglet.readthedocs.io/en/latest/index.html).

https://user-images.githubusercontent.com/102040556/189519518-738d4848-3c03-441e-b056-6cd0a63c909a.mp4

The source telemetry data is of a fairly low sample frequency and also contains a lot of noise, jitter and drops. Animating traces that directly follow the source signal results in a very messy and confusing visual. To tackle this, my approach has been the following:
- Synthesize points to fill significant drops in the raw signal using cubic interpolation.
- Create a duplicate signal for every trace and heavily filter it in order to smooth out much of the erratic behaviour.
- Display two traces for each driver:
    - A trace for the interpolated raw signal, which follows the racing line as close as is possible with the source's low sample rate, but which jumps back and forth on this line quite erratically.
    - A trace following the heavily smoothed signal, which behaves much less erratically but which also does not accurately follow the racing line (as a result of the applied filtering).
- The intention is that, between these two traces, it's possible to compare drivers' relative positions to one another, while also following what track features the drivers are navigating at the time.

Currently I have functions in place to animate full laps for a given session, and I intend to experiment with additional animations such as overtake compilations.
