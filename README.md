[pyramid_raven][] integrates the [raven python client][] and [raven-js][] with
a [Pyramid][] web application. It provides a configured [raven client][] at
`request.raven` and a [pyramid_layout][] panel called `raven-js`.

Raven has [built in support for Pyramid applications][] via a Paste filter and
logging handler. [pyramid_raven][] is an alternative integration, useful when:

1. you handle exceptions within your application -- i.e.: you register a catch
   all `Exception` view that renders an error page within your application, thus
   preventing errors reaching the WSGI pipeline
1. you also want to log javascript errors

## Setup

Install using [pip][]:

    pip install pyramid_raven

Configure Raven DSN address in the INI configuration of your application:

    raven.dsn = https://xxx:yyy@sentry.example.com/1

... or provide a [SENTRY_DSN environment variable][]:

    SENTRY_DSN=http://public:secret@example.com/1

[Configure your application][] to include the package:

    config.include('pyramid_raven')

## Configure

Any `raven.*` namespaced settings in your `.ini` [configuration file][] will
be passed to the [raven client][] constructor -- although it's your
responsibility to coerce them to the right type, e.g.:

    raven.timeout=3

You can augment the (already fairly comprehensive set of) request attributes
sent with the logged server side exceptions by adding space seperated request
property or method names (called with no args) to:

    pyramid_raven.additional_request_properties=foo bar
    pyramid_raven.additional_request_methods=baz bam

You can also override the panel template:

    pyramid_raven.panel_tmpl=mypkg:templates/foo.tmpl

## Use

You can use it to record server side errors:

    @view_config(context=Exception)
    def system_error_view(context, request):
        """Example catch all exception handler."""
        
        # Notify sentry.
        request.raven.captureException()
        
        # XXX E.g.: render error page.
        # ...

### Client side JavaScript errors

Client side error tracking requires that you have
[pyramid_layout](http://pyramid-layout.readthedocs.org/)
configured before `pyramid_raven`.

And client side errors:

    <!-- in production, in the head of your main layout, above all other js -->
    ${panel('raven-js')}

E.g.: then in any of your subsequently loaded scripts:

    throw new Error('This javascript error will be logged.')

Note that if you load your scripts from an external domain (e.g.: from a CDN)
then errors will not be logged by many browsers, due to cross origin security
(not leaking information across domains). You can workaround this [using CORS][]
but browser support is, at the time of writing, wobbly to say the least.

## Tests

To run the tests, `pip install nose coverage mock` and e.g.:

    $ nosetests --with-doctest --with-coverage --cover-tests --cover-package pyramid_raven pyramid_raven
    ......
    Name                      Stmts   Miss  Cover   Missing
    -------------------------------------------------------
    pyramid_raven                 9      0   100%   
    pyramid_raven.client         69      0   100%   
    pyramid_raven.constants       5      0   100%   
    pyramid_raven.panel          39      0   100%   
    -------------------------------------------------------
    TOTAL                       122      0   100%   
    ----------------------------------------------------------------------
    Ran 6 tests in 0.143s
    
    OK

[built in support for Pyramid applications]: http://raven.readthedocs.org/en/latest/config/pyramid.html
[configuration file]: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/paste.html
[configure your application]: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/configuration.html
[pip]: http://www.pip-installer.org
[pyramid]: http://pyramid.readthedocs.org
[pyramid_layout]: http://pyramid_layout.readthedocs.org/en/latest/
[pyramid_raven]: https://github.com/thruflo/pyramid_raven
[raven client]: http://raven.readthedocs.org/en/latest/usage.html#raven.base.Client
[raven python client]: http://raven.readthedocs.org/en/latest
[raven-js]: http://raven-js.readthedocs.org/en/latest
[sentry_dsn environment variable]: http://raven.readthedocs.org/en/latest/config/index.html#the-sentry-dsn
[using cors]: http://enable-cors.org/
